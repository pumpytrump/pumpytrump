#!/usr/bin/env python3
"""Build 3 TikTok Shop videos (1080x1920, ~16 s) from product images + ElevenLabs voiceovers.

Usage: python3 build.py            -> renders out/*.mp4
Needs: ffmpeg, Pillow, numpy, assets/*.mp3, assets/*.png, assets/words.json
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "out")
TMP = os.path.join(HERE, ".tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

W, H, FPS = 1080, 1920, 30
TARGET_SPEECH = 16.0      # seconds of voice after tightening
TAIL = 0.8                # CTA hold after the voice -> total ~16.8 s
SR = 44100

FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FXB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FEMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        f = ImageFont.truetype(FEMO, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
        im = im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
        _emo[k] = im
    return _emo[k]

# ----------------------------------------------------------------- audio
def load_pcm(mp3):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

def tighten(pcm, cuts=(), min_sil=0.14, keep_sil=0.10, thr=0.012):
    """Remove explicit cut ranges, shrink every silent run to keep_sil.
    Returns new pcm and a function mapping original time -> new time."""
    n = len(pcm); hop = int(0.01 * SR)
    rms = np.array([np.sqrt(np.mean(pcm[i:i + hop] ** 2)) for i in range(0, n, hop)])
    drop = np.zeros(len(rms), bool)
    for a, b in cuts:
        drop[int(a * 100):int(b * 100)] = True
    silent = rms < thr
    i = 0
    while i < len(rms):
        if silent[i] and not drop[i]:
            j = i
            while j < len(rms) and silent[j] and not drop[j]: j += 1
            if (j - i) / 100 >= min_sil:
                k = int(keep_sil * 100 / 2)
                drop[i + k:j - k] = True
            i = j
        else:
            i += 1
    keep = ~drop
    # never drop the very first/last 3 frames edge fades
    out = np.concatenate([pcm[f * hop:(f + 1) * hop] for f in range(len(rms)) if keep[f]])
    cum = np.concatenate([[0], np.cumsum(keep)]) / 100.0
    def remap(t):
        f = min(max(int(t * 100), 0), len(keep))
        return float(cum[f])
    return out, remap

def stretch_to(pcm, target, name):
    src = os.path.join(TMP, name + "_tight.wav"); dst = os.path.join(TMP, name + "_voice.wav")
    write_wav(src, pcm)
    speed = len(pcm) / SR / target
    speed = min(max(speed, 1.0), 1.25)
    # rubberband keeps pitch & sounds natural; fall back to atempo
    flt = f"atempo={speed:.4f}"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", flt, "-ar", str(SR), dst], check=True)
    return dst, speed

def write_wav(path, pcm):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", path], input=pcm.astype(np.float32).tobytes(), check=True)

def sfx_track(events, dur):
    """events: list of (time, kind). Synthesised pops/whooshes/ding so no licensing issues."""
    n = int(dur * SR); out = np.zeros(n, np.float32)
    rng = np.random.default_rng(1)
    for t, kind in events:
        s = int(t * SR)
        if kind == "pop":
            L = int(0.09 * SR); x = np.arange(L) / SR
            f = 900 * np.exp(-x * 30) + 250
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 45) * 0.35
        elif kind == "whoosh":
            L = int(0.35 * SR); x = np.arange(L) / SR
            noise = rng.standard_normal(L).astype(np.float32)
            k = np.ones(40) / 40; noise = np.convolve(noise, k, "same")
            env = np.sin(np.pi * x / x[-1]) ** 2
            sig = noise * env * 0.5
        elif kind == "ding":
            L = int(0.6 * SR); x = np.arange(L) / SR
            sig = (np.sin(2 * np.pi * 1320 * x) + 0.5 * np.sin(2 * np.pi * 1980 * x)) * np.exp(-x * 7) * 0.18
        elif kind == "boom":
            L = int(0.5 * SR); x = np.arange(L) / SR
            sig = np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 8) * 0.6
        else:
            continue
        e = min(n, s + len(sig)); out[s:e] += sig[:e - s]
    return out

# ----------------------------------------------------------------- drawing helpers
def ease_out_back(t):
    t = min(max(t, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out(t):
    t = min(max(t, 0), 1); return 1 - (1 - t) ** 3

def gradient(c1, c2):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(c1)[None, None, :] * (1 - g) + np.array(c2)[None, None, :] * g)
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")

def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    im = im.convert("RGBA"); im.putalpha(m); return im

def paste_center(canvas, im, cx, cy, scale=1.0, rot=0.0, shadow=True):
    if scale <= 0.01: return
    w, h = im.size
    im2 = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
    if rot: im2 = im2.rotate(rot, Image.BICUBIC, expand=True)
    x, y = int(cx - im2.size[0] / 2), int(cy - im2.size[1] / 2)
    if shadow:
        a = im2.split()[3] if im2.mode == "RGBA" else Image.new("L", im2.size, 255)
        sh = Image.new("RGBA", im2.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: v * 0.45))
        sh = sh.filter(ImageFilter.GaussianBlur(25))
        canvas.paste(sh, (x + 10, y + 30), sh)
    canvas.paste(im2, (x, y), im2 if im2.mode == "RGBA" else None)

def text_block(d, cx, cy, text, size, fill, stroke=(0, 0, 0), sw=10, maxw=980, fnt=FB, anchor_mid=True):
    f = font(fnt, size)
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    if cur: lines.append(cur)
    lh = int(size * 1.08); y0 = cy - lh * len(lines) / 2 + lh / 2
    for i, ln in enumerate(lines):
        d.text((cx, y0 + i * lh), ln, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor="mm")
    return lh * len(lines)

def pill(canvas, cx, cy, text, size, bg, fg=(255, 255, 255), scale=1.0, rot=0, emo=None):
    if scale <= 0.02: return
    f = font(FB, size); d0 = ImageDraw.Draw(canvas)
    tw = d0.textlength(text, font=f); ew = int(size * 1.1) if emo else 0
    pw, ph = int(tw + ew + size * 1.2), int(size * 1.7)
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], ph // 2, fill=bg, outline=(255, 255, 255), width=5)
    x = size * 0.6
    if emo:
        e = emoji(emo, int(size * 1.0)); im.paste(e, (int(x), int((ph - e.size[1]) / 2)), e); x += ew
    d.text((x, ph / 2), text, font=f, fill=fg, anchor="lm")
    paste_center(canvas, im, cx, cy, scale, rot, shadow=True)

def captions(canvas, words, t, y=1430):
    """TikTok-style 1-3 word chunks; active word highlighted and popped."""
    # group into chunks of <=3 words / <=16 chars, break on punctuation
    chunks, cur = [], []
    for i, (w_, s, e) in enumerate(words):
        cur.append(i)
        txt = " ".join(words[j][0] for j in cur)
        if len(cur) >= 3 or len(txt) >= 15 or w_[-1] in ".,!?…" :
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    active = None
    for ch in chunks:
        s = words[ch[0]][1]; e = words[ch[-1]][2] + 0.25
        if s - 0.02 <= t <= e: active = ch
    if active is None: return
    d = ImageDraw.Draw(canvas)
    f = font(FB, 92); gap = 26
    toks = [words[i][0].upper() for i in active]
    widths = [d.textlength(x, font=f) for x in toks]
    total = sum(widths) + gap * (len(toks) - 1)
    if total > 1000:  # shrink to fit
        f = font(FB, int(92 * 1000 / total)); widths = [d.textlength(x, font=f) for x in toks]
        total = sum(widths) + gap * (len(toks) - 1)
    x = (W - total) / 2
    for i, tok, wd in zip(active, toks, widths):
        s, e = words[i][1], words[i][2]
        on = s <= t < max(e, s + 0.12) + 0.08
        col = (255, 226, 50) if on else (255, 255, 255)
        pop = 1 + 0.12 * max(0, 1 - (t - s) / 0.15) if on else 1
        fs = font(f.path, int(f.size * pop))
        d.text((x + wd / 2, y), tok, font=fs, fill=col, stroke_width=11, stroke_fill=(0, 0, 0), anchor="mm")
        x += wd + gap

def progress_bar(d, t, total, col):
    d.rectangle([0, 0, int(W * min(t / total, 1)), 12], fill=col)

def cart_cta(canvas, t, t0, accent):
    """Big pulsing arrow + text pointing to TikTok's product anchor (bottom-left)."""
    k = ease_out_back((t - t0) / 0.35)
    if k <= 0: return
    pulse = 1 + 0.06 * math.sin((t - t0) * 12)
    pill(canvas, W / 2, 1180, "JETZT IM WARENKORB", 64, accent, scale=k * pulse, emo="🛒")
    # arrow
    d = ImageDraw.Draw(canvas)
    bob = 18 * math.sin((t - t0) * 10)
    ax, ay = 230, 1610 + bob
    pts = [(ax, ay + 110), (ax - 90, ay), (ax - 35, ay), (ax - 35, ay - 120), (ax + 35, ay - 120), (ax + 35, ay), (ax + 90, ay)]
    if k > 0.5:
        d.polygon(pts, fill=(255, 226, 50), outline=(0, 0, 0), width=8)
        e = emoji("👇", 110); canvas.paste(e, (W - 250, int(1560 + bob)), e)

# ----------------------------------------------------------------- video specs
def load_img(name, h=None, w=None, rad=0):
    im = Image.open(os.path.join(A, name)).convert("RGBA")
    if h: im = im.resize((int(im.size[0] * h / im.size[1]), h), Image.LANCZOS)
    if w: im = im.resize((w, int(im.size[1] * w / im.size[0])), Image.LANCZOS)
    if rad: im = rounded(im, rad)
    return im

def find(words, token, start=0):
    for i in range(start, len(words)):
        if words[i][0] and words[i][0].lower().strip(".,!?„“-").startswith(token.lower()): return i
    raise KeyError(token)

def render(spec):
    name = spec["name"]
    raw = json.load(open(os.path.join(A, "words.json")))[spec["voice"] + ".mp3"]
    words = [(spec["fix"].get(i, w_), s, e) for i, (w_, s, e) in enumerate(raw)]
    cut_idx = set()
    for a, b in spec.get("cut_words", []):
        cut_idx.update(range(a, b + 1))
    cuts = [(raw[a][1] - 0.05, raw[b + 1][1] - 0.08) for a, b in spec.get("cut_words", [])]
    pcm = load_pcm(os.path.join(A, spec["voice"] + ".mp3"))
    tight, remap = tighten(pcm, cuts)
    voice, speed = stretch_to(tight, TARGET_SPEECH, name)
    vdur = len(tight) / SR / speed
    words = [(w_, remap(s) / speed, remap(e) / speed) for i, (w_, s, e) in enumerate(words) if i not in cut_idx]
    merged = []
    for w_, s, e in words:          # None = glue onto previous word (e.g. split compound nouns)
        if w_ is None: merged[-1] = (merged[-1][0], merged[-1][1], e)
        else: merged.append((w_, s, e))
    words = merged
    total = vdur + TAIL
    print(f"[{name}] voice {len(pcm)/SR:.1f}s -> tight {len(tight)/SR:.1f}s -> x{speed:.3f} = {vdur:.2f}s, video {total:.2f}s")

    T = lambda tok, start=0: words[find(words, tok, start)][1]
    scenes = spec["scenes"](T, total)           # list of (start, fn)
    starts = [s for s, _ in scenes]
    sfx = [(max(0, s - 0.05), k) for s, k in spec["sfx"](T, total)]
    fx = sfx_track(sfx, total + 0.5)
    write_wav(os.path.join(TMP, name + "_sfx.wav"), fx)

    frames = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", voice, "-i", os.path.join(TMP, name + "_sfx.wav"),
                           "-filter_complex",
                           "[1:a]volume=1.0,apad[v];[2:a]volume=0.8[s];[v][s]amix=inputs=2:duration=first:normalize=0,"
                           "loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                           "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
                           os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for fi in range(frames):
        t = fi / FPS
        idx = max(i for i, s in enumerate(starts) if s <= t + 1e-6)
        s0 = starts[idx]
        canvas = scenes[idx][1](t, t - s0).convert("RGBA")
        captions(canvas, words, t)
        d = ImageDraw.Draw(canvas)
        progress_bar(d, t, total, spec["accent"])
        # subtle flash on scene cut
        if 0 < idx and t - s0 < 0.06:
            canvas = Image.blend(canvas, Image.new("RGBA", canvas.size, (255, 255, 255, 255)), 0.35)
        ff.stdin.write(canvas.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    with open(os.path.join(OUT, name + "_captions.txt"), "w") as fh:
        fh.write(spec["post"])
    return total

# ================================================================= HONEY
def honey():
    bg = gradient((122, 18, 30), (38, 6, 12))
    jar = load_img("honey_jar.png", h=900, rad=60)
    jar_s = load_img("honey_jar.png", h=620, rad=50)
    couple = load_img("honey_couple.png", w=W + 200)
    accent = (228, 40, 80)

    def s_hook(t, lt):
        c = bg.copy().convert("RGBA")
        k = ease_out_back(lt / 0.4)
        paste_center(c, jar, W / 2, 870, 0.35 + 0.6 * k, rot=(1 - k) * -14)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 215, "DIESER HONIG RETTET BEZIEHUNGEN", 80, (255, 255, 255), maxw=960)
        pill(c, 830, 380, "LIMITIERT", 44, accent, scale=ease_out_back((lt - 0.6) / 0.3), rot=8, emo="🔥")
        e = emoji("🍯", 150); paste_center(c, e, 170, 1180 + 15 * math.sin(lt * 6), 1, rot=-10, shadow=False)
        e = emoji("❤️", 120); paste_center(c, e, 930, 1100 + 15 * math.sin(lt * 7 + 1), ease_out_back((lt - 0.3) / 0.3), shadow=False)
        return c

    def s_couple(t, lt):
        c = bg.copy().convert("RGBA")
        z = 1.0 + lt * 0.05
        paste_center(c, couple, W / 2 - 60, 820, z * 1.02, shadow=False)
        d = ImageDraw.Draw(c)
        k = ease_out_back((lt - 0.9) / 0.3)
        pill(c, W / 2, 230, "„SCHATZ“ IST ZURÜCK", 62, accent, scale=k, emo="😳")
        return c

    def s_uses(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, jar, W / 2, 800, 0.95 + lt * 0.06, rot=math.sin(lt * 3) * 3)
        pill(c, 290, 330, "AUFS EIS", 56, (200, 120, 30), scale=ease_out_back(lt / 0.3), rot=-6, emo="🍦")
        pill(c, 800, 470, "AUFS BROT", 56, (160, 90, 30), scale=ease_out_back((lt - 0.45) / 0.3), rot=5, emo="🍞")
        pill(c, W / 2, 1200, "ODER PUR...", 60, (90, 20, 30), scale=ease_out_back((lt - 0.9) / 0.3), emo="🤫")
        return c

    def s_deal(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, jar, W / 2, 800, 0.9 + 0.08 * ease_out(lt / 0.5))
        k = ease_out_back(lt / 0.35)
        pill(c, W / 2, 260, "LIMITIERTE EDITION", 70, (40, 8, 14), scale=k, rot=-4, emo="⏳")
        pill(c, W / 2, 1200, "BLACK FRIDAY DEAL", 72, accent, scale=ease_out_back((lt - 0.5) / 0.3), rot=3, emo="💥")
        return c

    def s_cta(t, lt):
        c = bg.copy().convert("RGBA")
        shake = 6 * math.sin(lt * 40) * max(0, 1 - lt / 0.4)
        paste_center(c, jar_s, W / 2 + shake, 660, 1.0 + 0.03 * math.sin(lt * 8))
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 190, "BEVOR'S WEG IST!", 96, (255, 226, 50))
        cart_cta(c, t, t - lt, accent)
        return c

    def scenes(T, total):
        return [(0, s_hook), (T("Ein"), s_couple), (T("Aufs"), s_uses),
                (T("Limitierte"), s_deal), (T("Tipp"), s_cta)]

    def sfx(T, total):
        return [(0.0, "boom"), (0.6, "pop"), (T("Ein"), "whoosh"), (T("Schatz"), "ding"),
                (T("Aufs"), "whoosh"), (T("Brot"), "pop"),
                (T("Limitierte"), "boom"), (T("Black"), "pop"), (T("Tipp"), "whoosh")]

    return dict(name="1_honig_heisse_liebe", voice="honey_b", accent=accent,
                fix={9: "Bourbon-Vanille!", 18: "„Schatz“!"},
                scenes=scenes, sfx=sfx,
                post=("CAPTION:\nDieser Honig hat mehr Romantik als meine letzte Beziehung 🍯❤️ "
                      "Heiße Liebe – Honig mit Himbeeren & Bourbon-Vanille, limitierte Edition. "
                      "Link im Warenkorb 🛒\n\n#honig #heißeliebe #blackfriday #tiktokmademebuyit "
                      "#geschenkidee #imker #foodtok #tiktokshop #weihnachtsgeschenk\n"))

# ================================================================= PROTEIN
def protein():
    bg = gradient((232, 30, 90), (120, 8, 50))
    tub = load_img("protein_tub.png", h=860, rad=60)
    tub_s = load_img("protein_tub.png", h=600, rad=50)
    bag = load_img("protein_bag.png", w=900, rad=50)
    accent = (20, 20, 20)

    def s_hook(t, lt):
        c = bg.copy().convert("RGBA")
        k = ease_out_back(lt / 0.4)
        paste_center(c, tub, W / 2, 800, 0.3 + 0.7 * k, rot=(1 - k) * 18)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 220, "BROWNIE, ABER DIE DIÄT MERKT'S NICHT", 84, (255, 255, 255))
        e = emoji("🍫", 140); paste_center(c, e, 160, 1180 + 14 * math.sin(lt * 6), 1, rot=-12, shadow=False)
        e = emoji("🤯", 130); paste_center(c, e, 920, 1160, ease_out_back((lt - 0.4) / 0.3), shadow=False)
        return c

    def s_stats(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, tub, 330, 820, 0.72, rot=-4)
        items = [("23 g", "PROTEIN", 0.0), ("-95 %", "ZUCKER*", 1.0), ("100 %", "VEGAN", 1.9)]
        for i, (big, small, dl) in enumerate(items):
            k = ease_out_back((lt - dl) / 0.3)
            if k <= 0: continue
            im = Image.new("RGBA", (420, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, 419, 229], 40, fill=(255, 255, 255), outline=(20, 20, 20), width=6)
            d.text((210, 95), big, font=font(FB, 100), fill=(220, 20, 80), anchor="mm")
            d.text((210, 185), small, font=font(FB, 50), fill=(20, 20, 20), anchor="mm")
            paste_center(c, im, 800, 470 + i * 290, k, rot=(-1) ** i * 4)
        return c

    def s_diet(t, lt):
        c = bg.copy().convert("RGBA")
        jit = 8 * math.sin(lt * 30)
        paste_center(c, tub, W / 2 + jit, 820, 0.9, rot=math.sin(lt * 5) * 4)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 230, "MEINE DIÄT:", 96, (255, 255, 255))
        e = emoji("🙈", 200); paste_center(c, e, W / 2, 420, ease_out_back((lt - 0.2) / 0.3), shadow=False)
        e = emoji("🤫", 150); paste_center(c, e, 880, 1150, ease_out_back((lt - 1.2) / 0.3), shadow=False)
        return c

    def s_how(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, bag, W / 2, 760, 0.9 + lt * 0.05, rot=-3)
        pill(c, 270, 300, "WASSER", 60, (30, 120, 220), scale=ease_out_back(lt / 0.3), rot=-6, emo="💧")
        pill(c, 760, 300, "LÖFFEL", 60, (20, 20, 20), scale=ease_out_back((lt - 0.45) / 0.3), rot=5, emo="🥄")
        pill(c, W / 2, 1180, "FERTIG!", 76, (40, 170, 80), scale=ease_out_back((lt - 0.9) / 0.3), emo="✅")
        return c

    def s_cta(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, tub_s, W / 2, 650, 1.0 + 0.03 * math.sin(lt * 8))
        k = ease_out_back((lt - 1.3) / 0.35)
        e = emoji("🥦", 170); paste_center(c, e, 900, 420 + 10 * math.sin(lt * 9), k, rot=-15, shadow=False)
        pill(c, 860, 250, "SORRY, BROKKOLI", 40, (40, 140, 60), scale=k, rot=6)
        cart_cta(c, t, t - lt, (20, 20, 20))
        return c

    def scenes(T, total):
        return [(0, s_hook), (T("23"), s_stats), (T("Meine"), s_diet), (T("Mit"), s_how), (T("Tipp"), s_cta)]

    def sfx(T, total):
        return [(0.0, "boom"), (T("23"), "pop"), (T("95"), "pop"), (T("Brownie", 8), "pop"),
                (T("Meine"), "whoosh"), (T("Mit"), "whoosh"), (T("fertig"), "ding"), (T("Tipp"), "boom")]

    return dict(name="2_more_protein_dessert", voice="protein_b", accent=(255, 226, 50),
                fix={2: "Dessert", 4: "Brownie-", 5: "Style!", 44: "Brokkoli"},
                scenes=scenes, sfx=sfx,
                post=("CAPTION:\nDessert ohne schlechtes Gewissen? Meine Diät schaut einfach weg 🙈🍫 "
                      "More Protein Dessert Brownie Style – 23 g Protein pro Portion, vegan. "
                      "Hol's dir über den Warenkorb 🛒\n\n#morenutrition #protein #proteindessert #fitfood "
                      "#abnehmen #highprotein #tiktokmademebuyit #tiktokshop #gymtok\n\n"
                      "*laut Hersteller: 95 % weniger Zucker im Vergleich zu herkömmlichen Desserts\n"))

# ================================================================= ZINC
def zinc():
    bg = gradient((40, 40, 46), (10, 10, 12))
    bottle = load_img("zinc_bottle.png", h=880, rad=60)
    bottle_s = load_img("zinc_bottle.png", h=600, rad=50)
    claims = load_img("zinc_claims.png", w=960, rad=40)
    accent = (245, 120, 70)

    def s_hook(t, lt):
        c = bg.copy().convert("RGBA")
        k = ease_out_back(lt / 0.4)
        paste_center(c, bottle, W / 2, 820, 0.3 + 0.7 * k, rot=(1 - k) * -15)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 220, "FÜR ALLE, DIE ALLES VERGESSEN", 88, (255, 255, 255))
        pill(c, W / 2, 1190, "25 MG PRO KAPSEL", 60, accent, scale=ease_out_back((lt - 1.2) / 0.3), emo="💊")
        return c

    def s_forget(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, bottle, 300, 820, 0.62, rot=-6 + math.sin(lt * 4) * 2)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 230, "ICH VERGESSE:", 90, (255, 255, 255))
        items = [("🔑", "SCHLÜSSEL", "Schlüssel"), ("📱", "HANDY", "Handy"), ("🎂", "GEBURTSTAGE", "Geburtstage")]
        for i, (em, label, tok) in enumerate(items):
            st = forget_times[tok] - (t - lt)
            k = ease_out_back((lt - st) / 0.25)
            if k <= 0: continue
            y = 520 + i * 250
            e = emoji(em, 110); paste_center(c, e, 640, y, k, shadow=False)
            im = Image.new("RGBA", (420, 120), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            dd.text((0, 60), label, font=font(FB, 58 if len(label) < 10 else 48), fill=(255, 255, 255), anchor="lm")
            paste_center(c, im, 920, y, k, shadow=False)
            e = emoji("❌", 70); paste_center(c, e, 990, y - 50, ease_out_back((lt - st - 0.3) / 0.2), shadow=False)
        return c

    def s_never(t, lt):
        c = bg.copy().convert("RGBA")
        k = ease_out_back(lt / 0.35)
        paste_center(c, bottle, W / 2, 800, 0.8 + 0.15 * k)
        d = ImageDraw.Draw(c)
        text_block(d, W / 2, 230, "DIE KAPSEL AM MORGEN?", 84, (255, 255, 255))
        kk = ease_out_back((t - never_t) / 0.25)
        pill(c, W / 2, 1190, "NIE!", 110, (40, 170, 80), scale=kk, rot=-5, emo="✅")
        return c

    def s_claim(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, claims, W / 2, 760, 0.95 + lt * 0.03)
        pill(c, W / 2, 230, "IMMUNSYSTEM-SUPPORT", 64, accent, scale=ease_out_back(lt / 0.3), emo="🛡️")
        return c

    def s_cta(t, lt):
        c = bg.copy().convert("RGBA")
        paste_center(c, bottle_s, W / 2, 660, 1.0 + 0.03 * math.sin(lt * 8))
        d = ImageDraw.Draw(c)
        pill(c, W / 2, 210, "BLACK FRIDAY PREIS", 74, (228, 40, 80), scale=ease_out_back(lt / 0.3), rot=-3, emo="💥")
        cart_cta(c, t, t - lt + 0.5, accent)
        return c

    forget_times = {}; never_t = 0
    def scenes(T, total):
        nonlocal never_t
        for tok in ("Schlüssel", "Handy", "Geburtstage"): forget_times[tok] = T(tok)
        never_t = T("Nie")
        return [(0, s_hook), (T("ich"), s_forget), (T("aber"), s_never), (T("Zink", 5), s_claim), (T("Black"), s_cta)]

    def sfx(T, total):
        return [(0.0, "boom"), (T("25"), "pop"), (T("ich"), "whoosh"), (T("Schlüssel"), "pop"),
                (T("Handy"), "pop"), (T("Geburtstage"), "pop"), (T("aber"), "whoosh"), (T("Nie"), "ding"),
                (T("Zink", 5), "whoosh"), (T("Black"), "boom")]

    return dict(name="3_esn_zink", voice="zinc_a", accent=accent,
                fix={4: "Zinkbisglycinat", 5: None, 6: None, 10: "Stück!", 32: "bei!",
                     37: "Black-", 38: "Friday-", 39: "Preis!"},
                cut_words=[(33, 36)],   # drop "perfekt für den Winter" to fit 15-17 s
                scenes=scenes, sfx=sfx,
                post=("CAPTION:\nIch vergess ALLES – außer meine Zink-Kapsel am Morgen 😅💊 "
                      "ESN Zink: 25 mg Zinkbisglycinat, 120 vegane Kapseln. Zink trägt zu einer normalen "
                      "Funktion des Immunsystems bei. Black-Friday-Deal im Warenkorb 🛒\n\n"
                      "#esn #zink #supplements #immunsystem #gymtok #fitness #blackfriday #tiktokshop "
                      "#tiktokmademebuyit\n\nHinweis: Nahrungsergänzungsmittel sind kein Ersatz für eine "
                      "ausgewogene, abwechslungsreiche Ernährung und eine gesunde Lebensweise.\n"))

if __name__ == "__main__":
    which = sys.argv[1:] or ["honey", "protein", "zinc"]
    for w_ in which:
        render({"honey": honey, "protein": protein, "zinc": zinc}[w_]())
