#!/usr/bin/env python3
"""Tighten an ElevenLabs take and get word timestamps.
python3 prep_voice.py <project_dir> <target_seconds> [max_pause]
-> assets/voice.wav, assets/words.json  ([[word, start, end], ...])"""
import json, os, subprocess, sys
import numpy as np

d = sys.argv[1]; target = float(sys.argv[2]); pause = float(sys.argv[3]) if len(sys.argv) > 3 else 0.16
A = os.path.join(d, "assets"); raw = os.path.join(A, "voice_raw.mp3"); tight = os.path.join(A, "tight.wav"); out = os.path.join(A, "voice.wav")

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        f"silenceremove=stop_periods=-1:stop_duration={pause + 0.08}:stop_threshold=-45dB:stop_silence={pause}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", trim, "-ar", "44100", "-ac", "1", tight], check=True)
L = dur(tight); tempo = min(max(L / target, 1.0), 1.22)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tight, "-af", f"atempo={tempo:.4f}", "-ar", "44100", "-ac", "1", out], check=True)
print(f"raw {dur(raw):.2f}s  tight {L:.2f}s  tempo {tempo:.3f}  -> {dur(out):.2f}s")

from faster_whisper import WhisperModel
pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", out, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"])
audio = np.frombuffer(pcm, np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="de", word_timestamps=True, beam_size=5)
words = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
json.dump(words, open(os.path.join(A, "words.json"), "w"), ensure_ascii=False)
print(len(words), "words:", " ".join(f"{i}:{w[0]}@{w[1]}" for i, w in enumerate(words)))
