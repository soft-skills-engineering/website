"""Measurements comparing an original episode with its normalized copy. Judging them
(pass/fail) is left to judge.py, so thresholds can be tuned without re-measuring.

What does it measure?
  Structural:
    - Duration of the decoded audio of each file
    - Decoder errors/warnings in each file
    - Whether the ID3v2 and ID3v1 tags were preserved byte-for-byte
  Loudness: integrated loudness, loudness range and true peak of each file (EBU R128)
  Content (normalization changes every sample's level, so these ignore gain):
    - Chromaprint fingerprint similarity, overall and per 30-second chunk
    - Waveform cross-correlation: the time offset between the files, then the
      correlation of each 1-second window, which pinpoints where content differs.
      Windows are short so the gain is near-constant within each one: matching audio
      scores ~1.0, peak limiting dips it a little, and missing or garbled audio
      drops it toward 0.
    - Silence map: whether the pauses in speech line up in both files

Each file is decoded once, by one ffmpeg run that feeds all of its analyses."""

import os
import re
import subprocess
import tempfile

import numpy as np

from common import FP_ITEM_SECONDS, HIGHPASS, PCM_RATE, window_correlations

FP_CHUNK_SECONDS = 30         # Fingerprint similarity chunk
MAX_LAG_SECONDS = 1           # Largest time offset searched between the files
SILENCE_FRAME_SECONDS = 0.05
SILENCE_BELOW_PEAK_DB = 35    # How far below the loud speech level counts as silence
SILENCE_MIN_SECONDS = 0.6


def analyze(path, highpass, workdir):
    """Decode a file once and return its loudness stats, fingerprint, 8 kHz mono audio
    and decoder complaints"""
    fp_path = os.path.join(workdir, 'fp')
    pcm_path = os.path.join(workdir, 'pcm')
    pre = [HIGHPASS] if highpass else []
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-loglevel', 'level+info', '-y',
           '-i', path,
           '-map', '0:a:0', '-af', 'ebur128=framelog=quiet:peak=true', '-f', 'null', '-',
           '-map', '0:a:0', '-af', ','.join(pre + ['anull']),
           '-f', 'chromaprint', '-fp_format', 'raw', fp_path,
           '-map', '0:a:0', '-af', ','.join(pre + ['anull']), '-ac', '1', '-ar', str(PCM_RATE),
           '-f', 'f32le', pcm_path]
    result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    if result.returncode != 0:
        raise RuntimeError(f'ffmpeg failed on {path}:\n{result.stderr[-2000:]}')
    log = result.stderr

    def stat(label):
        found = re.findall(rf'^\s*{label}:\s*(-?[\d.]+|-inf)', log, re.M)
        return float(found[-1]) if found else None

    complaints = [line for line in log.splitlines()
                  if re.search(r'\[(error|warning|fatal)\]', line) and 'ebur128' not in line]
    pcm = np.fromfile(pcm_path, dtype='<f4')
    fp = np.fromfile(fp_path, dtype='<u4')
    os.remove(pcm_path)
    return {
        'loudness_i': stat('I'),
        'lra': stat('LRA'),
        'true_peak': stat('Peak'),
        'decode_complaints': complaints[:20],
        'decode_complaint_count': len(complaints),
    }, fp, pcm


def id3v2_size(data):
    """Size in bytes of the ID3v2 tag(s) at the start of a file (same logic as
    normalize-audio-volume)"""
    total = 0
    while data[total:total + 3] == b'ID3' and len(data) >= total + 10:
        h = data[total:total + 10]
        size = (h[6] << 21) | (h[7] << 14) | (h[8] << 7) | h[9]
        if h[5] & 0x10:
            size += 10  # Footer present
        total += 10 + size
    return total


def check_tags(original_path, normalized_path):
    with open(original_path, 'rb') as f:
        original = f.read()
    with open(normalized_path, 'rb') as f:
        normalized = f.read()
    size = id3v2_size(original)
    original_v1 = original[-128:] if original[-128:-125] == b'TAG' else None
    normalized_v1 = normalized[-128:] if normalized[-128:-125] == b'TAG' else None
    return {
        'id3v2_bytes': size,
        'id3v2_identical': id3v2_size(normalized) == size and normalized[:size] == original[:size],
        'id3v1_present': original_v1 is not None,
        'id3v1_identical': original_v1 == normalized_v1,
    }


def find_lag(a, b):
    """How many samples later content appears in b than in a. Cross-correlates 30-second
    excerpts from three points in the episode and takes the median."""
    max_lag = MAX_LAG_SECONDS * PCM_RATE
    n = 30 * PCM_RATE
    lags = []
    for fraction in (0.25, 0.5, 0.75):
        start = int(len(a) * fraction)
        excerpt = a[start:start + n]
        region_start = max(0, start - max_lag)
        region = b[region_start:start + n + max_lag]
        if len(excerpt) < n or len(region) <= n or not excerpt.any():
            continue
        size = 1 << (len(region) + n).bit_length()
        corr = np.fft.irfft(np.fft.rfft(region, size) * np.conj(np.fft.rfft(excerpt, size)), size)
        lags.append(region_start + int(np.argmax(corr[:len(region) - n + 1])) - start)
    return int(np.median(lags)) if lags else 0


def align(a, b, lag):
    a = a[max(0, -lag):]
    b = b[max(0, lag):]
    n = min(len(a), len(b))
    return a[:n], b[:n]


def compare_windows(a, b):
    """Correlation and gain change of each 1-second window of aligned audio"""
    r, active, gain = window_correlations(a, b, PCM_RATE)
    r_active = r[active]
    order = np.argsort(np.where(active, r, np.inf))
    worst = [{'at': float(i), 'r': round(float(r[i]), 4)} for i in order[:5] if active[i]]
    return {
        'windows': len(r),
        'windows_compared': int(active.sum()),
        'r_min': round(float(r_active.min()), 4),
        'r_p1': round(float(np.percentile(r_active, 1)), 4),
        'r_median': round(float(np.median(r_active)), 4),
        'windows_below_0_9': int((r_active < 0.9).sum()),
        'windows_below_0_5': int((r_active < 0.5).sum()),
        'worst_windows': worst,
        'mismatch_regions': mismatch_regions(r, active)[:20],
        'gain_db_median': round(float(np.median(gain[active])), 2),
        'gain_db_min': round(float(gain[active].min()), 2),
        'gain_db_max': round(float(gain[active].max()), 2),
        'gain_db_std': round(float(gain[active].std()), 2),
    }


def mismatch_regions(r, active):
    """Stretches of seconds that don't match (correlation below 0.5), as [start, end]
    seconds, longest first. Gaps of up to 2 seconds are bridged."""
    bad = np.flatnonzero(active & (r < 0.5))
    regions = []
    for second in bad:
        if regions and second - regions[-1][1] <= 2:
            regions[-1][1] = int(second) + 1
        else:
            regions.append([int(second), int(second) + 1])
    return sorted(regions, key=lambda region: region[0] - region[1])


def silences(x):
    """Pauses in speech, as (start, end) seconds. The threshold is relative to each file's
    own speech level, so it doesn't matter that one file is louder than the other."""
    frame = int(SILENCE_FRAME_SECONDS * PCM_RATE)
    count = len(x) // frame
    frames = x[:count * frame].reshape(count, frame).astype(np.float64)
    level = 10 * np.log10((frames * frames).mean(axis=1) + 1e-12)
    silent = level < np.percentile(level, 95) - SILENCE_BELOW_PEAK_DB
    edges = np.diff(np.concatenate(([0], silent.astype(np.int8), [0])))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    keep = (ends - starts) * SILENCE_FRAME_SECONDS >= SILENCE_MIN_SECONDS
    return np.stack([starts[keep], ends[keep]], axis=1) * SILENCE_FRAME_SECONDS


def matched(these, those):
    """Which intervals in `these` overlap some interval in `those`"""
    if len(these) == 0 or len(those) == 0:
        return np.zeros(len(these), dtype=bool)
    # The last interval of `those` starting before each interval of `these` ends
    i = np.searchsorted(those[:, 0], these[:, 1]) - 1
    return (i >= 0) & (those[np.maximum(i, 0), 1] > these[:, 0])


def compare_silences(a, b):
    sa, sb = silences(a), silences(b)
    ma, mb = matched(sa, sb), matched(sb, sa)
    unmatched = [float(s) for s in sa[~ma][:3, 0]] + [float(s) for s in sb[~mb][:3, 0]]
    return {
        'silences_original': len(sa),
        'silences_normalized': len(sb),
        # Fraction of pauses found in both, checked in each direction; the worse one
        'match': round(float(min(ma.mean() if len(sa) else 1, mb.mean() if len(sb) else 1)), 4),
        'unmatched_at': sorted(unmatched)[:5],
    }


def compare_fingerprints(a, b):
    """Bitwise similarity of two Chromaprint fingerprints (1.0 = identical, ~0.5 = unrelated)"""
    best = None
    for lag in range(-8, 9):
        x, y = align(a, b, lag)
        if len(x) == 0:
            continue
        sim = 1 - np.bitwise_count(x ^ y).astype(np.float64) / 32
        if best is None or sim.mean() > best[1].mean():
            best = (lag, sim)
    if best is None:
        return {'similarity': 0.0}
    lag, sim = best
    chunk = int(FP_CHUNK_SECONDS / FP_ITEM_SECONDS)
    count = max(1, len(sim) // chunk)
    chunks = [sim[i * chunk:(i + 1) * chunk].mean() for i in range(count)]
    worst = int(np.argmin(chunks))
    return {
        'similarity': round(float(sim.mean()), 4),
        'chunk_min': round(float(chunks[worst]), 4),
        'chunk_min_at': round(worst * chunk * FP_ITEM_SECONDS + max(0, -lag) * FP_ITEM_SECONDS, 1),
        'lag_items': lag,
    }


def measure_pair(original_path, normalized_path):
    """Every measurement comparing the two files"""
    with tempfile.TemporaryDirectory(prefix='check-pair.') as workdir:
        stats_a, fp_a, pcm_a = analyze(original_path, True, workdir)
        stats_b, fp_b, pcm_b = analyze(normalized_path, False, workdir)

    lag = find_lag(pcm_a, pcm_b)
    a, b = align(pcm_a, pcm_b, lag)
    return {
        'episode': os.path.basename(normalized_path),
        'original': {**stats_a, 'duration': round(len(pcm_a) / PCM_RATE, 3)},
        'normalized': {**stats_b, 'duration': round(len(pcm_b) / PCM_RATE, 3)},
        'tags': check_tags(original_path, normalized_path),
        'lag_seconds': round(lag / PCM_RATE, 4),
        'fingerprint': compare_fingerprints(fp_a, fp_b),
        'xcorr': compare_windows(a, b),
        'silence': compare_silences(a, b),
    }
