#!/usr/bin/env python3
"""LYORA Nerion -> out/14_lyora_nerion_3d.mp4"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import comp_core as C
from comp_core import gold_text, pill, outlined, sticker, back, ease, W, WHITE, font, rrect

T = [w[1] for w in json.load(open(os.path.join(HERE, "assets", "words.json")))]
TL = dict(spray=2.6, ask=3.75, extrait=6.0, elegant=9.3, gift=11.95, you=13.62, cta=15.0, end=16.75)
WINE = (0.45, 0.1, 0.2); GOLDC = (0.85, 0.65, 0.3); DARK = (0.08, 0.07, 0.08)

def bubble(cr, x, y, k, txt, rot):
    if k < 0.05: return
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); cr.scale(k, k)
    font(cr, 44); e = cr.text_extents(txt); w = e.x_advance + 60
    rrect(cr, -w / 2, -45, w, 90, 40); cr.set_source_rgba(1, 1, 1, 0.96); cr.fill()
    cr.move_to(-20, 40); cr.line_to(0, 75); cr.line_to(15, 40); cr.close_path(); cr.fill()
    cr.move_to(-e.x_advance / 2, 15); cr.set_source_rgb(0.15, 0.1, 0.12); cr.show_text(txt); cr.restore()

def overlays(cr, t, fi, conf, anc):
    fade = 1 - ease((t - TL["spray"] + 0.15) / 0.2)
    gold_text(cr, "LYORA NERION", W / 2, 320, 118, scale=back(t / 0.35) * fade, rot=-3)
    outlined(cr, "Extrait de Parfum", W / 2, 460, 62, WHITE, sw=12, scale=back((t - T[2]) / 0.3) * fade)
    if fi == 1: conf.burst(W / 2, 600, 110, [(0.95, 0.75, 0.35), (1, 1, 1), (0.5, 0.1, 0.2)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
    if TL["spray"] <= t < TL["ask"]:
        pill(cr, "1 SPRÜHER", W / 2, 320, 64, WINE, scale=back((t - T[3]) / 0.25), rot=-3)
    if TL["ask"] <= t < TL["extrait"]:
        for i, (x, y, r, dt) in enumerate(((290, 300, -5, 0.0), (790, 400, 5, 0.35), (330, 520, -3, 0.7))):
            bubble(cr, x, y, back((t - T[8] + 0.6 - dt) / 0.25), "Was trägst du da?!", r)
    if TL["extrait"] <= t < TL["elegant"]:
        pill(cr, "EXTRAIT = INTENSIVSTE STUFE", W / 2, 320, 50, DARK, scale=back((t - T[12]) / 0.25), rot=-2)
        outlined(cr, "höchste Duftkonzentration", W / 2, 430, 52, GOLDC, sw=11, scale=back((t - T[16]) / 0.3))
    if TL["elegant"] <= t < TL["gift"]:
        for txt, ti, y, r in (("ELEGANT", 17, 300, -3), ("EDEL", 18, 410, 3), ("UNVERGESSLICH", 19, 520, -2)):
            gold_text(cr, txt, W / 2, y, 88, scale=back((t - T[ti]) / 0.3), rot=r)
    if TL["gift"] <= t < TL["you"]:
        sticker(cr, 800, 380, back((t - T[22]) / 0.3), ["PERFEKTES", "GESCHENK"], col=(0.8, 0.12, 0.18), rot=-10, r=135, fs=40)
    if TL["you"] <= t < TL["cta"]:
        outlined(cr, "…ODER FÜR DICH.", W / 2, 330, 84, WHITE, sw=13, scale=back((t - T[23]) / 0.3))

cfg = C.Cfg()
cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = 17.55; cfg.outname = "14_lyora_nerion_3d.mp4"
cfg.product_img = os.path.join(HERE, "assets", "product.png")
cfg.badge = "LYORA · NERION EXTRAIT DE PARFUM"; cfg.accent = GOLDC
cfg.card_title = "LYORA NERION"; cfg.card_lines = ["Extrait de Parfum", "Versand aus DE"]
cfg.end_title = "LYORA NERION"; cfg.end_sub = "Extrait de Parfum · perfekt als Geschenk"; cfg.end_bg = (0.97, 0.9, 0.9); cfg.end_img_h = 640
cfg.captions = ["LYORA", "Nerion.", "Extrait de Parfum.", "Ein Sprüher…", "und", "plötzlich", "fragt", "jeder:", "Was", "trägst", "du", "da?",
                "Extrait", "heißt:", "die", "intensivste", "Duftkonzentration.", "Elegant,", "edel,", "unvergesslich.", "Das", "perfekte",
                "Weihnachtsgeschenk…", "oder", "einfach", "für", "dich.", "Tipp", "unten", "links", "und", "hol's", "dir!"]
cfg.overlays = overlays
cfg.sfx = ([(0.0, "boom"), (0.05, "tada"), (T[2], "whoosh"), (TL["spray"], "whoosh"), (TL["spray"] + 0.5, "buzz"), (T[8] - 0.6, "pop"), (T[8] - 0.25, "pop"),
            (T[8] + 0.1, "pop"), (TL["extrait"], "whoosh"), (T[16], "ding"), (T[17], "pop"), (T[18], "pop"), (T[19], "pop"), (TL["gift"], "whoosh"),
            (T[22], "tada"), (TL["you"], "whoosh"), (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")])
C.run(cfg)
