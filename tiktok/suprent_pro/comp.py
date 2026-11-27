#!/usr/bin/env python3
"""Suprent Pro clipper -> out/11_suprent_pro_3d.mp4"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, WHITE

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(date=1.9, bart=4.12, trim=7.0, reveal=10.55, colors=13.05, cta=14.55, end=16.25)
ORANGE = (0.95, 0.45, 0.12); DARK = (0.08, 0.08, 0.1); BLUE = (0.15, 0.3, 0.6)

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["date"] + 0.15) / 0.2)
    gold_text(cr, "SUPRENT PRO", W / 2, 320, 120, scale=back(t / 0.35) * fade, rot=-3, c1=(1.0, 0.8, 0.45), mid=(1.0, 0.55, 0.15), c2=(0.8, 0.3, 0.05))
    outlined(cr, "Profi-Haarschneider", W / 2, 460, 60, WHITE, sw=12, scale=back((t - 0.5) / 0.3) * fade)
    if fi == 1: conf.burst(W / 2, 600, 110, [(1, 0.55, 0.1), (1, 1, 1), (0.6, 0.6, 0.65)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["date"] <= t < TL["bart"]:
        pill(cr, "FREITAG, 19:50", 300, 320, 54, BLUE, scale=back((t - T[3]) / 0.25), rot=-4)
        pill(cr, "DATE IN 10 MIN!", 760, 430, 58, (0.85, 0.15, 0.3), scale=back((t - T[4]) / 0.25), rot=4)
    if TL["bart"] <= t < TL["trim"]:
        gold_text(cr, "KATASTROPHE", W / 2, 330, 110, scale=back((t - T[11]) / 0.3), rot=-3, c1=(1, 0.6, 0.6), mid=(0.95, 0.25, 0.2), c2=(0.6, 0.05, 0.05))
    if TL["trim"] <= t < TL["reveal"]:
        for i, (txt, ti, x, y, r) in enumerate((("KERAMIKKLINGE", 12, 320, 300, -4), ("KABELLOS", 13, 790, 400, 4), ("ZERO-GAP-KONTUR", 14, W / 2, 510, -2))):
            pill(cr, txt, x, y, 50, DARK if i < 2 else ORANGE, scale=back((t - T[ti]) / 0.25), rot=r)
    if TL["reveal"] <= t < TL["colors"]:
        if t < T[22]:
            outlined(cr, "10 MINUTEN?", W / 2, 330, 90, WHITE, sw=14, scale=back((t - T[20]) / 0.3))
        else:
            gold_text(cr, "NUR 5 GEBRAUCHT!", W / 2, 330, 104, scale=back((t - T[22]) / 0.3), rot=-2)
            if abs(t - T[22]) < 0.02: conf.burst(W / 2, 420, 70, [(1, 0.85, 0.2), (1, 1, 1)], spd=1300, life=1.4, size=(8, 14), grav=1200, kind="rect")
    if TL["colors"] <= t < TL["cta"]:
        a = C.anchor_px(anc, "clipper"); b = C.anchor_px(anc, "silver")
        if b: pill(cr, "SILBER", min(max(b[0], 170), W - 170), max(b[1] - 200, 260), 50, (0.45, 0.47, 0.52), scale=back((t - T[29]) / 0.25), rot=-3)
        if a: pill(cr, "ORANGE", min(max(a[0], 170), W - 170), max(a[1] - 200, 260), 50, ORANGE, scale=back((t - T[31]) / 0.25), rot=3)

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.25; cfg.outname = "11_suprent_pro_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "SUPRENT · PRO HAARSCHNEIDER"; cfg.accent = ORANGE
cfg.card_title = "SUPRENT PRO"; cfg.card_lines = ["Keramikklinge · kabellos", "Silber oder Orange"]
cfg.end_title = "SUPRENT PRO"; cfg.end_sub = "Keramikklinge · kabellos · Zero-Gap"; cfg.end_bg = (1.0, 0.93, 0.85); cfg.end_img_h = 760
cfg.captions = ["Suprent", "Pro", "Haarschneider!", "Freitagabend.", "Date", "in", "10", "Minuten.", "Und", "mein", "Bart?", "Katastrophe.",
                "Keramikklinge.", "Kabellos.", "Zero", "-Gap", "für", "die", "perfekte", "Kontur.", "10", "Minuten?", "Ich", "hab", "nur",
                "fünf", "gebraucht!", "Gibt's", "in", "Silber", "oder", "Orange.", "Tipp", "unten", "links", "und", "hol", "ihn", "dir!"]
cfg.overlays = overlays
cfg.deal = "BLACK FRIDAY: -12 % → 99,99 €"
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (0.6, "buzz"), (TL["date"], "whoosh"), (T[3], "pop"), (T[4], "pop"), (T[11], "boing"), (T[11], "crack"),
            (T[12], "pop"), (T[13], "pop"), (T[14], "pop")] + [(TL["trim"] + 0.85 * i, "buzz") for i in range(4)] +
           [(T[20], "whoosh"), (T[22], "tada"), (T[22], "ding"), (TL["colors"], "whoosh"), (T[29], "pop"), (T[31], "pop"),
            (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
