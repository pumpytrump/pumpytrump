#!/usr/bin/env python3
"""Stickman TikTok Shop videos: a fully animated character (every frame moves) holding the real products.

python3 make.py [d3|levlup|schoko ...]   -> out/*.mp4  (1080x1920, 30 fps, ~16.5 s)
Needs: pycairo, numpy, Pillow, ffmpeg; assets/*.wav (voice), assets/words.json (word timings), product cutouts.
"""
import json, math, os, subprocess, sys, random
import numpy as np
import cairo
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets"); OUT = os.path.join(HERE, "out"); TMP = os.path.join(HERE, ".tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 30, 44100
TAIL = 0.65
FONT = "Inter Display"
YEL = (1, 0.886, 0.2); WHITE = (1, 1, 1); BLACK = (0, 0, 0)

# ============================================================ math / easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def win(t, a, b, fade=0.15):
    """1 inside [a,b] with soft edges."""
    return ease((t - a) / fade) * (1 - ease((t - b) / fade))

# ============================================================ assets
def surf_from_pil(im):
    im = im.convert("RGBA"); a = np.asarray(im).astype(np.float32)
    al = a[..., 3:4] / 255.0
    bgra = np.empty_like(a); bgra[..., 0] = a[..., 2]; bgra[..., 1] = a[..., 1]; bgra[..., 2] = a[..., 0]
    bgra[..., :3] *= al; bgra[..., 3] = a[..., 3]
    h, w = a.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    buf[:, :w] = bgra.astype(np.uint8); s.mark_dirty()
    return s

_img = {}
def img(name, max_side=700):
    if name not in _img:
        im = Image.open(os.path.join(A, name)).convert("RGBA")
        k = max_side / max(im.size)
        if k < 1: im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
        _img[name] = surf_from_pil(im)
    return _img[name]

def draw_img(cr, s, cx, cy, height, rot=0.0, alpha=1.0, flip=False):
    if height <= 1 or alpha <= 0: return
    k = height / s.get_height()
    cr.save(); cr.translate(cx, cy); cr.rotate(math.radians(rot)); cr.scale(-k if flip else k, k)
    # soft drop shadow
    cr.save(); cr.translate(8 / k, 14 / k)
    cr.set_source_rgba(0, 0, 0, 0.18 * alpha)
    cr.mask_surface(s, -s.get_width() / 2, -s.get_height() / 2); cr.restore()
    cr.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    cr.get_source().set_filter(cairo.FILTER_GOOD)
    cr.paint_with_alpha(alpha); cr.restore()

# ============================================================ text helpers
def font(cr, size):
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    try:
        fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); cr.set_font_options(fo)
    except Exception: pass
    cr.set_font_size(size)

def wrap(cr, text, maxw):
    lines, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if cr.text_extents(t).x_advance > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    if cur: lines.append(cur)
    return lines

def outlined(cr, text, x, y, size, fill=WHITE, stroke=BLACK, sw=12, maxw=980, scale=1.0, rot=0.0):
    if scale <= 0.01: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(scale, scale)
    font(cr, size)
    lines = wrap(cr, text, maxw); lh = size * 1.08
    y0 = -lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        e = cr.text_extents(ln)
        cr.move_to(-e.x_advance / 2, y0 + i * lh + size * 0.36)
        cr.text_path(ln)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgb(*stroke); cr.set_line_width(sw); cr.stroke_preserve()
    cr.set_source_rgb(*fill); cr.fill(); cr.restore()

def rrect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()

def pill(cr, text, x, y, size, bg, fg=WHITE, scale=1.0, rot=0.0):
    if scale <= 0.01: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(scale, scale)
    font(cr, size); e = cr.text_extents(text)
    pw, ph = e.x_advance + size * 1.3, size * 1.75
    rrect(cr, -pw / 2 + 6, -ph / 2 + 10, pw, ph, ph / 2); cr.set_source_rgba(0, 0, 0, 0.3); cr.fill()
    rrect(cr, -pw / 2, -ph / 2, pw, ph, ph / 2); cr.set_source_rgb(*bg); cr.fill_preserve()
    cr.set_source_rgb(1, 1, 1); cr.set_line_width(6); cr.stroke()
    cr.move_to(-e.x_advance / 2, size * 0.36); cr.set_source_rgb(*fg); cr.show_text(text)
    cr.restore()

# ============================================================ stickman
BASE = dict(x=540.0, y=1000.0, s=1.0, lean=0.0, tilt=0.0,
            lh=(-75.0, 255.0), rh=(75.0, 255.0), lf=(-62.0, 318.0), rf=(62.0, 318.0),
            eyes="dot", mouth="smile", ink=1.0, look=0.0, smear=0.0, sweat=0.0, blush=0.0)
TORSO, NECKH, HEADR = 235, 78, 64
UA, FA, TH, SH = 148, 140, 168, 160

def P(**kw):
    p = dict(BASE); p.update(kw); return p

def mixp(a, b, u):
    o = {}
    for k in a:
        va, vb = a[k], b.get(k, a[k])
        if isinstance(va, tuple): o[k] = tuple(lerp(x, y, u) for x, y in zip(va, vb))
        elif isinstance(va, (int, float)): o[k] = lerp(va, vb, u)
        else: o[k] = vb if u > 0.5 else va
    return o

def track(keys, t, dur=0.22):
    """keys: [(time, pose)], each pose eases in over `dur` starting at its time."""
    cur = keys[0][1]
    for tk, pk in keys[1:]:
        if t >= tk + dur: cur = pk
        elif t > tk: return mixp(cur, pk, ease((t - tk) / dur))
        else: break
    return cur

def ik(sx, sy, tx, ty, l1, l2, side):
    dx, dy = tx - sx, ty - sy; d = math.hypot(dx, dy)
    d = max(min(d, l1 + l2 - 0.5), abs(l1 - l2) + 0.5)
    a = math.atan2(dy, dx)
    b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    c1 = (sx + l1 * math.cos(a + b), sy + l1 * math.sin(a + b))
    c2 = (sx + l1 * math.cos(a - b), sy + l1 * math.sin(a - b))
    e = c1 if c1[0] * side > c2[0] * side else c2
    return e, (sx + d * math.cos(a), sy + d * math.sin(a))

def rig(p):
    s = p["s"]; L = math.radians(p["lean"])
    hip = (p["x"], p["y"])
    neck = (hip[0] + TORSO * s * math.sin(L), hip[1] - TORSO * s * math.cos(L))
    ht = L + math.radians(p["tilt"])
    head = (neck[0] + NECKH * s * math.sin(ht), neck[1] - NECKH * s * math.cos(ht))
    sh = (neck[0] - 12 * s * math.sin(L), neck[1] + 14 * s * math.cos(L))
    J = dict(hip=hip, neck=neck, head=head, sh=sh)
    for k, side in (("lh", -1), ("rh", 1)):
        tx, ty = p[k]; e, h = ik(sh[0], sh[1], sh[0] + tx * s, sh[1] + ty * s, UA * s, FA * s, side)
        J[k + "_e"], J[k] = e, h
    for k, side in (("lf", -1), ("rf", 1)):
        tx, ty = p[k]; e, h = ik(hip[0], hip[1], hip[0] + tx * s, hip[1] + ty * s, TH * s, SH * s, side)
        J[k + "_e"], J[k] = e, h
    return J

def ink_col(p):
    v = 0.08 + (1 - p["ink"]) * 0.78
    return (v, v, v)

def draw_face(cr, p, J, t):
    s = p["s"]; hx, hy = J["head"]; col = ink_col(p)
    cr.save(); cr.translate(hx, hy); cr.rotate(math.radians(p["lean"] + p["tilt"])); cr.scale(s, s)
    cr.set_source_rgb(*col); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    blink = (t % 3.1) < 0.1
    ex = p.get("look", 0)
    eyes = p["eyes"]
    for sx in (-1, 1):
        x0, y0 = sx * 23 + ex, -12
        if eyes == "happy":
            cr.set_line_width(7); cr.arc(x0, y0 + 6, 11, math.pi * 1.15, math.pi * 1.85); cr.stroke()
        elif eyes == "x":
            cr.set_line_width(7)
            cr.move_to(x0 - 9, y0 - 9); cr.line_to(x0 + 9, y0 + 9); cr.move_to(x0 + 9, y0 - 9); cr.line_to(x0 - 9, y0 + 9); cr.stroke()
        elif eyes == "wide":
            cr.set_line_width(5); cr.arc(x0, y0, 14, 0, 2 * math.pi); cr.stroke()
            cr.arc(x0 + ex * 0.2, y0, 6, 0, 2 * math.pi); cr.fill()
        elif eyes == "closed" or blink:
            cr.set_line_width(7); cr.move_to(x0 - 10, y0); cr.line_to(x0 + 10, y0); cr.stroke()
        elif eyes == "squint":
            cr.set_line_width(7); cr.move_to(x0 - 11, y0 - sx * 4); cr.line_to(x0 + 11, y0 + sx * 4); cr.stroke()
        else:
            cr.arc(x0, y0, 8, 0, 2 * math.pi); cr.fill()
    m = p["mouth"]; cr.set_line_width(7)
    if m == "chew": m = "open" if (t * 8) % 2 < 1 else "flat"
    if m == "smile": cr.arc(0, 10, 22, math.pi * 0.15, math.pi * 0.85); cr.stroke()
    elif m == "grin":
        cr.move_to(-26, 14); cr.line_to(26, 14); cr.arc(0, 14, 26, 0, math.pi); cr.close_path()
        cr.fill_preserve(); cr.stroke()
    elif m == "open": cr.save(); cr.translate(0, 24); cr.scale(1, 1.3); cr.arc(0, 0, 12, 0, 2 * math.pi); cr.restore(); cr.fill()
    elif m == "sad": cr.arc(0, 40, 20, math.pi * 1.2, math.pi * 1.8); cr.stroke()
    elif m == "flat": cr.move_to(-18, 26); cr.line_to(18, 26); cr.stroke()
    elif m == "sip": cr.arc(0, 24, 7, 0, 2 * math.pi); cr.stroke()
    elif m == "wavy":
        cr.move_to(-24, 26)
        for i in range(1, 7): cr.line_to(-24 + i * 8, 26 + (5 if i % 2 else -5))
        cr.stroke()
    if p.get("smear"):
        cr.set_source_rgba(0.36, 0.2, 0.1, 0.85 * p["smear"])
        for (x, y, r) in ((-30, 30, 9), (28, 22, 7), (6, 40, 6), (-12, 44, 5)):
            cr.arc(x, y, r, 0, 2 * math.pi); cr.fill()
    if p.get("sweat"):
        cr.set_source_rgba(0.35, 0.7, 1, p["sweat"])
        cr.move_to(52, -40); cr.curve_to(42, -18, 46, -6, 56, -6); cr.curve_to(66, -6, 68, -20, 52, -40); cr.fill()
    if p.get("blush"):
        cr.set_source_rgba(1, 0.4, 0.5, 0.45 * p["blush"])
        for sx in (-1, 1): cr.arc(sx * 38, 12, 11, 0, 2 * math.pi); cr.fill()
    cr.restore()

def draw_stick(cr, p, t, props=(), wear=(), hat=None):
    """props: list of dicts(surf|fn, at='rh'|'lh'|'mid', h, rot, dx, dy, alpha)."""
    J = rig(p); s = p["s"]; col = ink_col(p)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    lw = 17 * s
    def seg(*pts):
        for c_, w_ in (((1, 1, 1), lw + 12), (col, lw)) if p.get("outline") else ((col, lw),):
            cr.move_to(*pts[0])
            for q in pts[1:]: cr.line_to(*q)
            cr.set_source_rgb(*c_); cr.set_line_width(w_); cr.stroke()
    # ground shadow
    gy = max(J["lf"][1], J["rf"][1]) + 6
    cr.save(); cr.translate(p["x"], p.get("ground", gy)); cr.scale(1, 0.16)
    cr.arc(0, 0, 120 * s, 0, 2 * math.pi); cr.set_source_rgba(0, 0, 0, 0.15); cr.fill(); cr.restore()
    seg(J["sh"], J["lh_e"], J["lh"])
    seg(J["hip"], J["lf_e"], J["lf"]); seg(J["hip"], J["rf_e"], J["rf"])
    seg(J["hip"], J["neck"])
    for f in wear: f(cr, J, p)
    hx, hy = J["head"]
    if p.get("outline"): cr.arc(hx, hy, HEADR * s + lw * 0.45 + 6, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.arc(hx, hy, HEADR * s, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill_preserve()
    cr.set_source_rgb(*col); cr.set_line_width(lw * 0.85); cr.stroke()
    draw_face(cr, p, J, t)
    if hat: hat(cr, J, p)
    seg(J["sh"], J["rh_e"], J["rh"])
    for pr in props:
        at = pr.get("at", "rh")
        if at == "mid": ax, ay = (J["lh"][0] + J["rh"][0]) / 2, (J["lh"][1] + J["rh"][1]) / 2
        elif at in J: ax, ay = J[at]
        else: ax, ay = at
        cx, cy = ax + pr.get("dx", 0) * s, ay + pr.get("dy", 0) * s
        if "fn" in pr: pr["fn"](cr, cx, cy, pr.get("h", 100) * s, pr.get("rot", 0))
        else: draw_img(cr, pr["surf"], cx, cy, pr["h"] * s, pr.get("rot", 0), pr.get("alpha", 1))
    for k in ("lh", "rh"):  # hands on top of props = grip
        if p.get("outline"): cr.arc(*J[k], 20 * s, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
        cr.arc(*J[k], 14 * s, 0, 2 * math.pi); cr.set_source_rgb(*col); cr.fill()
    return J

# ============================================================ shared fx
class Particles:
    def __init__(self, seed=0): self.rng = random.Random(seed); self.ps = []
    def burst(self, x, y, n, cols, spd=900, life=1.0, size=(8, 16), grav=1800, kind="dot"):
        for _ in range(n):
            a = self.rng.uniform(0, 2 * math.pi); v = self.rng.uniform(0.3, 1) * spd
            self.ps.append(dict(x=x, y=y, vx=math.cos(a) * v, vy=math.sin(a) * v - spd * 0.5, life=life,
                                age=0, r=self.rng.uniform(*size), c=self.rng.choice(cols), g=grav, kind=kind,
                                rot=self.rng.uniform(0, 6), vr=self.rng.uniform(-10, 10)))
    def step_draw(self, cr, dt):
        keep = []
        for q in self.ps:
            q["age"] += dt
            if q["age"] > q["life"]: continue
            q["vy"] += q["g"] * dt; q["x"] += q["vx"] * dt; q["y"] += q["vy"] * dt; q["rot"] += q["vr"] * dt
            a = 1 - q["age"] / q["life"]
            cr.save(); cr.translate(q["x"], q["y"]); cr.rotate(q["rot"])
            cr.set_source_rgba(*q["c"], a)
            if q["kind"] == "rect": cr.rectangle(-q["r"], -q["r"] / 2, q["r"] * 2, q["r"]); cr.fill()
            else: cr.arc(0, 0, q["r"], 0, 2 * math.pi); cr.fill()
            cr.restore(); keep.append(q)
        self.ps = keep

def captions(cr, words, t, y=1500):
    chunks, cur = [], []
    for i, (w_, s, e) in enumerate(words):
        cur.append(i)
        txt = " ".join(words[j][0] for j in cur)
        if len(cur) >= 3 or len(txt) >= 15 or w_[-1] in ".,!?:": chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    act = None
    for ch in chunks:
        if words[ch[0]][1] - 0.02 <= t <= words[ch[-1]][2] + 0.2: act = ch
    if not act: return
    size = 88; font(cr, size); gap = 32
    toks = [words[i][0].upper() for i in act]
    ws = [cr.text_extents(x).x_advance for x in toks]; tot = sum(ws) + gap * (len(ws) - 1)
    if tot > 1000: size = int(size * 1000 / tot); font(cr, size); ws = [cr.text_extents(x).x_advance for x in toks]; tot = sum(ws) + gap * (len(ws) - 1)
    x = (W - tot) / 2
    for i, tok, wd in zip(act, toks, ws):
        s, e = words[i][1], words[i][2]
        on = s <= t < max(e, s + 0.12) + 0.06
        pop = 1 + 0.07 * max(0, 1 - (t - s) / 0.15) if on else 1
        outlined(cr, tok, x + wd / 2, y, size, YEL if on else WHITE, sw=13, maxw=2000, scale=pop)
        x += wd + gap

def cta(cr, t, t0, col):
    k = back((t - t0) / 0.35)
    if k <= 0: return
    pulse = 1 + 0.06 * math.sin((t - t0) * 12)
    pill(cr, "JETZT IM WARENKORB", W / 2, 1360, 60, col, scale=k * pulse)
    bob = 22 * math.sin((t - t0) * 10)
    cr.save(); cr.translate(200, 1640 + bob); cr.scale(k, k)
    cr.move_to(0, 120); cr.line_to(-95, 0); cr.line_to(-38, 0); cr.line_to(-38, -120); cr.line_to(38, -120)
    cr.line_to(38, 0); cr.line_to(95, 0); cr.close_path()
    cr.set_source_rgb(*YEL); cr.fill_preserve(); cr.set_source_rgb(0, 0, 0); cr.set_line_width(8); cr.stroke()
    cr.restore()

def hook(cr, text, t, until, y=300, col=WHITE):
    k = back(t / 0.3) * (1 - ease((t - until) / 0.25))
    outlined(cr, text, W / 2, y, 82, col, sw=14, maxw=940, scale=k)

# ============================================================ audio
def write_wav(path, pcm):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", path],
                   input=pcm.astype(np.float32).tobytes(), check=True)

def sfx_track(events, dur):
    n = int(dur * SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    for t, kind in events:
        s = int(max(0, t) * SR)
        if kind == "pop":
            L = int(0.09 * SR); x = np.arange(L) / SR; f = 900 * np.exp(-x * 30) + 250
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 45) * 0.35
        elif kind == "whoosh":
            L = int(0.35 * SR); x = np.arange(L) / SR
            nz = np.convolve(rng.standard_normal(L), np.ones(40) / 40, "same")
            sig = nz * np.sin(np.pi * x / x[-1]) ** 2 * 0.6
        elif kind == "ding":
            L = int(0.7 * SR); x = np.arange(L) / SR
            sig = (np.sin(2 * np.pi * 1320 * x) + 0.5 * np.sin(2 * np.pi * 1980 * x)) * np.exp(-x * 6) * 0.2
        elif kind == "boom":
            L = int(0.5 * SR); x = np.arange(L) / SR
            sig = np.sin(2 * np.pi * (55 + 90 * np.exp(-x * 20)) * x) * np.exp(-x * 8) * 0.7
        elif kind == "boing":
            L = int(0.4 * SR); x = np.arange(L) / SR; f = 180 + 260 * x / x[-1] + 40 * np.sin(2 * np.pi * 14 * x)
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 5) * 0.3
        elif kind == "crack":   # can opening: click + fizz
            L = int(0.8 * SR); x = np.arange(L) / SR; nz = rng.standard_normal(L)
            hp = nz - np.convolve(nz, np.ones(6) / 6, "same")
            sig = hp * (np.exp(-x * 60) * 0.9 + 0.18 * np.exp(-x * 4)); sig[:int(0.004 * SR)] += 0.8
        elif kind == "crunch":
            L = int(0.25 * SR); x = np.arange(L) / SR; nz = rng.standard_normal(L)
            env = np.exp(-x * 18) * (0.6 + 0.4 * (np.sin(2 * np.pi * 40 * x) > 0))
            sig = (nz - np.convolve(nz, np.ones(3) / 3, "same")) * env * 0.45
        elif kind == "gulp":
            L = int(0.22 * SR); x = np.arange(L) / SR; f = 420 - 300 * x / x[-1]
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / x[-1]) * 0.4
        elif kind == "buzz":
            L = int(0.5 * SR); x = np.arange(L) / SR
            sig = np.sign(np.sin(2 * np.pi * 110 * x)) * np.exp(-x * 3) * 0.12
        elif kind == "tada":
            L = int(0.9 * SR); x = np.arange(L) / SR; sig = np.zeros(L)
            for i, f in enumerate((523, 659, 784, 1047)):
                st = int(i * 0.08 * SR); xx = x[: L - st]
                sig[st:] += np.sin(2 * np.pi * f * xx) * np.exp(-xx * 4) * 0.12
        else: continue
        e = min(n, s + len(sig)); out[s:e] += sig[: e - s]
    return out

# ============================================================ renderer
def render(name, voice, caption_words, frame_fn, sfx, total_pad=TAIL):
    wj = json.load(open(os.path.join(A, "words.json")))[voice]
    assert len(wj) == len(caption_words), (len(wj), len(caption_words))
    words = []
    for (w_, s, e), c in zip(wj, caption_words):
        if c is None: words[-1] = (words[-1][0], words[-1][1], e)
        else: words.append((c, s, e))
    Ts = [s for _, s, _ in wj]
    vdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 os.path.join(A, voice + ".wav")], capture_output=True, text=True).stdout)
    total = vdur + total_pad
    fx = sfx_track([(Ts[i] if isinstance(i, int) else i, k) for i, k in sfx(Ts)], total + 1)
    write_wav(os.path.join(TMP, name + "_sfx.wav"), fx)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    out = os.path.join(OUT, name + ".mp4")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", os.path.join(A, voice + ".wav"), "-i", os.path.join(TMP, name + "_sfx.wav"),
                           "-filter_complex", "[1:a]aresample=44100,apad[v];[2:a]volume=0.85[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                           "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "16", "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    state = {}
    for fi in range(int(total * FPS)):
        t = fi / FPS
        cr = cairo.Context(surf)
        cr.set_antialias(cairo.ANTIALIAS_BEST)
        frame_fn(cr, t, Ts, total, state)
        captions(cr, words, t)
        cr.rectangle(0, 0, W * t / total, 10); cr.set_source_rgb(*YEL); cr.fill()
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait()
    print(f"[{name}] {total:.2f}s -> {out}")

def camera(cr, t, shake_times, zoom=0.04):
    """Slow continuous push-in plus impact shakes -> the whole frame is always moving."""
    z = 1 + zoom * (0.5 + 0.5 * math.sin(t * 0.7))
    sx = sy = 0
    for ts in shake_times:
        d = t - ts
        if 0 <= d < 0.35:
            a = 22 * (1 - d / 0.35); sx += a * math.sin(d * 90); sy += a * math.cos(d * 70)
    cr.translate(W / 2 + sx, H / 2 + sy); cr.scale(z, z); cr.translate(-W / 2, -H / 2)

# ============================================================ VIDEO 1: ESN Vitamin D3+K2
def video_d3():
    bottle = img("d3.png", 600)
    cw = ["ESN", "Vitamin", "D3", "plus", "K2!", "Deutschland", "im", "Winter:", "grau,", "nass,", "null Sonne.",
          "Ich", "bin", "schon", "so", "blass,", "man", "sieht", "mich", "kaum", "noch.", "Also:", "eine", "Tablette",
          "am", "Tag.", "Vitamin", "D", "trägt", "zur", "normalen", "Funktion", "des", "Immunsystems", "bei.", "Sonne",
          "kann", "man", "nicht", "kaufen.", "Das", "hier", "schon!", "Tipp", "unten", "auf", "den", "Waren-", "korb!"]
    PURPLE = (0.55, 0.42, 0.85)
    rng = random.Random(5)
    drops = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(900, 1400)) for _ in range(140)]
    clouds = [(rng.uniform(-200, W), rng.uniform(150, 650), rng.uniform(0.8, 1.4), rng.uniform(15, 40)) for _ in range(6)]

    def frame(cr, t, T, total, st):
        T_de, T_ich, T_also, T_tab, T_vit, T_sonne, T_das, T_tipp = T[5], T[11], T[21], T[23], T[26], T[35], T[40], T[43]
        T_gulp = T[25] + 0.15
        sun = ease((t - T_gulp) / 0.8)
        rain = win(t, T_de - 0.1, T_gulp, 0.3)
        # sky
        g = cairo.LinearGradient(0, 0, 0, H)
        top = [lerp(a, b, sun) for a, b in zip((0.45, 0.48, 0.52), (0.33, 0.66, 1.0))]
        bot = [lerp(a, b, sun) for a, b in zip((0.7, 0.72, 0.74), (0.75, 0.9, 1.0))]
        g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot); cr.set_source(g); cr.paint()
        cr.save(); camera(cr, t, [T_gulp, T_das])
        # sun
        if sun > 0:
            cx, cy = 860, 560 - 120 * (1 - sun)
            cr.save(); cr.translate(cx, cy); cr.rotate(t * 0.8)
            for i in range(12):
                cr.rotate(math.pi / 6); cr.move_to(0, -140); cr.line_to(-20, -230 * sun); cr.line_to(20, -230 * sun); cr.close_path()
                cr.set_source_rgba(1, 0.8, 0.1, sun); cr.fill()
            cr.restore(); cr.arc(cx, cy, 120 * sun, 0, 2 * math.pi); cr.set_source_rgb(1, 0.85, 0.15); cr.fill()
        # clouds drift away when sunny
        for (x0, y0, k, v) in clouds:
            x = (x0 + v * t) % (W + 500) - 250 + sun * 900 * (1 if x0 > W / 2 else -1)
            dark = lerp(0.55, 0.95, sun)
            cr.set_source_rgba(dark, dark, dark + 0.03, 0.95)
            for dx, dy, r in ((0, 0, 70), (70, -30, 85), (150, 0, 70), (75, 25, 75)):
                cr.arc(x + dx * k, y0 + dy * k, r * k, 0, 2 * math.pi); cr.fill()
        # ground
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(*[lerp(a, b, sun) for a, b in zip((0.42, 0.45, 0.42), (0.45, 0.75, 0.35))]); cr.fill()
        # rain
        if rain > 0:
            cr.set_source_rgba(0.75, 0.82, 1, 0.7 * rain); cr.set_line_width(4)
            for x0, y0, v in drops:
                y = (y0 + v * t) % (H + 100) - 50; x = x0 - 0.15 * ((v * t) % (H + 100))
                x %= W; cr.move_to(x, y); cr.line_to(x - 8, y + 45); cr.stroke()

        # ---- stickman choreography
        stand = P(rh=(130, 60), lh=(-80, 250))
        hold_up = P(rh=(110, -235), lh=(-120, 120), mouth="grin", eyes="happy")
        shiver = P(lh=(80, 60), rh=(175, 150), mouth="wavy", eyes="squint")
        pale = P(lh=(-185, 80), rh=(185, 80), mouth="open", eyes="wide")
        take = P(lh=(-185, 100), rh=(-70, 80), mouth="smile")
        to_mouth = P(lh=(-185, 100), rh=(15, -55), mouth="open", eyes="dot")
        flexA = P(lh=(-215, -95), rh=(120, -230), mouth="grin", eyes="happy", lean=-4)
        flexB = P(lh=(-120, -230), rh=(215, -95), mouth="grin", eyes="happy", lean=4)
        point_sun = P(rh=(230, -200), lh=(-195, 90), mouth="smile", look=10)
        present = P(lh=(-215, 0), rh=(170, 30), mouth="grin", eyes="happy")
        point_dn = P(rh=(-120, 170), lh=(-150, -200), mouth="grin", eyes="dot", lean=-6)
        keys = [(0, hold_up), (T_de, shiver), (T_ich, pale), (T_also, take), (T_tab + 0.1, to_mouth),
                (T_gulp + 0.25, flexA)]
        tt = T_gulp + 0.25
        while tt < T_sonne - 0.3:
            tt += 0.5; keys.append((tt, flexB if len(keys) % 2 else flexA))
        keys += [(T_sonne, point_sun), (T_das, present), (T_tipp, point_dn)]
        p = track(keys, t)
        # entry jump
        if t < 0.6:
            u = t / 0.6; p["x"] = lerp(1300, 540, ease(u)); p["y"] -= 380 * math.sin(math.pi * u)
        p["y"] += 6 * math.sin(t * 7.5)                               # breathing / bounce
        if T_tipp <= t: p["y"] -= abs(math.sin(t * 6)) * 30
        if T_de <= t < T_ich: p["x"] += 7 * math.sin(t * 60)          # shiver
        # pale -> recover
        p["ink"] = 1 - 0.8 * ease((t - T_ich - 0.3) / 1.0) * (1 - ease((t - T_gulp) / 0.25))
        props = []
        if t >= T_also and t < T_gulp + 0.25:
            props.append(dict(surf=bottle, at="lh", h=250, dy=-55))
        else:
            props.append(dict(surf=bottle, at="rh" if t < T_sonne else "lh", h=250, dy=-60,
                              rot=10 * math.sin(t * 3)))
        if T_das <= t < T_tipp:
            props[-1]["h"] = 250 * (1 + 0.35 * back((t - T_das) / 0.35))
        if T_tab - 0.1 <= t < T_gulp:
            props.append(dict(fn=lambda cr, x, y, h, r: (cr.arc(x, y - 18, 16, 0, 2 * math.pi), cr.set_source_rgb(1, 1, 1),
                              cr.fill_preserve(), cr.set_source_rgb(0.6, 0.6, 0.6), cr.set_line_width(3), cr.stroke()), at="rh"))
        draw_stick(cr, p, t, props)
        # gulp flash
        if T_gulp <= t < T_gulp + 0.4:
            cr.set_source_rgba(1, 1, 0.8, 0.7 * (1 - (t - T_gulp) / 0.4)); cr.paint()
        cr.restore()
        # overlays
        hook(cr, "WENN DU IM WINTER UNSICHTBAR WIRST", t, T_de - 0.1)
        for i, (txt, col, x, rot) in enumerate((("GRAU", (0.4, 0.4, 0.45), 230, -6), ("NASS", (0.2, 0.45, 0.8), 520, 4), ("NULL SONNE", (0.25, 0.25, 0.3), 820, -3))):
            ts = T[8 + i]
            pill(cr, txt, x, (290, 410, 290)[i], 56, col, scale=back((t - ts) / 0.25) * (1 - ease((t - T_ich) / 0.2)), rot=rot)
        if T_ich <= t < T_also:
            outlined(cr, "*wird unsichtbar*", W / 2, 320, 70, (0.85, 0.85, 0.85), scale=back((t - T_ich - 0.6) / 0.3))
        if T_also <= t < T_vit:
            pill(cr, "1 TABLETTE / TAG", W / 2, 300, 62, PURPLE, scale=back((t - T_also) / 0.3))
        if T_vit <= t < T_sonne:
            pill(cr, "VITAMIN D: NORMALES IMMUNSYSTEM", W / 2, 300, 46, PURPLE, scale=back((t - T_vit) / 0.3))
        if T_sonne <= t < T_tipp:
            outlined(cr, "SONNE ZUM MITNEHMEN", W / 2, 300, 80, YEL, scale=back((t - T_das) / 0.3))
        cta(cr, t, T_tipp, PURPLE)

    def sfx(T):
        g = T[25] + 0.15
        return [(0.0, "whoosh"), (0.55, "boing"), (5, "whoosh"), (8, "pop"), (9, "pop"), (10, "pop"),
                (11, "whoosh"), (23, "pop"), (g, "gulp"), (g + 0.15, "tada"), (26, "pop"), (35, "whoosh"),
                (40, "ding"), (43, "boom")]
    render("1_esn_vitamin_d3_k2", "d3", cw, frame, sfx)

# ============================================================ VIDEO 2: LevlUp Gaming Drink
def draw_can(cr, x, y, h, rot):
    w = h * 0.42
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot))
    g = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    g.add_color_stop_rgb(0, 0.3, 0.1, 0.5); g.add_color_stop_rgb(0.45, 0.58, 0.3, 0.85); g.add_color_stop_rgb(1, 0.25, 0.08, 0.42)
    rrect(cr, -w / 2, -h / 2, w, h, w * 0.18); cr.set_source(g); cr.fill()
    cr.rectangle(-w / 2 + 4, -h / 2, w - 8, h * 0.07); cr.set_source_rgb(0.8, 0.8, 0.85); cr.fill()
    cr.arc(w * 0.08, -h * 0.05, w * 0.36, 0, 2 * math.pi); cr.set_source_rgba(0.95, 0.3, 0.65, 0.8); cr.fill()
    cr.save(); cr.translate(-w * 0.12, h * 0.25); cr.rotate(-math.pi / 2)
    font(cr, w * 0.42); cr.set_source_rgb(1, 1, 1); cr.move_to(0, 0); cr.show_text("LEVLUP"); cr.restore()
    cr.restore()

def video_levlup():
    tray = img("levlup.png", 700)
    cw = ["LevlUp", None, "Gaming", "Drink,", "zero Zucker!", "Runde", "eins:", None, "verloren.", "Runde", "zwei:", None,
          "verloren.", "Runde", "drei:", None, "Dose", "auf.", "Und", "plötzlich:", None, "SIEG!", "Okay,", "vielleicht",
          "war's", "nicht", "nur", "der", "Drink.", "Aber", "der", "Geschmack?", "Galaxy,", "Cola", "Orange", "und", "mehr.",
          "Tipp", "unten", "auf", "den", "Waren-", "korb", "und", "level", "up!"]
    PUR = (0.55, 0.2, 0.85)
    parts = Particles(2)

    def frame(cr, t, T, total, st):
        T_r1, T_l1, T_r2, T_l2, T_r3, T_dose, T_auf, T_und, T_sieg, T_ok, T_aber, T_gal, T_tipp = \
            T[5], T[8], T[9], T[12], T[13], T[16], T[17], T[18], T[21], T[22], T[29], T[32], T[37]
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.3, 0.16, 0.48); g.add_color_stop_rgb(1, 0.12, 0.06, 0.22)
        cr.set_source(g); cr.paint()
        cr.save(); camera(cr, t, [T_sieg, T_auf])
        # RGB light strip
        for i in range(14):
            hue = (t * 0.4 + i / 14) % 1
            r, gg, b = [0.5 + 0.5 * math.sin(2 * math.pi * (hue + o)) for o in (0, 1 / 3, 2 / 3)]
            cr.rectangle(i * W / 14, 470, W / 14 + 1, 12); cr.set_source_rgb(r, gg, b); cr.fill()
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(0.1, 0.06, 0.15); cr.fill()
        # desk + monitor
        cr.rectangle(560, 1120, 560, 30); cr.set_source_rgb(0.25, 0.2, 0.3); cr.fill()
        cr.rectangle(600, 1150, 22, 180); cr.rectangle(1040, 1150, 22, 180); cr.fill()
        cr.rectangle(830, 1040, 40, 80); cr.fill()
        rrect(cr, 610, 720, 450, 330, 20); cr.set_source_rgb(0.08, 0.08, 0.1); cr.fill()
        sx0, sy0, sw_, sh_ = 630, 740, 410, 290
        lost = win(t, T_l1, T_r2 - 0.05, 0.05) or win(t, T_l2, T_r3 - 0.05, 0.05)
        victory = t >= T_sieg
        if victory:
            fl = 0.5 + 0.5 * math.sin(t * 14)
            cr.rectangle(sx0, sy0, sw_, sh_); cr.set_source_rgb(0.95, 0.7 + 0.2 * fl, 0.1); cr.fill()
            outlined(cr, "VICTORY!", sx0 + sw_ / 2, sy0 + sh_ / 2, 74, WHITE, sw=8, scale=back((t - T_sieg) / 0.3))
        elif lost > 0.5:
            cr.rectangle(sx0, sy0, sw_, sh_); cr.set_source_rgb(0.6, 0.05, 0.08); cr.fill()
            outlined(cr, "GAME OVER", sx0 + sw_ / 2, sy0 + sh_ / 2, 62, WHITE, sw=8)
        else:  # little "game": dodging blocks
            cr.rectangle(sx0, sy0, sw_, sh_); cr.set_source_rgb(0.05, 0.12, 0.25); cr.fill()
            spd = 3 if t < T_und else 9
            for i in range(6):
                bx = sx0 + ((i * 97 + t * 160 * spd / 3) % sw_); by = sy0 + 30 + (i * 53) % (sh_ - 60)
                cr.rectangle(bx, by, 26, 26); cr.set_source_rgb(0.9, 0.2 + 0.1 * i, 0.6); cr.fill()
            px = sx0 + 60; py = sy0 + sh_ / 2 + 80 * math.sin(t * (4 if t < T_und else 14))
            cr.arc(px, py, 18, 0, 2 * math.pi); cr.set_source_rgb(0.3, 1, 0.5); cr.fill()
            if t >= T_r1:
                rn = "RUNDE 3" if t >= T_r3 else "RUNDE 2" if t >= T_r2 else "RUNDE 1"
                font(cr, 30); cr.set_source_rgb(1, 1, 1); cr.move_to(sx0 + 14, sy0 + 40); cr.show_text(rn)
        # tray position: carried in overhead, then set onto desk
        desk_pos = (720, 1035)
        # ---- poses
        X = 330
        carry = P(x=X, lh=(-80, -250), rh=(80, -250), mouth="grin", eyes="happy")
        put = P(x=X, lh=(60, 60), rh=(200, 60), mouth="smile")
        game = P(x=X, lh=(40, 120), rh=(110, 120), mouth="flat", look=12)
        loseP = P(x=X, y=1030, lh=(-40, 250), rh=(60, 250), lean=8, tilt=18, mouth="sad", eyes="x")
        grab = P(x=X, lh=(40, 120), rh=(170, 60), mouth="smile", look=12)
        sip = P(x=X, lh=(40, 120), rh=(20, -60), mouth="sip", eyes="closed", tilt=-10)
        mash = P(x=X, lh=(30, 110), rh=(100, 110), mouth="open", eyes="wide", look=14)
        win_ = P(x=X, lh=(-110, -230), rh=(110, -235), mouth="grin", eyes="happy")
        shrug = P(x=X, lh=(-170, -40), rh=(170, -40), mouth="flat", eyes="dot", tilt=12)
        sip2 = P(x=X, lh=(-75, 250), rh=(20, -60), mouth="sip", eyes="happy")
        pointT = P(x=X, lh=(-60, 240), rh=(260, 40), mouth="grin", eyes="happy", look=14)
        ctaP = P(x=X, lh=(-120, -235), rh=(-110, 180), mouth="grin", eyes="happy", lean=-5)
        keys = [(0, carry), (1.55, put), (T_r1, game), (T_l1, loseP), (T_r2, game), (T_l2, loseP), (T_r3, grab),
                (T_auf + 0.15, sip), (T_und, mash), (T_sieg, win_), (T_ok + 0.2, shrug), (T_aber, sip2),
                (T_gal, pointT), (T_tipp, ctaP)]
        p = track(keys, t)
        if t < 0.7: u = t / 0.7; p["x"] = lerp(-250, X, ease(u)); p["lf"] = (-62 + 50 * math.sin(t * 20), 318); p["rf"] = (62 - 50 * math.sin(t * 20), 318)
        p["y"] += 6 * math.sin(t * 7)
        if T_und <= t < T_sieg:
            p["lh"] = (p["lh"][0] + 10 * math.sin(t * 70), p["lh"][1]); p["rh"] = (p["rh"][0], p["rh"][1] + 10 * math.sin(t * 64))
        if T_sieg <= t < T_ok: p["y"] -= 160 * abs(math.sin((t - T_sieg) * 5.5))
        if t >= T_tipp: p["y"] -= abs(math.sin(t * 6)) * 30
        p["sweat"] = win(t, T_ok, T_aber, 0.2); p["outline"] = 1
        props = []
        if t < 1.55: props.append(dict(surf=tray, at="mid", h=330, dy=-130))
        has_ctrl = T_r1 <= t < T_r3 or T_und <= t < T_sieg
        if has_ctrl:
            props.append(dict(fn=lambda cr, x, y, h, r: (rrect(cr, x - 70, y - 28, 140, 56, 26), cr.set_source_rgb(0.15, 0.15, 0.18), cr.fill()), at="mid"))
        if t >= T_r3 and not (T_und <= t < T_sieg):
            rot = -55 if (T_auf + 0.15 <= t < T_und or T_aber <= t < T_gal) else 0
            props.append(dict(fn=draw_can, at="lh" if t >= T_tipp else "rh", h=230, dy=-60 if rot == 0 else -20, rot=rot))
        J = draw_stick(cr, p, t, props)
        # tray on desk after set-down
        if t >= 1.55:
            u = ease((t - 1.55) / 0.3)
            start = ((J["lh"][0] + J["rh"][0]) / 2, (J["lh"][1] + J["rh"][1]) / 2 - 130)
            k = 1 + 0.12 * back((t - T_gal) / 0.3) * (1 - ease((t - T_tipp) / 0.3)) if t >= T_gal else 1
            draw_img(cr, tray, lerp(start[0], desk_pos[0], u), lerp(start[1], desk_pos[1], u), lerp(330, 230, u) * k)
        if t >= T_auf and "fizz" not in st:
            st["fizz"] = 1; parts.burst(J["rh"][0], J["rh"][1] - 170, 40, [(0.85, 0.6, 1), (1, 1, 1), (1, 0.5, 0.85)], spd=700, life=0.8, size=(5, 10))
        if t >= T_sieg and "conf" not in st:
            st["conf"] = 1; parts.burst(W / 2, 700, 160, [(1, 0.85, 0.1), (0.3, 0.9, 1), (1, 0.3, 0.6), (0.5, 1, 0.4)], spd=1500, life=1.6, size=(10, 18), grav=1400, kind="rect")
        parts.step_draw(cr, 1 / FPS)
        cr.restore()
        hook(cr, "WENN DU 2X VERLIERST UND DANN…", t, T_r3)
        if T_ok <= t < T_aber:
            outlined(cr, "(ehrlich gesagt: Skill Issue)", W / 2, 320, 60, (0.85, 0.85, 0.85), scale=back((t - T_ok - 0.3) / 0.3))
        for i, (txt, ts) in enumerate((("GALAXY", T[32]), ("COLA ORANGE", T[33]), ("+ MEHR SORTEN", T[35]))):
            if T_gal <= t < T_tipp:
                pill(cr, txt, (300, 760, 540)[i], 280 + 120 * i, 56, ((0.75, 0.2, 0.7), (0.95, 0.45, 0.1), PUR)[i], scale=back((t - ts) / 0.25), rot=(-5, 4, -2)[i])
        if t < 2.2 and t > 0.4:
            pill(cr, "ZERO ZUCKER", W / 2, 520, 52, PUR, scale=back((t - T[4]) / 0.25))
        cta(cr, t, T_tipp, PUR)

    def sfx(T):
        return [(0.0, "whoosh"), (1.6, "boom"), (8, "buzz"), (12, "buzz"), (16, "pop"), (17, "crack"),
                (T[17] + 0.55, "gulp"), (18, "whoosh"), (21, "tada"), (21, "boom"), (22, "boing"),
                (32, "pop"), (33, "pop"), (35, "pop"), (37, "boom")]
    render("2_levlup_gaming_drink", "levlup", cw, frame, sfx)

# ============================================================ VIDEO 3: Schokoellsen
def video_schoko():
    stack = img("schoko.png", 700); bar = img("bar.png", 700); pieces = img("pieces.png", 500)
    cw = ["Schokoellsen!", None, "Bei", "dieser", "Schokolade", "wird", "nicht", "gelogen.", "Also,", "ganz", "ehrlich,",
          "unter", "uns:", "Ich", "wollte", "nur", "ein", "Stück.", "Nur", "ein", "ganz", "kleines!", "Okay,", "die",
          "ganze", "Tafel.", "Und", "die", "zweite.", "Darum", "gibt's", "die", "direkt", "im", "Vierer-", "pack!",
          "Tipp", "unten", "auf", "den", "Waren-", "korb,", "bevor", "ich", "alle", "vier", "esse!"]
    RED = (0.85, 0.1, 0.12); BROWN = (0.45, 0.25, 0.12)
    parts = Particles(4)

    def frame(cr, t, T, total, st):
        T_bei, T_also, T_ich, T_nur, T_ok, T_ganze, T_und, T_zw, T_darum, T_vier, T_tipp = \
            T[2], T[8], T[13], T[18], T[22], T[24], T[26], T[28], T[29], T[34], T[36]
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 1, 0.93, 0.82); g.add_color_stop_rgb(1, 0.98, 0.8, 0.65)
        cr.set_source(g); cr.paint()
        cr.save(); camera(cr, t, [T_vier + 0.25, T_ok])
        # wallpaper dots drifting
        for i in range(40):
            x = (i * 137 + t * 25) % (W + 60) - 30; y = (i * 251) % 1250
            cr.arc(x, y, 10, 0, 2 * math.pi); cr.set_source_rgba(0.85, 0.55, 0.4, 0.25); cr.fill()
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(0.62, 0.38, 0.22); cr.fill()
        # table on right where the 4-pack lands
        cr.rectangle(640, 1150, 440, 26); cr.set_source_rgb(0.5, 0.3, 0.16); cr.fill()
        cr.rectangle(680, 1176, 20, 150); cr.rectangle(1030, 1176, 20, 150); cr.fill()
        X = 360
        lift = P(x=X, lh=(-80, -250), rh=(80, -250), mouth="grin", eyes="happy")
        honest = P(x=X, lh=(40, 90), rh=(170, 30), mouth="smile", eyes="closed")
        close = P(x=X + 120, y=930, s=1.28, lh=(30, -40), rh=(150, 120), mouth="flat", eyes="dot", look=-12, tilt=-8)
        piece = P(x=X, lh=(-60, 80), rh=(20, -55), mouth="open", eyes="dot")
        tiny = P(x=X, lh=(-130, -150), rh=(160, 40), mouth="smile", eyes="squint")
        munch = P(x=X, lh=(-80, 120), rh=(25, -45), mouth="chew", eyes="closed")
        munch2 = P(x=X, lh=(-25, -45), rh=(150, 60), mouth="chew", eyes="closed")
        present = P(x=X, lh=(-140, -100), rh=(260, -40), mouth="grin", eyes="happy", look=14)
        ctaP = P(x=X, lh=(-120, -235), rh=(-110, 180), mouth="grin", eyes="happy", lean=-5)
        keys = [(0, lift), (T_bei, honest), (T_also, close), (T_ich, piece), (T_nur, tiny), (T_ok, munch),
                (T_und, munch2), (T_darum, present), (T_tipp, ctaP)]
        p = track(keys, t, dur=0.25)
        if t < T_bei: p["y"] -= 120 * abs(math.sin(t * 6))
        p["y"] += 6 * math.sin(t * 7)
        if T_ok <= t < T_darum:  # frantic munching shake
            p["rh"] = (p["rh"][0] + 8 * math.sin(t * 50), p["rh"][1] + 8 * math.cos(t * 43))
            p["lh"] = (p["lh"][0] + 8 * math.sin(t * 47), p["lh"][1])
        if t >= T_tipp: p["y"] -= abs(math.sin(t * 6)) * 30
        p["smear"] = ease((t - T_ok - 0.4) / 0.6)
        p["blush"] = win(t, T_also, T_ich, 0.2)
        props = []
        if t < T_bei: props.append(dict(surf=stack, at="mid", h=320, dy=-140, rot=4 * math.sin(t * 8)))
        elif t < T_ok:
            props.append(dict(surf=bar, at="rh", h=150, dy=-40, rot=-8 if t < T_also else 0))
        else:
            eaten = ease((t - T_ok) / (T_und - T_ok))
            if t < T_und: props.append(dict(surf=bar, at="rh", h=130 * (1 - 0.75 * eaten), dy=25, rot=-30))
            if T_und <= t < T_darum:
                e2 = ease((t - T_zw) / (T_darum - T_zw))
                props.append(dict(surf=bar, at="lh", h=130 * (1 - 0.8 * e2), dy=25, rot=30))
        if T_ich <= t < T_nur:  # piece travels to mouth
            props.append(dict(surf=pieces, at="rh", h=60, dy=-10))
        if T_nur <= t < T_ok:
            props.append(dict(surf=pieces, at="lh", h=45, dy=-30))
        J = draw_stick(cr, p, t, props)
        if T_ok <= t < T_darum and int(t * FPS) % 4 == 0:
            parts.burst(J["head"][0], J["head"][1] + 40, 4, [(0.45, 0.25, 0.12), (0.6, 0.35, 0.18)], spd=500, life=0.7, size=(5, 10))
        parts.step_draw(cr, 1 / FPS)
        # 4-pack falls onto table
        if t >= T_darum:
            land = T_vier + 0.25
            yy = 1000 if t >= land else lerp(-300, 1000, ease((t - T_darum) / (land - T_darum)) ** 2)
            sq = 1 + 0.15 * math.sin(min(1, (t - land) / 0.3) * math.pi) if t >= land else 1
            draw_img(cr, stack, 860, yy, 280 / sq)
        cr.restore()
        hook(cr, "ICH WOLLTE NUR EIN STÜCK…", t, T_bei + 1.8)
        if T_also <= t < T_ich:
            outlined(cr, "(psst…)", W / 2, 320, 70, WHITE, BROWN, sw=10, scale=back((t - T_also) / 0.3))
        if T_nur <= t < T_ok:
            pill(cr, "NUR 1 STÜCK", W / 2, 300, 60, BROWN, scale=back((t - T_nur) / 0.3))
        if T_ok <= t < T_darum:
            n = 1 if t < T_und else 2
            pill(cr, f"TAFELN GEGESSEN: {n}", W / 2, 300, 58, RED, scale=1 + 0.15 * max(0, 1 - (t - (T_ok if n == 1 else T_und)) / 0.2))
        if T_darum <= t < T_tipp:
            pill(cr, "4ER-PACK", W / 2, 300, 72, RED, scale=back((t - T_vier) / 0.3), rot=-4)
        cta(cr, t, T_tipp, RED)

    def sfx(T):
        ev = [(0.0, "boing"), (2, "pop"), (8, "whoosh"), (13, "whoosh"), (17, "crunch"), (18, "pop"),
              (22, "whoosh"), (26, "pop"), (29, "whoosh"), (T[34] + 0.25, "boom"), (36, "ding")]
        tt = T[22] + 0.1
        while tt < T[29] - 0.1: ev.append((tt, "crunch")); tt += 0.3
        return ev
    render("3_schokoellsen", "schoko", cw, frame, sfx)

if __name__ == "__main__":
    which = sys.argv[1:] or ["d3", "levlup", "schoko"]
    for w_ in which: {"d3": video_d3, "levlup": video_levlup, "schoko": video_schoko}[w_]()
