#!/usr/bin/env python3
"""Elusa 501 -> out/15_elusa_501_3d.mp4"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, WHITE

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(spray=2.1, notes=3.9, market=7.25, deal=10.25, cta=13.2, end=15.25)
ORANGE = (0.95, 0.5, 0.1); VAN = (0.45, 0.3, 0.15); SPICE = (0.6, 0.2, 0.1); RED = (0.85, 0.12, 0.15); GREEN = (0.15, 0.45, 0.25)

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["spray"] + 0.15) / 0.2)
    gold_text(cr, "ELUSA 501", W / 2, 320, 124, scale=back(t / 0.35) * fade, rot=-3)
    outlined(cr, "Extrait de Parfum · Unisex", W / 2, 460, 56, WHITE, sw=12, scale=back((t - 0.6) / 0.3) * fade)
    if fi == 1: conf.burst(W / 2, 600, 110, [(1, 0.8, 0.3), (1, 1, 1), (0.95, 0.5, 0.1)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["spray"] <= t < TL["notes"]:
        pill(cr, "UNISEX", W / 2, 320, 66, GREEN, scale=back((t - T[3]) / 0.25), rot=-3)
    if TL["notes"] <= t < TL["market"]:
        pill(cr, "SÜSS", W / 2, 290, 60, (0.85, 0.4, 0.55), scale=back((t - T[4]) / 0.25), rot=-3)
        for txt, ti, x, y, col, r in (("ORANGE", 6, 260, 400, ORANGE, -4), ("VANILLE", 7, 540, 470, VAN, 3), ("GEWÜRZE", 9, 820, 400, SPICE, -3)):
            pill(cr, txt, x, y, 48, col, scale=back((t - T[ti]) / 0.25), rot=r)
    if TL["market"] <= t < TL["deal"]:
        outlined(cr, "RIECHT WIE", W / 2, 290, 70, WHITE, sw=12, scale=back((t - T[10]) / 0.3))
        gold_text(cr, "WEIHNACHTSMARKT", W / 2, 400, 100, scale=back((t - T[12]) / 0.3), rot=-2)
        if t >= T[13]: pill(cr, "…NUR EDEL", W / 2, 530, 56, (0.12, 0.1, 0.1), scale=back((t - T[13]) / 0.25), rot=3)
    if TL["deal"] <= t < TL["cta"]:
        sticker(cr, W / 2, 380, back((t - T[18]) / 0.3), ["KAUF 3", "SPAR 46 %"], col=RED, rot=-8, r=170, fs=50)
        outlined(cr, "gerade im Shop", W / 2, 600, 50, WHITE, sw=11, scale=back((t - T[20]) / 0.3))

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 16.3; cfg.outname = "15_elusa_501_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "ELUSA · 501 EXTRAIT DE PARFUM"; cfg.accent = ORANGE
cfg.card_title = "ELUSA 501"; cfg.card_lines = ["Extrait de Parfum · Unisex", "süß · Orange · Vanille"]
cfg.end_title = "ELUSA 501"; cfg.end_sub = "Extrait de Parfum · Unisex · süß & würzig"; cfg.end_bg = (1.0, 0.94, 0.86); cfg.end_img_h = 700
cfg.captions = ["Elusa", "501!", "Extrait de Parfum,", "unisex.", "Süß,", "mit", "Orange,", "Vanille", "und", "Gewürzen…", "Riecht", "wie",
                "Weihnachtsmarkt –", "nur", "edel!", "Und", "gerade", "gilt:", "Kauf", "drei,", "spar", "46 %!", "Tipp", "unten", "links", "und", "hol's", "dir!"]
cfg.overlays = overlays
cfg.deal = "KAUF 3 = -46 %"
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (TL["spray"], "whoosh"), (TL["spray"] + 0.5, "buzz"), (T[3], "pop"), (T[4], "pop"), (T[6], "pop"), (T[7], "pop"),
            (T[9], "pop"), (TL["market"], "whoosh"), (T[12], "ding"), (T[12] + 0.1, "tada"), (T[13], "pop"), (T[18], "boom"), (T[18], "pop"), (T[20], "ding"),
            (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
