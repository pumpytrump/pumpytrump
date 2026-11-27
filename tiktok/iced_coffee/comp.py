#!/usr/bin/env python3
"""More Protein Iced Coffee -> out/13_more_iced_coffee_3d.mp4"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, WHITE

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(intro=1.75, yes=4.6, powder=5.65, milk=6.45, ice=7.2, shake=7.95, pour=8.6, sip=9.3, barista=12.15, cta=14.65, end=16.25)
PURPLE = (0.55, 0.2, 0.55); BROWN = (0.42, 0.24, 0.12); GREEN = (0.45, 0.65, 0.2); DARK = (0.08, 0.08, 0.1)

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["intro"] + 0.15) / 0.2)
    gold_text(cr, "PROTEIN ICED COFFEE", W / 2, 320, 104, scale=back(t / 0.35) * fade, rot=-3)
    outlined(cr, "von More Nutrition", W / 2, 455, 60, WHITE, sw=12, scale=back((t - 0.5) / 0.3) * fade)
    if fi == 1: conf.burst(W / 2, 600, 110, [(0.55, 0.2, 0.55), (1, 1, 1), (0.45, 0.65, 0.2)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["intro"] <= t < TL["powder"]:
        sticker(cr, 820, 360, back((t - T[8]) / 0.3), ["~20 G", "PROTEIN"], col=PURPLE, rot=-10, r=125, fs=46)
        outlined(cr, "pro Portion", 820, 520, 46, WHITE, sw=10, scale=back((t - T[11]) / 0.3))
        if t >= T[12]: gold_text(cr, "JA, BITTE!", 340, 330, 100, scale=back((t - T[12]) / 0.3), rot=-4)
    steps = (("PULVER REIN", TL["powder"], BROWN), ("MILCH DRAUF", TL["milk"], (0.2, 0.45, 0.85)), ("EIS DAZU", TL["ice"], (0.3, 0.7, 0.9)),
             ("SHAKEN!", TL["shake"], PURPLE), ("FERTIG!", TL["pour"], GREEN))
    for i, (txt, ts, col) in enumerate(steps):
        te = steps[i + 1][1] if i + 1 < len(steps) else TL["sip"]
        if ts <= t < te:
            pill(cr, f"{i + 1}. {txt}", W / 2, 320, 70, col, scale=back((t - ts) / 0.2), rot=(-3, 3)[i % 2])
    if TL["sip"] <= t < TL["barista"]:
        pill(cr, "ECHTER KAFFEE", 320, 300, 56, BROWN, scale=back((t - T[22]) / 0.25), rot=-4)
        if t >= T[24]: sticker(cr, 820, 400, back((t - T[24]) / 0.3), ["SORTEN", "WÄHLBAR"], col=(0.9, 0.2, 0.2), rot=-10)
    if TL["barista"] <= t < TL["cta"]:
        outlined(cr, "BARISTA:", W / 2, 300, 80, WHITE, sw=13, scale=back((t - T[31]) / 0.3))
        gold_text(cr, "ARBEITSLOS", W / 2, 420, 110, scale=back((t - T[35]) / 0.3), rot=-3, c1=(1, 0.6, 0.6), mid=(0.95, 0.25, 0.2), c2=(0.6, 0.05, 0.05))

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.25; cfg.outname = "13_more_iced_coffee_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "MORE NUTRITION · PROTEIN ICED COFFEE"; cfg.accent = PURPLE
cfg.card_title = "MORE ICED COFFEE"; cfg.card_lines = ["Protein · echter Kaffee", "Sorten wählbar"]
cfg.end_title = "MORE PROTEIN ICED COFFEE"; cfg.end_sub = "Protein-Eiskaffee · echter Kaffee · Sorten wählbar"; cfg.end_bg = (0.96, 0.9, 0.98); cfg.end_img_h = 720
cfg.captions = ["More", "Protein", "Iced", "Coffee!", "Eiskaffee", "", "mit", "fast", "20", "Gramm", "Protein", "pro Portion?", "Ja,", "bitte!",
                "Pulver", "rein,", "Milch", "drauf,", "Eis", "dazu,", "shaken,", "fertig!", "Echter", "Kaffee,", "und", "die", "Sorte",
                "kannst", "du", "wählen!", "Mein", "Barista", "ist", "jetzt", "offiziell", "arbeitslos!", "Tipp", "unten", "links", "und", "hol's", "dir!"]
cfg.overlays = overlays
cfg.deal = "BLACK FRIDAY DEAL IM SHOP"
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (TL["intro"], "whoosh"), (T[8], "pop"), (T[12], "tada"), (TL["powder"], "whoosh"), (TL["powder"] + 0.45, "crunch"),
            (TL["milk"], "whoosh"), (TL["milk"] + 0.3, "gulp"), (TL["ice"], "pop")] + [(TL["ice"] + 0.15 + 0.08 * i, "crack") for i in range(4)] +
           [(TL["shake"] + 0.07 * i, "crunch") for i in range(9)] + [(TL["pour"], "ding"), (TL["pour"] + 0.2, "gulp"), (TL["sip"] + 0.5, "gulp"),
            (T[22], "pop"), (T[24], "pop"), (T[31], "boing"), (TL["barista"] + 0.7, "buzz"), (T[35], "crack"),
            (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
