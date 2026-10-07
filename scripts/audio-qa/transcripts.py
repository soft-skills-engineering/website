"""Transcribe the same clips from an original episode and its normalized copy, and
compare the transcripts. Judging them (pass/fail) is left to judge.py.

Which clips?
  full_clips(): the whole episode, as back-to-back clips
  sample_clips(): a given number of clips spread evenly through the episode, e.g. 3 clips
  centred 1/6, 1/2 and 5/6 of the way in

How is it kept fair?
  Both versions of a clip are cut at the same moment (corrected for the time offset
  measure.py found) and transcribed with deterministic settings (greedy decoding,
  temperature 0, no context carried between clips), so differences come from the audio
  alone.

Uses faster-whisper from requirements.txt. The first run downloads the transcription
model (~500 MB) into ./models."""

import os
import re
import subprocess

import numpy as np

from common import timestamp, window_correlations

MODEL = 'small.en'
CLIP_SECONDS = 60  # Of each clip in full_clips()
WHISPER_RATE = 16000
EDGE_WORDS = 3  # Words at each end of a clip may be cut off differently, so ignore them
FILLERS = {'um', 'umm', 'uh', 'uhm', 'hmm', 'mm', 'mhm', 'ah', 'er', 'oh'}

here = os.path.dirname(os.path.abspath(__file__))


def load_model():
    from faster_whisper import WhisperModel
    return WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 1,
                        download_root=os.path.join(here, 'models'))


def clip(path, start, seconds):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{max(0, start):.3f}', '-t', str(seconds),
           '-i', path, '-map', '0:a:0', '-ac', '1', '-ar', str(WHISPER_RATE), '-f', 'f32le', '-']
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f'ffmpeg failed to cut a clip from {path}:\n{result.stderr.decode(errors="replace")[-2000:]}')
    return np.frombuffer(result.stdout, '<f4')


def transcribe(model, audio):
    segments, _ = model.transcribe(audio, language='en', beam_size=1, temperature=0.0,
                                   condition_on_previous_text=False, vad_filter=False,
                                   without_timestamps=True)
    return ' '.join(s.text.strip() for s in segments)


def words(text):
    found = [w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in FILLERS]
    return found[EDGE_WORDS:-EDGE_WORDS] if len(found) > 2 * EDGE_WORDS else []


def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, row[0] = row[0], i
        for j, y in enumerate(b, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (x != y))
    return row[-1]


def full_clips(duration):
    """(start, seconds) of back-to-back clips covering the whole episode. A short
    leftover at the end joins the clip before it."""
    count = max(1, round(duration / CLIP_SECONDS))
    return [(i * CLIP_SECONDS, CLIP_SECONDS if i < count - 1 else duration - i * CLIP_SECONDS)
            for i in range(count)]


def sample_clips(duration, count, seconds):
    """(start, seconds) of `count` clips spread evenly through the episode"""
    seconds = min(seconds, duration / count)
    return [(duration * (i + 0.5) / count - seconds / 2, seconds) for i in range(count)]


def compare_transcripts(original_path, normalized_path, clips_to_check, lag_seconds):
    """Both transcripts of each (start, seconds) clip, and their word error rate (the
    fraction of words that differ)"""
    model = load_model()
    clips = []
    for number, (start, seconds) in enumerate(clips_to_check, 1):
        print(f'Transcribing clip {number}/{len(clips_to_check)} ({timestamp(start)}) from both versions',
              flush=True)
        audio_a = clip(original_path, start, seconds)
        audio_b = clip(normalized_path, start + lag_seconds, seconds)
        original, normalized = transcribe(model, audio_a), transcribe(model, audio_b)
        # Whisper sometimes skips a sentence over tiny audio differences, so also record
        # whether the waveforms themselves match here
        r, active, _ = window_correlations(audio_a, audio_b, WHISPER_RATE)
        a, b = words(original), words(normalized)
        clips.append({
            'start': round(start, 1),
            'seconds': round(seconds, 1),
            'original': original,
            'normalized': normalized,
            'words': len(a),
            'wer': round(edit_distance(a, b) / len(a), 4) if a else (0.0 if not b else 1.0),
            'waveform_r_min': round(float(r[active].min()), 4) if active.any() else None,
        })
    return {'model': MODEL, 'clips': clips}
