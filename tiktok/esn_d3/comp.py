#!/usr/bin/env python3
"""Composite ESN D3+K2 Blender frames + overlays + voice/SFX -> out/9_esn_d3k2_3d.mp4
COMP_TEST=1.0,6.0 python3 comp.py   -> still previews"""
import glob, json, math, os, subprocess, sys
import cairo
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "stick"))
from make import (outlined, pill, rrect, font, captions, sfx_track, write_wav, back, ease, Particles, surf_from_pil, draw_img, W, H, YEL, WHITE)

A = os.path.join(HERE, "assets"); OUT = os.path.join(HERE, "out")
FPS, SRC_FPS = 30, 24
wj = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in wj]
TL = dict(winter=2.72, ghost=6.24, capsule=8.46, sun=10.1, k120=13.6, cta=15.28, end=16.42)
TOTAL = 17.5
RED = (0.93, 0.16, 0.2); PINK = (0.96, 0.7, 0.12); DARK = (0.12, 0.1, 0.12); GOLD1 = (1.0, 0.86, 0.3); GOLD2 = (0.85, 0.55, 0.05)
frames = sorted(glob.glob(os.path.join(OUT, "frames", "[0-9][0-9][0-9][0-9].png")))
anchors = {}
for f in glob.glob(os.path.join(OUT, "frames", "anchors_*.json")): anchors.update(json.load(open(f)))
NSRC = len(frames)
bottle_s = surf_from_pil(Image.open(os.path.join(A, "bottle.png")))

cw = ["ESN", "Vitamin", "D3", "plus", "K2", "Depot!", "Deutschland", "im", "Winter:", "grau,", "nass,", "null", "Sonne.",
      "Ich", "seh", "schon", "aus", "wie", "ein", "Gespenst.", "Also:", "eine", "Kapsel.", "Vitamin", "D", "trägt", "zur",
      "normalen", "Funktion", "des", "Immunsystems", "und", "der", "Muskeln", "bei.", "120", "Kapseln", "pro", "Dose.",
      "Tipp", "unten", "links", "auf", "den", "Shop!"]
assert len(cw) == len(wj), (len(cw), len(wj))
words = [(c, s, e) for c, (_, s, e) in zip(cw, wj)]

def gold_text(cr, text, x, y, size, scale=1.0, rot=0.0):
    if scale <= 0.05: return
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
    font(cr, 30); txt = "ESN · VITAMIN D3+K2 DEPOT"; e = cr.text_extents(txt)
    rrect(cr, 0, -28, e.x_advance + 84, 56, 28); cr.set_source_rgba(1, 1, 1, 0.92); cr.fill()
    cr.arc(30, 0, 13, 0, 2 * math.pi); cr.set_source_rgb(*PINK); cr.fill()
    cr.move_to(56, 11); cr.set_source_rgb(0.1, 0.1, 0.12); cr.show_text(txt); cr.restore()

def sticker(cr, x, y, k, rot=-10):
    """round red 'SORTEN WÄHLBAR' sticker like on the product photo"""
    if k < 0.05: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(k, k)
    cr.arc(6, 10, 120, 0, 2 * math.pi); cr.set_source_rgba(0, 0, 0, 0.25); cr.fill()
    cr.arc(0, 0, 120, 0, 2 * math.pi); cr.set_source_rgb(*RED); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(6); cr.stroke()
    for i, txt in enumerate(("SORTEN", "WÄHLBAR")):
        font(cr, 44); e = cr.text_extents(txt); cr.move_to(-e.x_advance / 2, -6 + i * 52); cr.set_source_rgb(1, 1, 1); cr.show_text(txt)
    cr.restore()

def anchor_px(anc, key):
    x, y, _ = anc[key]; return x * W, y * H

def product_card(cr, t):
    k = back((t - TL["cta"] - 0.1) / 0.35)
    if k < 0.05: return
    cr.save(); cr.translate(330, 1250); cr.scale(k, k)
    rrect(cr, -290, -110, 600, 220, 26); cr.set_source_rgba(1, 1, 1, 0.97); cr.fill()
    draw_img(cr, bottle_s, -215, 0, 190)
    font(cr, 40); cr.set_source_rgb(0.1, 0.1, 0.12); cr.move_to(-130, -40); cr.show_text("ESN D3+K2 DEPOT")
    font(cr, 27); cr.set_source_rgb(0.35, 0.35, 0.4); cr.move_to(-130, 0); cr.show_text("5.600 I.E. D3 · 200 µg K2")
    font(cr, 27); cr.set_source_rgb(0.35, 0.35, 0.4); cr.move_to(-130, 38); cr.show_text("120 Kapseln")
    font(cr, 27); cr.set_source_rgb(*RED); cr.move_to(-130, 80); cr.show_text("TIPP UNTEN LINKS")
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
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, 1, 0.96, 0.86)
    cr.set_source(g); cr.paint()
    font(cr, 96); txt = "ESN D3+K2 DEPOT"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 330); cr.set_source_rgb(0.1, 0.08, 0.1); cr.show_text(txt)
    kk = back(u / 0.35)
    if kk > 0.05: draw_img(cr, bottle_s, W / 2, 790, 720 * (1 + 0.04 * u) * kk)
    font(cr, 44); txt = "5.600 I.E. D3 · 200 µg K2 · 120 Kapseln"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 1260); cr.set_source_rgb(0.3, 0.3, 0.35); cr.show_text(txt)
    font(cr, 52); txt = "TIPP UNTEN LINKS AUF DEN SHOP"; e = cr.text_extents(txt)
    cr.move_to(W / 2 - e.x_advance / 2, 1355); cr.set_source_rgb(*RED); cr.show_text(txt)
    red_arrow(cr, t, TL["end"] + 0.2, 200, 1640)

def draw_frame(cr, t, fi, conf, cache):
    if t >= TL["end"]:
        end_card(cr, t)
    else:
        si = min(int(t * SRC_FPS), NSRC - 1)
        if si not in cache:
            cache.clear()
            im = Image.open(frames[si]).convert("RGBA").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 50, 2))
            cache[si] = surf_from_pil(im)
        cr.set_source_surface(cache[si], 0, 0); cr.paint()
        anc = anchors.get(str(si))
        badge(cr, t)
        fade = 1 - ease((t - TL["winter"] + 0.15) / 0.2)
        gold_text(cr, "WINTER-BLASS?", W / 2, 330, 120, scale=back(t / 0.35) * fade, rot=-3)
        outlined(cr, "Sonne zum Mitnehmen.", W / 2, 470, 60, WHITE, sw=12, scale=back((t - 0.4) / 0.3) * fade)
        if fi == 1: conf.burst(W / 2, 600, 120, [(1, 0.8, 0.1), (1, 1, 1), (0.95, 0.65, 0.1)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
        conf.step_draw(cr, 1 / FPS)
        if TL["winter"] <= t < TL["ghost"]:
            for i, (txt, ts, col, x, rot) in enumerate((("GRAU", T[9], (0.45, 0.47, 0.52), 260, -5), ("NASS", T[10], (0.2, 0.45, 0.8), 540, 4), ("NULL SONNE", T[11], (0.18, 0.18, 0.22), 800, -3))):
                pill(cr, txt, x, (300, 410, 300)[i], 58, col, scale=back((t - ts) / 0.25), rot=rot)
        if TL["ghost"] <= t < TL["capsule"]:
            outlined(cr, "*wird zum Gespenst*", W / 2, 330, 72, (0.85, 0.87, 0.9), sw=12, scale=back((t - TL["ghost"] - 0.2) / 0.3))
        if TL["capsule"] <= t < TL["sun"]:
            pill(cr, "1 KAPSEL", W / 2, 300, 66, (0.12, 0.12, 0.14), scale=back((t - TL["capsule"]) / 0.25), rot=-3)
            pill(cr, "5.600 I.E. D3 + 200 µg K2", W / 2, 415, 46, PINK, scale=back((t - TL["capsule"] - 0.3) / 0.25), rot=2)
        if TL["sun"] <= t < TL["k120"]:
            gold_text(cr, "SONNE AN!", W / 2, 320, 120, scale=back((t - TL["sun"]) / 0.3), rot=-2)
            pill(cr, "NORMALE IMMUNFUNKTION", W / 2, 460, 50, (0.15, 0.5, 0.3), scale=back((t - T[30]) / 0.25), rot=-2)
            pill(cr, "NORMALE MUSKELFUNKTION", W / 2, 565, 50, (0.15, 0.4, 0.7), scale=back((t - T[33]) / 0.25), rot=2)
        if TL["k120"] <= t < TL["cta"]:
            gold_text(cr, "120 KAPSELN", W / 2, 330, 118, scale=back((t - TL["k120"]) / 0.3), rot=-3)
        if t >= TL["cta"]:
            product_card(cr, t); red_arrow(cr, t, TL["cta"] + 0.25)
        captions(cr, words, t, y=1520)
    cr.rectangle(0, 0, W * t / TOTAL, 8); cr.set_source_rgb(*PINK); cr.fill()

def main():
    sfx = [(0.0, "boom"), (0.05, "tada"), (TL["winter"], "whoosh"), (T[9], "pop"), (T[10], "pop"), (T[11], "pop"),
           (TL["ghost"], "whoosh"), (TL["ghost"] + 0.3, "boing"), (TL["capsule"], "whoosh"), (TL["capsule"] + 0.3, "pop"),
           (TL["capsule"] + 0.85, "pop"), (TL["capsule"] + 1.3, "gulp"), (TL["capsule"] + 1.65, "gulp"), (TL["sun"], "tada"),
           (TL["sun"], "boom"), (T[30], "pop"), (T[33], "pop"), (TL["k120"], "whoosh")] + [(TL["k120"] + 0.1 + i * 0.12, "crunch") for i in range(8)] + [
           (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")]
    fx = sfx_track(sfx, TOTAL + 1); write_wav(os.path.join(OUT, "sfx.wav"), fx)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    dst = os.path.join(OUT, "9_esn_d3k2_3d.mp4")
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

if __name__ == "__main__":
    if os.environ.get("COMP_TEST"):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); conf = Particles(11)
        for ts in os.environ["COMP_TEST"].split(","):
            t = float(ts); cr = cairo.Context(surf); draw_frame(cr, t, int(t * FPS), conf, {})
            surf.write_to_png(os.path.join(OUT, f"ctest_{t:05.2f}.png"))
    else:
        main()
