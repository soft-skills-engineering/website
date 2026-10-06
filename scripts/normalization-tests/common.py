"""Helpers shared by the normalization test scripts."""

import json
import os
import re

import numpy as np

# Sample rate the content comparisons run at. Speech is intelligible well below 4 kHz.
PCM_RATE = 8000

# Must match normalize-audio-volume, so originals are compared like for like
HIGHPASS = 'highpass=f=70'

# Chromaprint's hop between fingerprint items (4096/3 samples at its internal 11025 Hz)
FP_ITEM_SECONDS = 4096 / 3 / 11025


def window_correlations(a, b, rate):
    """Compare aligned audio second by second. Returns each second's correlation (1.0 =
    same waveform, whatever the volume), whether it's loud enough in `a` to judge (quiet
    seconds only correlate noise), and its gain change in dB.

    Windows are short so the gain is near-constant within each one: matching audio scores
    ~1.0, peak limiting dips it a little, and missing or garbled audio drops it toward 0."""
    count = min(len(a), len(b)) // rate
    A = a[:count * rate].reshape(count, rate).astype(np.float64)
    B = b[:count * rate].reshape(count, rate).astype(np.float64)
    A -= A.mean(axis=1, keepdims=True)
    B -= B.mean(axis=1, keepdims=True)
    power_a = (A * A).mean(axis=1)
    power_b = (B * B).mean(axis=1)
    level_a = 10 * np.log10(power_a + 1e-12)
    active = level_a > np.percentile(level_a, 90) - 30
    r = (A * B).mean(axis=1) / np.sqrt(power_a * power_b + 1e-24)
    gain = 10 * np.log10((power_b + 1e-12) / (power_a + 1e-12))
    return r, active, gain


def natural_key(name):
    """Sort sse-2.mp3 before sse-10.mp3"""
    return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', name)]


def write_json(path, data):
    """Write atomically, so an interrupted run never leaves a half-written result"""
    tmp = path + '.part'
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def read_json(path):
    with open(path) as f:
        return json.load(f)


def read_results(directory):
    """All result files in a directory, keyed by episode file name"""
    if not os.path.isdir(directory):
        return {}
    return {name[:-len('.json')]: read_json(os.path.join(directory, name))
            for name in os.listdir(directory) if name.endswith('.json')}


def timestamp(seconds):
    seconds = max(0, int(seconds))
    return f'{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}'
