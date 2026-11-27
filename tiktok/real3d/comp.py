#!/usr/bin/env python3
"""Composite the Blender frames with overlays (reference style), voice + SFX -> out/7_schokoellsen_3d.mp4"""
import glob, json, math, os, subprocess, sys
import numpy as np, cairo
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "stick"))
from make import (outlined, pill, rrect, font, captions, sfx_track, write_wav, back, ease, win, lerp, clamp,
                  Particles, surf_from_pil, draw_img, W, H, YEL, WHITE)

A = os.path.join(HERE, "assets"); OUT = os.path.join(HERE, "out")
FPS, SRC_FPS = 30, 24
TL = dict(drawer=3.44, burst=4.55, wide=5.0, board=6.26, b2=7.06, buero=8.32, eat=10.06, clock=11.0,
          witz=12.36, bfd=13.96, cta=15.02, end=16.0)
TOTAL = 17.2
RED = (0.88, 0.1, 0.12); NAVY = (0.08, 0.12, 0.3); GOLD1 = (1.0, 0.86, 0.3); GOLD2 = (0.85, 0.55, 0.05)

frames = sorted(glob.glob(os.path.join(OUT, "frames", "[0-9][0-9][0-9][0-9].png")))
anchors = {}
for f in glob.glob(os.path.join(OUT, "frames", "anchors_*.json")): anchors.update(json.load(open(f)))
NSRC = len(frames)
bar_s = surf_from_pil(Image.open(os.path.join(A, "bar.png")))
stack_s = surf_from_pil(Image.open(os.path.join(A, "schoko.png")))

cw = ["Schokoellsen!", None, "Bei", "dieser", "Schokolade", "wird", "nicht", "gelogen!", "Schublade", "auf…", "und",
      "alles", "voll!", "Vier", "Tafeln,", "je", "70", "Gramm.", "Das", "reicht", "fürs", "ganze", "Büro…", "oder", "für",
      "mich", "allein", "bis", "zur", "Mittagspause.", "Und", "jetzt", "kein", "Witz:", "gerade", "im", "Black-",
      "Friday-", "Deal!", "Tipp", "unten", "links", "auf", "den", "Shop!"]
wj = json.load(open(os.path.join(A, "words.json")))
assert len(wj) == len(cw), (len(wj), len(cw))
words = []
for (w_, s, e), c in zip(wj, cw):
    if c is None: words[-1] = (words[-1][0], words[-1][1], e)
    else: words.append((c, s, e))

def gold_text(cr, text, x, y, size, scale=1.0, rot=0.0):
    """Big reference-style headline: gold gradient fill, thick dark outline, drop shadow."""
    if scale <= 0.01: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(scale, scale)
    font(cr, size); e = cr.text_extents(text)
    if e.x_advance > 940: cr.scale(940 / e.x_advance, 940 / e.x_advance)
    cr.move_to(-e.x_advance / 2 + 8, size * 0.36 + 10); cr.text_path(text); cr.set_source_rgba(0, 0, 0, 0.45); cr.fill()
    cr.move_to(-e.x_advance / 2, size * 0.36); cr.text_path(text)
    cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.set_source_rgb(0.15, 0.08, 0.02); cr.set_line_width(size * 0.16); cr.stroke_preserve()
    g = cairo.LinearGradient(0, -size * 0.5, 0, size * 0.4)
    g.add_color_stop_rgb(0, *GOLD1); g.add_color_stop_rgb(0.55, 1.0, 0.74, 0.15); g.add_color_stop_rgb(1, *GOLD2)
    cr.set_source(g); cr.fill(); cr.restore()

def badge(cr, t):
    k = back((t - 0.2) / 0.3)
    if k < 0.05 or t >= TL["end"]: return
    cr.save(); cr.translate(60, 170); cr.scale(k, k)
    font(cr, 30); txt = "SCHOKOELLSEN · 4 × 70 G"; e = cr.text_extents(txt)
    rrect(cr, 0, -28, e.x_advance + 84, 56, 28); cr.set_source_rgba(1, 1, 1, 0.92); cr.fill()
    cr.arc(30, 0, 13, 0, 2 * math.pi); cr.set_source_rgb(*RED); cr.fill()
    cr.move_to(56, 11); cr.set_source_rgb(0.1, 0.1, 0.12); cr.show_text(txt); cr.restore()

def board_space(cr, anc):
    sx, sy = W, H
    (x0, y0, _), (x1, y1, _), _, (x3, y3, _) = anc["board"]
    TLp, TRp, BLp = (x0 * sx, y0 * sy), (x1 * sx, y1 * sy), (x3 * sx, y3 * sy)
    cr.transform(cairo.Matrix((TRp[0] - TLp[0]) / 1000, (TRp[1] - TLp[1]) / 1000, (BLp[0] - TLp[0]) / 708,
                              (BLp[1] - TLp[1]) / 708, TLp[0], TLp[1]))

def board_overlay(cr, t, anc):
    if not anc: return
    in1 = TL["board"] <= t < TL["buero"]; in2 = TL["witz"] <= t < TL["cta"]
    if not (in1 or in2): return
    cr.save(); board_space(cr, anc)
    if in1:
        rrect(cr, 60, 50, 880, 120, 18); cr.set_source_rgb(*NAVY); cr.fill()
        font(cr, 74); cr.set_source_rgb(1, 1, 1); e = cr.text_extents("SCHOKOELLSEN"); cr.move_to(500 - e.x_advance / 2, 137); cr.show_text("SCHOKOELLSEN")
        for i, (txt, ts, col) in enumerate((("4 TAFELN", TL["board"] + 0.1, (0.9, 0.7, 0.1)), ("JE 70 GRAMM", TL["b2"], (0.15, 0.4, 0.85)),
                                             ("NICHT GELOGEN!", TL["b2"] + 0.6, (0.15, 0.65, 0.3)))):
            k = back((t - ts) / 0.25)
            if k < 0.05: continue
            y = 270 + i * 150
            cr.save(); cr.translate(110, y); cr.scale(k, k)
            cr.arc(0, 0, 26, 0, 2 * math.pi); cr.set_source_rgb(*col); cr.fill()
            font(cr, 78); cr.move_to(60, 28); cr.set_source_rgb(0.08, 0.1, 0.18); cr.show_text(txt); cr.restore()
    else:
        rrect(cr, 40, 40, 920, 140, 18); cr.set_source_rgb(*RED); cr.fill()
        font(cr, 72); txt = "UND JETZT KEIN WITZ"; e = cr.text_extents(txt)
        cr.move_to(500 - e.x_advance / 2, 135); cr.set_source_rgb(1, 1, 1); cr.show_text(txt)
        k = back((t - TL["bfd"]) / 0.3)
        if k > 0.05:
            cr.save(); cr.translate(500, 420); cr.scale(k, k)
            font(cr, 150); txt = "BLACK FRIDAY"; e = cr.text_extents(txt)
            if e.x_advance > 880: cr.scale(880 / e.x_advance, 880 / e.x_advance)
            cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgb(*RED); cr.show_text(txt)
            font(cr, 110); e = cr.text_extents("DEAL"); cr.move_to(-e.x_advance / 2, 150); cr.set_source_rgb(0.08, 0.08, 0.1); cr.show_text("DEAL")
            cr.restore()
        elif t > TL["witz"] + 0.4:   # little "loading" dots before the reveal
            for i in range(3):
                a = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * 8 - i))
                cr.arc(420 + i * 80, 420, 22, 0, 2 * math.pi); cr.set_source_rgba(0.3, 0.3, 0.35, a); cr.fill()
    cr.restore()

def product_card(cr, t):
    k = back((t - TL["cta"] - 0.1) / 0.35)
    if k < 0.05: return
    cr.save(); cr.translate(330, 1250); cr.scale(k, k)
    rrect(cr, -270, -95, 540, 190, 26); cr.set_source_rgba(1, 1, 1, 0.96); cr.fill()
    draw_img(cr, bar_s, -150, 0, 120)
    font(cr, 40); cr.set_source_rgb(0.1, 0.1, 0.12); cr.move_to(-30, -32); cr.show_text("SCHOKOELLSEN")
    font(cr, 28); cr.set_source_rgb(0.35, 0.35, 0.4); cr.move_to(-30, 8); cr.show_text("4 × 70 g · Black Friday")
    font(cr, 28); cr.set_source_rgb(*RED); cr.move_to(-30, 52); cr.show_text("TIPP UNTEN LINKS")
    cr.restore()

def red_arrow(cr, t, t0, x=150, y=1690):
    k = back((t - t0) / 0.3)
    if k < 0.05: return
    bob = 18 * math.sin((t - t0) * 9)
    cr.save(); cr.translate(x - bob * 0.7, y + bob); cr.rotate(math.radians(45)); cr.scale(k, k)
    cr.move_to(0, 110); cr.line_to(-80, 10); cr.line_to(-30, 10); cr.line_to(-30, -110); cr.line_to(30, -110)
    cr.line_to(30, 10); cr.line_to(80, 10); cr.close_path()
    cr.set_source_rgb(*RED); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(7); cr.stroke(); cr.restore()

def end_card(cr, t):
    u = t - TL["end"]
    cr.set_source_rgb(1, 1, 1); cr.paint()
    font(cr, 92); txt = "SCHOKOELLSEN"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 400); cr.set_source_rgb(0.08, 0.08, 0.1); cr.show_text(txt)
    z = 1 + 0.05 * u
    kk = back(u / 0.35)
    if kk > 0.05: draw_img(cr, stack_s, W / 2, 860, 640 * z * kk)
    font(cr, 40); txt = "4 × 70 g · Black-Friday-Deal"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 1260); cr.set_source_rgb(0.3, 0.3, 0.35); cr.show_text(txt)
    font(cr, 50); txt = "TIPP UNTEN LINKS AUF DEN SHOP"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 1350); cr.set_source_rgb(*RED); cr.show_text(txt)
    red_arrow(cr, t, TL["end"] + 0.2, 200, 1640)

def main():
    sfx = [(0.0, "boom"), (0.05, "tada"), (TL["drawer"], "whoosh"), (TL["drawer"] + 0.2, "whoosh"), (TL["burst"], "tada"),
           (TL["wide"], "whoosh"), (TL["board"], "whoosh"), (TL["board"] + 0.1, "pop"), (TL["b2"], "pop"), (TL["b2"] + 0.6, "pop"),
           (TL["buero"], "whoosh"), (TL["eat"], "whoosh"), (TL["clock"], "boing"), (TL["witz"], "whoosh"), (TL["bfd"], "ding"),
           (TL["bfd"], "boom"), (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")]
    tt = TL["eat"] + 0.3
    while tt < TL["eat"] + 1.4: sfx.append((tt, "crunch")); tt += 0.28
    fx = sfx_track(sfx, TOTAL + 1); write_wav(os.path.join(OUT, "sfx.wav"), fx)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    dst = os.path.join(OUT, "7_schokoellsen_3d.mp4")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(OUT, "sfx.wav"),
                           "-filter_complex", "[1:a]aresample=44100,apad[v];[2:a]volume=0.7[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                           "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst],
                          stdin=subprocess.PIPE)
    conf = Particles(11); cache = {}
    for fi in range(int(TOTAL * FPS)):
        t = fi / FPS
        cr = cairo.Context(surf)
        draw_frame(cr, t, fi, conf, cache)
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait(); print("->", dst, f"{TOTAL:.1f}s")

def draw_frame(cr, t, fi, conf, cache):
    if True:
        if t < TL["end"]:
            si = min(int(t * SRC_FPS), NSRC - 1)
            if si not in cache:
                cache.clear()
                im = Image.open(frames[si]).convert("RGBA").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
                cache[si] = surf_from_pil(im)
            cr.set_source_surface(cache[si], 0, 0); cr.paint()
            anc = anchors.get(str(si))
            board_overlay(cr, t, anc)
            badge(cr, t)
            if t < TL["drawer"]:
                gold_text(cr, "NICHT GELOGEN?!", W / 2, 360, 128, scale=back(t / 0.35) * (1 - ease((t - TL["drawer"] + 0.2) / 0.2)), rot=-3)
                outlined(cr, "BEI DIESER SCHOKOLADE", W / 2, 520, 64, WHITE, sw=12, scale=back((t - 0.25) / 0.3) * (1 - ease((t - TL["drawer"] + 0.2) / 0.2)))
            if fi == 1: conf.burst(W / 2, 700, 140, [(1, 0.85, 0.1), (1, 0.3, 0.4), (0.3, 0.8, 1), (0.5, 1, 0.4), (1, 1, 1)], spd=1600, life=2.0, size=(9, 16), grav=1300, kind="rect")
            if abs(t - TL["burst"] - 0.1) < 0.5 / FPS: conf.burst(W / 2, 900, 60, [(1, 0.85, 0.1), (1, 1, 1)], spd=1100, life=1.2, size=(6, 12), grav=1400, kind="rect")
            conf.step_draw(cr, 1 / FPS)
            if TL["wide"] <= t < TL["board"]:
                gold_text(cr, "ALLES VOLL!", W / 2, 330, 110, scale=back((t - TL["wide"]) / 0.3), rot=-2)
            if TL["buero"] <= t < TL["eat"]:
                pill(cr, "FÜRS GANZE BÜRO", W / 2, 330, 64, NAVY, scale=back((t - TL["buero"] - 0.5) / 0.3), rot=-2)
            if TL["eat"] <= t < TL["witz"]:
                pill(cr, "…ODER NUR FÜR MICH", W / 2, 330, 60, RED, scale=back((t - TL["eat"]) / 0.3), rot=-3)
                pill(cr, "BIS ZUR MITTAGSPAUSE", W / 2, 450, 50, NAVY, scale=back((t - TL["clock"]) / 0.3), rot=2)
            if t >= TL["cta"]:
                product_card(cr, t); red_arrow(cr, t, TL["cta"] + 0.25)
            captions(cr, words, t, y=1520)
        else:
            end_card(cr, t)
        cr.rectangle(0, 0, W * t / TOTAL, 8); cr.set_source_rgb(*RED); cr.fill()

if __name__ == "__main__":
    if os.environ.get("COMP_TEST"):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); conf = Particles(11)
        for ts in os.environ["COMP_TEST"].split(","):
            t = float(ts); cr = cairo.Context(surf); draw_frame(cr, t, int(t * FPS), conf, {})
            surf.write_to_png(os.path.join(OUT, f"ctest_{t:05.2f}.png"))
    else:
        main()
