#!/usr/bin/env python3
"""Suprent FANGS -> out/10_suprent_fangs_3d.mp4   (COMP_TEST=1.0,6.0 python3 comp.py for stills)"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, WHITE

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(barber=3.3, self=5.0, thick=6.65, cut=7.6, zack=9.12, ki=10.75, colors=13.0, cta=14.62, end=16.3)
GREEN = (0.2, 0.85, 0.25); PINK = (0.95, 0.35, 0.65); DARK = (0.08, 0.08, 0.1)

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["barber"] + 0.15) / 0.2)
    gold_text(cr, "SUPRENT FANGS", W / 2, 320, 118, scale=back(t / 0.35) * fade, rot=-3, c1=(0.75, 1.0, 0.5), mid=(0.3, 0.95, 0.3), c2=(0.1, 0.6, 0.15))
    if T[2] - 0.05 <= t < TL["barber"]:
        pill(cr, "13.000 U/MIN", W / 2, 470, 64, DARK, scale=back((t - T[2]) / 0.25) * fade, rot=2)
    if fi == 1: conf.burst(W / 2, 600, 110, [(0.3, 1, 0.3), (1, 1, 1), (0.1, 0.1, 0.1)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["barber"] <= t < TL["self"]:
        pill(cr, "BARBER IM URLAUB", W / 2, 330, 56, (0.85, 0.3, 0.15), scale=back((t - T[6]) / 0.25), rot=-3)
    if TL["self"] <= t < TL["thick"]:
        outlined(cr, "DIY-MODUS: AN", W / 2, 330, 80, GREEN, sw=13, scale=back((t - T[9]) / 0.3))
    if TL["thick"] <= t < TL["zack"]:
        pill(cr, "KEIN ZIEPEN", 290, 320, 56, DARK, scale=back((t - T[16]) / 0.25), rot=-4)
        pill(cr, "KEIN ZERREN", 780, 430, 56, DARK, scale=back((t - T[18]) / 0.25), rot=4)
    if TL["zack"] <= t < TL["ki"]:
        gold_text(cr, "SAUBERER FADE!", W / 2, 330, 112, scale=back((t - TL["zack"]) / 0.3), rot=-2)
        if abs(t - TL["zack"]) < 0.02: conf.burst(W / 2, 420, 70, [(1, 0.85, 0.2), (1, 1, 1)], spd=1300, life=1.4, size=(8, 14), grav=1200, kind="rect")
    if TL["ki"] <= t < TL["colors"]:
        pill(cr, "KI-POWER-ANPASSUNG", W / 2, 320, 58, (0.1, 0.55, 0.2), scale=back((t - TL["ki"]) / 0.25), rot=-2)
        pill(cr, "FÜR JEDEN HAARTYP", W / 2, 430, 50, DARK, scale=back((t - T[27]) / 0.25), rot=2)
    if TL["colors"] <= t < TL["cta"]:
        a = C.anchor_px(anc, "clipper"); b = C.anchor_px(anc, "pink")
        if a: pill(cr, "SCHWARZ-GRÜN", min(max(a[0], 230), W - 230), max(a[1] - 200, 260), 46, (0.1, 0.55, 0.2), scale=back((t - T[31]) / 0.25), rot=3)
        if b: pill(cr, "PINK", min(max(b[0], 150), W - 150), max(b[1] - 200, 260), 46, PINK, scale=back((t - T[34]) / 0.25), rot=-3)
    if TL["colors"] <= t < TL["end"]:
        pass

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.3; cfg.outname = "10_suprent_fangs_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "SUPRENT · FANGS VECTOR CLIPPER"; cfg.accent = GREEN
cfg.card_title = "SUPRENT FANGS"; cfg.card_lines = ["13.000 U/min · KI-Motor", "Schwarz-Grün oder Pink"]
cfg.end_title = "SUPRENT FANGS"; cfg.end_sub = "13.000 U/min · KI-Power · 2 Farben"; cfg.end_bg = (0.88, 1.0, 0.9); cfg.end_img_h = 760
cfg.captions = ["Suprent", "FANGS!", "13.000", "", "Umdrehungen!", "Mein", "Barber", "hat", "Urlaub…", "also", "mach", "ich's", "halt",
                "selbst.", "Dicke", "Haare?", "Kein", "Ziepen,", "kein", "Zerren.", "Zack,", "sauberer", "Fade!", "Die", "KI", "passt",
                "die", "Power", "automatisch", "an.", "In", "Schwarz", "-Grün", "oder", "Pink.", "Tipp", "unten", "links", "und", "hol", "ihn", "dir!"]
cfg.overlays = overlays
cfg.deal = "BLACK FRIDAY: -11 % → 169,99 €"
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (T[2], "whoosh"), (1.5, "buzz"), (TL["barber"], "whoosh"), (T[6], "pop"), (TL["self"] + 0.4, "whoosh"),
            (T[9], "pop"), (T[16], "pop"), (T[18], "pop")] + [(TL["cut"] + 0.38 * i, "buzz") for i in range(4)] +
           [(TL["zack"], "tada"), (TL["zack"], "ding"), (TL["ki"], "whoosh"), (TL["ki"] + 0.1, "pop"), (T[27], "pop"), (TL["colors"], "whoosh"),
            (T[31], "pop"), (T[34], "pop"), (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
