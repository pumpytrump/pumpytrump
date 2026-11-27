"""Shared compositing for the 3D product videos: Blender frames + overlays + voice/SFX -> mp4.
A product comp.py builds a Cfg and calls run(cfg). COMP_TEST=1.0,6.0 -> stills."""
import glob, json, math, os, subprocess, sys
import cairo
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stick"))
from make import (outlined, pill, rrect, font, captions, sfx_track, write_wav, back, ease, Particles, surf_from_pil, draw_img, W, H, YEL, WHITE)

FPS, SRC_FPS = 30, 24
RED = (0.93, 0.16, 0.2); DARK = (0.12, 0.1, 0.12); GOLD1 = (1.0, 0.86, 0.3); GOLD2 = (0.85, 0.55, 0.05)

def gold_text(cr, text, x, y, size, scale=1.0, rot=0.0, c1=GOLD1, c2=GOLD2, mid=(1.0, 0.74, 0.15)):
    if scale <= 0.05: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(scale, scale)
    font(cr, size); e = cr.text_extents(text)
    if e.x_advance > 940: cr.scale(940 / e.x_advance, 940 / e.x_advance)
    cr.move_to(-e.x_advance / 2 + 8, size * 0.36 + 10); cr.text_path(text); cr.set_source_rgba(0, 0, 0, 0.45); cr.fill()
    cr.move_to(-e.x_advance / 2, size * 0.36); cr.text_path(text)
    cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.set_source_rgb(0.15, 0.08, 0.02); cr.set_line_width(size * 0.16); cr.stroke_preserve()
    g = cairo.LinearGradient(0, -size * 0.5, 0, size * 0.4)
    g.add_color_stop_rgb(0, *c1); g.add_color_stop_rgb(0.55, *mid); g.add_color_stop_rgb(1, *c2)
    cr.set_source(g); cr.fill(); cr.restore()

def badge(cr, t, txt, dot, t_end):
    k = back((t - 0.2) / 0.3)
    if k < 0.05 or t >= t_end: return
    cr.save(); cr.translate(60, 170); cr.scale(k, k)
    font(cr, 30); e = cr.text_extents(txt)
    rrect(cr, 0, -28, e.x_advance + 84, 56, 28); cr.set_source_rgba(1, 1, 1, 0.92); cr.fill()
    cr.arc(30, 0, 13, 0, 2 * math.pi); cr.set_source_rgb(*dot); cr.fill()
    cr.move_to(56, 11); cr.set_source_rgb(0.1, 0.1, 0.12); cr.show_text(txt); cr.restore()

def sticker(cr, x, y, k, lines, col=RED, rot=-10, r=120, fs=44):
    if k < 0.05: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(k, k)
    cr.arc(6, 10, r, 0, 2 * math.pi); cr.set_source_rgba(0, 0, 0, 0.25); cr.fill()
    cr.arc(0, 0, r, 0, 2 * math.pi); cr.set_source_rgb(*col); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(6); cr.stroke()
    n = len(lines)
    for i, txt in enumerate(lines):
        font(cr, fs); e = cr.text_extents(txt); cr.move_to(-e.x_advance / 2, fs * 0.35 + (i - (n - 1) / 2) * fs * 1.15)
        cr.set_source_rgb(1, 1, 1); cr.show_text(txt)
    cr.restore()

def red_arrow(cr, t, t0, x=150, y=1690):
    k = back((t - t0) / 0.3)
    if k < 0.05: return
    bob = 18 * math.sin((t - t0) * 9)
    cr.save(); cr.translate(x - bob * 0.7, y + bob); cr.rotate(math.radians(45)); cr.scale(k, k)
    cr.move_to(0, 110); cr.line_to(-80, 10); cr.line_to(-30, 10); cr.line_to(-30, -110); cr.line_to(30, -110)
    cr.line_to(30, 10); cr.line_to(80, 10); cr.close_path()
    cr.set_source_rgb(*RED); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(7); cr.stroke(); cr.restore()

def anchor_px(anc, key):
    if not anc or key not in anc: return None
    x, y, _ = anc[key]; return x * W, y * H

class Cfg:
    pass

def run(cfg):
    HERE = cfg.here; A = os.path.join(HERE, "assets"); OUT = os.path.join(HERE, "out")
    frames = sorted(glob.glob(os.path.join(OUT, "frames", "[0-9][0-9][0-9][0-9].png")))
    anchors = {}
    for f in glob.glob(os.path.join(OUT, "frames", "anchors_*.json")): anchors.update(json.load(open(f)))
    wj = json.load(open(os.path.join(A, "words.json")))
    assert len(cfg.captions) == len(wj), (len(cfg.captions), len(wj))
    words = []
    for c, (_, s_, e_) in zip(cfg.captions, wj):
        if c == "" and words: words[-1] = (words[-1][0], words[-1][1], e_)      # "" merges into previous word
        else: words.append((c, s_, e_))
    prod = surf_from_pil(Image.open(cfg.product_img))
    TL = cfg.TL; TOTAL = cfg.TOTAL

    def product_card(cr, t):
        k = back((t - TL["cta"] - 0.1) / 0.35)
        if k < 0.05: return
        cr.save(); cr.translate(330, 1250); cr.scale(k, k)
        rrect(cr, -290, -110, 600, 220, 26); cr.set_source_rgba(1, 1, 1, 0.97); cr.fill()
        draw_img(cr, prod, -215, 0, 190)
        font(cr, 38); cr.set_source_rgb(0.1, 0.1, 0.12); cr.move_to(-130, -40); cr.show_text(cfg.card_title)
        for i, ln in enumerate(cfg.card_lines):
            font(cr, 27); cr.set_source_rgb(0.35, 0.35, 0.4); cr.move_to(-130, 0 + 38 * i); cr.show_text(ln)
        font(cr, 27); cr.set_source_rgb(*RED); cr.move_to(-130, 80); cr.show_text("TIPP UNTEN LINKS")
        cr.restore()

    def end_card(cr, t):
        u = t - TL["end"]
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, *cfg.end_bg)
        cr.set_source(g); cr.paint()
        font(cr, 92); e = cr.text_extents(cfg.end_title); sc_ = min(1.0, 960 / e.x_advance)
        cr.save(); cr.translate(W / 2, 330); cr.scale(sc_, sc_); cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgb(0.1, 0.08, 0.1); cr.show_text(cfg.end_title); cr.restore()
        kk = back(u / 0.35)
        if kk > 0.05: draw_img(cr, prod, W / 2, 790, cfg.end_img_h * (1 + 0.04 * u) * kk)
        font(cr, 44); e = cr.text_extents(cfg.end_sub); sc_ = min(1.0, 980 / e.x_advance)
        cr.save(); cr.translate(W / 2, 1260); cr.scale(sc_, sc_); cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgb(0.3, 0.3, 0.35); cr.show_text(cfg.end_sub); cr.restore()
        font(cr, 52); txt = "TIPP UNTEN LINKS AUF DEN SHOP"; e = cr.text_extents(txt)
        cr.move_to(W / 2 - e.x_advance / 2, 1355); cr.set_source_rgb(*RED); cr.show_text(txt)
        if getattr(cfg, "end_note", None):
            font(cr, 30); e = cr.text_extents(cfg.end_note); cr.move_to(W / 2 - e.x_advance / 2, 1440); cr.set_source_rgb(0.45, 0.45, 0.5); cr.show_text(cfg.end_note)
        red_arrow(cr, t, TL["end"] + 0.2, 200, 1640)

    def draw_frame(cr, t, fi, conf, cache):
        if t >= TL["end"]:
            end_card(cr, t)
        else:
            si = min(int(t * SRC_FPS), len(frames) - 1)
            if si not in cache:
                cache.clear()
                im = Image.open(frames[si]).convert("RGBA").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 50, 2))
                cache[si] = surf_from_pil(im)
            cr.set_source_surface(cache[si], 0, 0); cr.paint()
            anc = anchors.get(str(si))
            badge(cr, t, cfg.badge, cfg.accent, TL["end"])
            cfg.overlays(cr, t, fi, conf, anc)
            conf.step_draw(cr, 1 / FPS)
            if t >= TL["cta"]:
                product_card(cr, t); red_arrow(cr, t, TL["cta"] + 0.25)
            captions(cr, words, t, y=1520)
        cr.rectangle(0, 0, W * t / TOTAL, 8); cr.set_source_rgb(*cfg.accent); cr.fill()

    if os.environ.get("COMP_TEST"):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); conf = Particles(11)
        for ts in os.environ["COMP_TEST"].split(","):
            t = float(ts); cr = cairo.Context(surf); draw_frame(cr, t, int(t * FPS), conf, {})
            surf.write_to_png(os.path.join(OUT, f"ctest_{t:05.2f}.png"))
        return
    fx = sfx_track(cfg.sfx, TOTAL + 1); write_wav(os.path.join(OUT, "sfx.wav"), fx)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    dst = os.path.join(OUT, cfg.outname)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(OUT, "sfx.wav"),
                           "-filter_complex", "[1:a]aresample=44100,apad[v];[2:a]volume=0.7[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                           "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst],
                          stdin=subprocess.PIPE)
    conf = Particles(11); cache = {}
    for fi in range(int(TOTAL * FPS)):
        cr = cairo.Context(surf); draw_frame(cr, fi / FPS, fi, conf, cache)
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait(); print("->", dst, f"{TOTAL:.1f}s")
