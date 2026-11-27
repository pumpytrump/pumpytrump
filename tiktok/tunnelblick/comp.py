#!/usr/bin/env python3
"""FGN Tunnelblick -> out/12_fgn_tunnelblick_3d.mp4"""
import json, math, os, sys
import cairo
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, H, WHITE, font

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(tired=1.95, coffee=5.95, pouch=7.3, facts=8.9, zack=12.7, cta=14.5, end=16.15)
MINT = (0.3, 0.8, 0.62); PINK = (0.93, 0.42, 0.52); DARK = (0.08, 0.08, 0.1)

def tunnel(cr, t):
    k = ease((t - TL["zack"]) / 0.25) * (1 - ease((t - TL["cta"] + 0.2) / 0.3))
    if k <= 0.01: return
    g = cairo.RadialGradient(W / 2, H * 0.4, 260, W / 2, H * 0.4, 1100)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.85 * k)
    cr.set_source(g); cr.paint()
    cr.set_line_width(5)
    for i in range(28):
        a = i * 2 * math.pi / 28 + t * 0.6; r0 = 420 + 140 * ((t * 3 + i * 0.37) % 1)
        cr.move_to(W / 2 + r0 * math.cos(a), H * 0.4 + r0 * math.sin(a)); cr.line_to(W / 2 + 1400 * math.cos(a), H * 0.4 + 1400 * math.sin(a))
        cr.set_source_rgba(1, 1, 1, 0.22 * k); cr.stroke()

def overlays(cr, t, fi, conf, anc):
    tunnel(cr, t)
    fade = 1 - ease((t - TL["tired"] + 0.15) / 0.2)
    gold_text(cr, "TUNNELBLICK", W / 2, 320, 120, scale=back(t / 0.35) * fade, rot=-3, c1=(0.75, 1.0, 0.9), mid=(0.35, 0.85, 0.65), c2=(0.1, 0.5, 0.4))
    outlined(cr, "von FGN", W / 2, 460, 62, WHITE, sw=12, scale=back((t - 0.5) / 0.3) * fade)
    if fi == 1: conf.burst(W / 2, 600, 110, [(0.95, 0.45, 0.55), (1, 1, 1), (0.35, 0.85, 0.65)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["tired"] <= t < TL["coffee"]:
        pill(cr, "MONTAG", 300, 320, 58, DARK, scale=back((t - T[2]) / 0.25), rot=-4)
        pill(cr, "DEADLINE", 760, 430, 58, (0.85, 0.15, 0.2), scale=back((t - T[3]) / 0.25), rot=4)
        outlined(cr, "AKKU: 3 %", W / 2, 560, 64, (1, 0.35, 0.3), sw=12, scale=back((t - T[4]) / 0.3))
    if TL["coffee"] <= t < TL["pouch"]:
        outlined(cr, "KAFFEE NR. 5?", W / 2, 340, 84, WHITE, sw=13, scale=back((t - T[10]) / 0.3))
        outlined(cr, "NÖ.", W / 2, 460, 90, (1, 0.4, 0.35), sw=13, scale=back((t - T[13] - 0.2) / 0.3))
    if TL["pouch"] <= t < TL["facts"]:
        pill(cr, "POUCH UNTER DIE LIPPE", W / 2, 330, 52, MINT, scale=back((t - T[15]) / 0.25), rot=-2)
    if TL["facts"] <= t < TL["zack"]:
        for txt, ti, y, col, r in (("75 MG KOFFEIN", 19, 300, DARK, -3), ("0 NIKOTIN", 22, 410, MINT, 3), ("0 ZUCKER", 24, 520, PINK, -2)):
            pill(cr, txt, W / 2, y, 60, col, scale=back((t - T[ti]) / 0.25), rot=r)
    if TL["zack"] <= t < TL["cta"]:
        gold_text(cr, "TUNNELBLICK!", W / 2, 330, 116, scale=back((t - T[27]) / 0.3), rot=-2, c1=(0.75, 1.0, 0.9), mid=(0.35, 0.85, 0.65), c2=(0.1, 0.5, 0.4))
        if abs(t - T[27]) < 0.02: conf.burst(W / 2, 420, 70, [(0.35, 0.85, 0.65), (1, 1, 1)], spd=1300, life=1.4, size=(8, 14), grav=1200, kind="rect")
    if t < TL["end"]:
        font(cr, 26); txt = "Erhöhter Koffeingehalt. Für Kinder und Schwangere nicht empfohlen."; e = cr.text_extents(txt)
        cr.move_to(W / 2 - e.x_advance / 2, 1880); cr.set_source_rgba(1, 1, 1, 0.85); cr.show_text(txt)

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.15; cfg.outname = "12_fgn_tunnelblick_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "can.png")
cfg.badge = "FGN · TUNNELBLICK KOFFEIN-POUCHES"; cfg.accent = MINT
cfg.card_title = "FGN TUNNELBLICK"; cfg.card_lines = ["75 mg Koffein pro Pouch", "0 Nikotin · 0 Zucker"]
cfg.end_title = "FGN TUNNELBLICK"; cfg.end_sub = "75 mg Koffein · 0 Nikotin · 0 Zucker"; cfg.end_bg = (0.88, 0.97, 0.93); cfg.end_img_h = 640
cfg.end_note = "Erhöhter Koffeingehalt. Für Kinder und Schwangere nicht empfohlen."
cfg.captions = ["FGN", "Tunnelblick!", "Montag,", "Deadline…", "meine", "Augen", "sind", "auf", "halb", "acht.", "Statt", "dem", "fünften",
                "Kaffee:", "ein", "Pouch", "unter", "die", "Lippe.", "75", "Milligramm", "Koffein,", "null", "Nikotin,", "null", "Zucker.",
                "Und", "zack:", "Tunnelblick!", "Tipp", "unten", "links", "und", "hol's", "dir!"]
cfg.overlays = overlays
cfg.deal = "BLACK FRIDAY DEAL IM SHOP"
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (0.7, "pop"), (TL["tired"], "whoosh"), (T[2], "pop"), (T[3], "pop"), (T[4], "boing"),
            (TL["coffee"], "whoosh"), (T[13] + 0.2, "crack"), (TL["pouch"], "pop"), (TL["pouch"] + 0.4, "pop"), (T[19], "pop"), (T[22], "pop"),
            (T[24], "pop"), (T[27], "boom"), (T[27], "whoosh"), (T[28], "tada")] + [(TL["zack"] + 0.3 + 0.09 * i, "crunch") for i in range(14)] +
           [(TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
