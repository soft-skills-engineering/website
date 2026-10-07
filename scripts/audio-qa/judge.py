"""Pass/fail judgment of the measurements from measure.py (and, when present, the
transcript comparison from transcripts.py)"""

from common import timestamp

TARGET_I = -16

# Any one of these flags an episode for a listen
MAX_DURATION_CHANGE = 0.1     # seconds
MAX_LOUDNESS_MISS = 1.0       # LU away from TARGET_I
MAX_TRUE_PEAK = -0.5          # dBTP (the target is -1.5; MP3 encoding overshoots a little)
MIN_FP_SIMILARITY = 0.90      # Whole-episode fingerprint (unrelated audio scores ~0.5)
MIN_FP_CHUNK = 0.80           # Worst 30-second fingerprint chunk
MIN_XCORR_P1 = 0.80           # 1st percentile of 1-second waveform correlations
MAX_XCORR_DROPOUTS = 0        # 1-second windows correlating below 0.5 (missing/garbled audio)
MIN_SILENCE_MATCH = 0.80      # Fraction of pauses found in both versions
MIN_SILENCES = 10             # ... only judged when there are enough pauses to judge
MAX_WER = 0.10                # Fraction of words that differ in a transcribed clip


def judge(p):
    """Reasons to listen, and where"""
    reasons, listen = [], []
    o, n = p['original'], p['normalized']

    change = n['duration'] - o['duration']
    if abs(change) > MAX_DURATION_CHANGE:
        reasons.append(f'duration changed {change:+.2f}s')
        listen.append(min(o['duration'], n['duration']) - 10)
    if n['decode_complaint_count'] > o['decode_complaint_count']:
        reasons.append(f"{n['decode_complaint_count']} decoder errors (original: {o['decode_complaint_count']})")
    if not p['tags']['id3v2_identical']:
        reasons.append('ID3v2 tag changed')
    if not p['tags']['id3v1_identical']:
        reasons.append('ID3v1 tag changed')

    if n['loudness_i'] is None or abs(n['loudness_i'] - TARGET_I) > MAX_LOUDNESS_MISS:
        reasons.append(f"loudness {n['loudness_i']} LUFS")
    if n['true_peak'] is None or n['true_peak'] > MAX_TRUE_PEAK:
        reasons.append(f"true peak {n['true_peak']} dBTP")

    fp = p['fingerprint']
    if fp['similarity'] < MIN_FP_SIMILARITY:
        reasons.append(f"fingerprint similarity {fp['similarity']:.3f}")
    if fp.get('chunk_min', 1) < MIN_FP_CHUNK:
        reasons.append(f"fingerprint chunk {fp['chunk_min']:.3f} at {timestamp(fp['chunk_min_at'])}")
        listen.append(fp['chunk_min_at'])

    x = p['xcorr']
    if x['windows_below_0_5'] > MAX_XCORR_DROPOUTS or x['r_p1'] < MIN_XCORR_P1:
        reasons.append(f"waveform: {x['windows_below_0_5']} seconds don't match, "
                       f"1st percentile r={x['r_p1']:.3f}")
        regions = x.get('mismatch_regions') or [[w['at'], w['at'] + 1] for w in x['worst_windows'][:3]]
        listen += [start for start, _ in regions]

    s = p['silence']
    if max(s['silences_original'], s['silences_normalized']) >= MIN_SILENCES and s['match'] < MIN_SILENCE_MATCH:
        reasons.append(f"pauses: only {s['match']:.0%} line up "
                       f"({s['silences_original']} vs {s['silences_normalized']})")
        listen += s['unmatched_at'][:3]

    t = p.get('transcript')
    if t:
        for c in t['clips']:
            if c['wer'] > MAX_WER and not transcriber_quirk(c):
                reasons.append(f"transcript differs {c['wer']:.0%} in clip at {timestamp(c['start'])}")
                listen.append(c['start'])
    return reasons, sorted(set(round(t) for t in listen))


def transcriber_quirk(c):
    """Whisper sometimes skips or rewords a sentence over tiny audio differences. When
    the waveforms match second by second throughout the clip, that's what happened."""
    return c.get('waveform_r_min') is not None and c['waveform_r_min'] >= 0.5
