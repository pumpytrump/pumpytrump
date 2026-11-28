#!/usr/bin/env python3
"""More DAILY100 -> out/16_more_daily100_3d.mp4"""
import json, math, os, sys
import cairo
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, H, WHITE, font, rrect

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(box=1.65, sachet=3.6, mix=4.85, drink=5.65, weeks=7.05, tease=9.35, price=10.5, cta=14.7, end=16.25)
MAG = (0.75, 0.15, 0.45); PINK = (0.93, 0.45, 0.65); RED = (0.9, 0.12, 0.18); DARK = (0.1, 0.08, 0.1)

def price_block(cr, t, y0=300):
    k = back((t - T[27]) / 0.3)
    if k > 0.05:
        cr.save(); cr.translate(W / 2, y0 + 30); cr.rotate(math.radians(-6)); cr.scale(k * (1 + 0.04 * math.sin(t * 10)), k * (1 + 0.04 * math.sin(t * 10)))
        gold_text(cr, "-50 %", 0, 0, 230, c1=(1, 0.6, 0.6), mid=(0.95, 0.2, 0.2), c2=(0.6, 0.02, 0.05))
        cr.restore()
    k2 = back((t - T[30]) / 0.25)
    if k2 > 0.05:
        cr.save(); cr.translate(W / 2 - 200, y0 + 240); cr.scale(k2, k2)
        font(cr, 80); txt = "87,99 €"; e = cr.text_extents(txt)
        rrect(cr, -e.x_advance / 2 - 24, -70, e.x_advance + 48, 96, 20); cr.set_source_rgba(1, 1, 1, 0.92); cr.fill()
        cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgb(0.4, 0.4, 0.45); cr.show_text(txt)
        sk = ease((t - T[30] - 0.15) / 0.25); cr.set_source_rgb(*RED); cr.set_line_width(9)
        cr.move_to(-e.x_advance / 2 - 10, -20); cr.line_to(-e.x_advance / 2 - 10 + (e.x_advance + 20) * sk, -20 - 20 * sk); cr.stroke(); cr.restore()
    k3 = back((t - T[33]) / 0.3)
    if k3 > 0.05:
        cr.save(); cr.translate(W / 2 + 190, y0 + 250); cr.rotate(math.radians(4)); cr.scale(k3, k3)
        pill(cr, "44,00 €", 0, 0, 96, RED)
        cr.restore()

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["box"] + 0.15) / 0.2)
    gold_text(cr, "MORE DAILY100", W / 2, 320, 118, scale=back(t / 0.35) * fade, rot=-3, c1=(1, 0.8, 0.9), mid=(0.95, 0.45, 0.65), c2=(0.6, 0.1, 0.35))
    pill(cr, "BLACK FRIDAY -50 %", W / 2, 460, 56, RED, scale=back((t - 0.6) / 0.3) * fade, rot=2)
    if fi == 1: conf.burst(W / 2, 600, 110, [(0.95, 0.45, 0.65), (1, 1, 1), (0.75, 0.15, 0.45)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["box"] <= t < TL["sachet"]:
        pill(cr, "MONATSBOX", W / 2, 320, 64, MAG, scale=back((t - T[5]) / 0.25), rot=-3)
    steps = (("1 SACHET", TL["sachet"], MAG), ("+ WASSER", TL["mix"], (0.2, 0.5, 0.85)), ("MIXEN & TRINKEN", TL["drink"], PINK))
    for i, (txt, ts, col) in enumerate(steps):
        te = steps[i + 1][1] if i + 1 < len(steps) else TL["weeks"]
        if ts <= t < te: pill(cr, txt, W / 2, 320, 66, col, scale=back((t - ts) / 0.2), rot=(-3, 3)[i % 2])
    if TL["weeks"] <= t < TL["tease"]:
        pill(cr, "4 WOCHEN", 330, 300, 60, MAG, scale=back((t - T[17]) / 0.25), rot=-4)
        pill(cr, "SMOOTHIE-MIX + VITAMINE", W / 2, 420, 50, DARK, scale=back((t - T[20]) / 0.25), rot=2)
    if TL["tease"] <= t < TL["price"]:
        outlined(cr, "PSST…", W / 2, 330, 90, WHITE, sw=13, scale=back((t - T[24]) / 0.3))
    if TL["price"] <= t < TL["cta"]:
        if abs(t - T[27]) < 0.02:
            conf.burst(W / 2, 380, 140, [(1, 0.85, 0.2), (1, 1, 1), (0.95, 0.3, 0.5)], spd=1700, life=2.0, size=(9, 16), grav=1200, kind="rect")
        price_block(cr, t)
    if TL["cta"] <= t < TL["end"]:
        pill(cr, "NUR 44,00 € STATT 87,99 €", W / 2, 320, 52, RED, scale=back((t - TL["cta"]) / 0.25), rot=-2)
    if t < TL["end"]:
        font(cr, 26); txt = "Nahrungsergänzungsmittel. Kein Ersatz für eine ausgewogene Ernährung."; e = cr.text_extents(txt)
        cr.move_to(W / 2 - e.x_advance / 2, 1880); cr.set_source_rgba(1, 1, 1, 0.9); cr.show_text(txt)

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.3; cfg.outname = "16_more_daily100_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "MORE NUTRITION · DAILY100"; cfg.accent = MAG
cfg.card_title = "MORE DAILY100"; cfg.card_lines = ["-50 %: 44,00 € statt 87,99 €", "Monatsbox · 4 Wochen"]
cfg.end_title = "MORE DAILY100"; cfg.end_sub = "BLACK FRIDAY: 44,00 € statt 87,99 €"; cfg.end_bg = (1.0, 0.9, 0.95); cfg.end_img_h = 700
cfg.end_note = "Nahrungsergänzungsmittel. Kein Ersatz für eine ausgewogene Ernährung."
cfg.captions = ["More", "DAILY", "100!", "Deine", "tägliche", "Routine", "in", "einer", "Box:", "Jeden", "Tag", "ein", "Sachet,", "mit",
                "Wasser mixen,", "trinken,", "fertig!", "Vier", "Wochen,", "ein", "Smoothie-Mix", "", "mit", "Vitaminen.", "Und", "jetzt",
                "kommt's:", "Minus", "50", "Prozent!", "Statt", "88", "nur", "44", "Euro!", "Tipp", "unten", "links", "und", "schnapp's", "dir!"]
cfg.overlays = overlays
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (0.5, "whoosh"), (TL["box"], "whoosh"), (T[5], "pop"), (TL["sachet"], "pop"), (TL["mix"], "crack"),
            (TL["mix"] + 0.25, "crunch"), (TL["drink"], "whoosh")] + [(TL["drink"] + 0.06 * i, "crunch") for i in range(8)] +
           [(TL["drink"] + 0.9, "gulp"), (TL["drink"] + 1.2, "gulp"), (T[17], "pop"), (T[20], "pop"), (T[24], "boing"), (T[27], "boom"), (T[27], "tada"),
            (T[30], "whoosh"), (T[30] + 0.15, "crack"), (T[33], "ding"), (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
