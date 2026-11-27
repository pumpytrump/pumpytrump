"""Prepare an ElevenLabs take: speed to fit, transcribe, and align word times onto the Piper token index space
so the existing animation timings (T[i]) keep working.  usage: python3 prep_el.py snocks [target_seconds]"""
import json, subprocess, sys, re, difflib, os
import numpy as np
from faster_whisper import WhisperModel
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
name = sys.argv[1]; target = float(sys.argv[2]) if len(sys.argv) > 2 else 16.2
src = os.path.join(A, name + "_el.mp3"); dst = os.path.join(A, name + "_el.wav")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
# trim leading/trailing silence, then speed up (pitch kept) only if needed
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af",
                "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=stop_periods=-1:stop_duration=0.22:stop_threshold=-45dB:stop_silence=0.14",
                "-ar", "44100", "-ac", "1", dst + ".tmp.wav"], check=True)
d2 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst + ".tmp.wav"], capture_output=True, text=True).stdout)
speed = min(max(d2 / target, 1.0), 1.2)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", dst + ".tmp.wav", "-af", f"atempo={speed:.4f}", dst], check=True)
os.remove(dst + ".tmp.wav")
a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", dst, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, dtype=np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="de", word_timestamps=True)
new = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
ref = json.load(open(os.path.join(A, "words_piper.json")))[name]
norm = lambda s: re.sub(r"[^a-zäöüß0-9]", "", s.lower())
# character-level alignment is robust to different word splits ("Snoxboxer" vs "SNOCKS Boxershorts")
def chars(ws):
    out = []
    for i, (w, s, e) in enumerate(ws):
        n = norm(w) or "_"
        for k, c in enumerate(n): out.append((c, i, s + (e - s) * k / len(n)))
    return out
rc, nc = chars(ref), chars(new)
sm = difflib.SequenceMatcher(None, "".join(c for c, _, _ in rc), "".join(c for c, _, _ in nc), autojunk=False)
tmap = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size): tmap.setdefault(rc[blk.a + k][1], nc[blk.b + k][2])
total = len(a) / 16000
out, last = [], 0.0
known = sorted(tmap.items())
for i, (w, s, e) in enumerate(ref):
    if i in tmap: t = tmap[i]
    else:  # interpolate between neighbours
        prev = max([(j, v) for j, v in known if j < i], default=(-1, 0.0)); nxt = min([(j, v) for j, v in known if j > i], default=(len(ref), total))
        t = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / (nxt[0] - prev[0])
    t = max(t, last); last = t; out.append([w, round(t, 2), 0])
for i in range(len(out)): out[i][2] = round(min(out[i + 1][1] if i + 1 < len(out) else total, out[i][1] + 0.6), 2)
wj = json.load(open(os.path.join(A, "words.json"))); wj[name + "_el"] = out
json.dump(wj, open(os.path.join(A, "words.json"), "w"), ensure_ascii=False)
print(f"{name}: raw {dur:.2f}s -> trimmed {d2:.2f}s -> x{speed:.3f} = {total:.2f}s; matched {len(tmap)}/{len(ref)} words")
print("heard:", " ".join(w for w, _, _ in new))
