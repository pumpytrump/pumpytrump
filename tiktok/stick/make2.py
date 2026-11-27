#!/usr/bin/env python3
"""Batch 2: SNOCKS Boxershorts, Weihnachts-Snackbox, Schokoellsen #2 (Detektiv).
python3 make2.py [snocks|snackbox|schoko2 ...]  -> out/*.mp4
"""
import math, random, sys
import cairo
from make import (P, track, draw_stick, draw_img, img, pill, outlined, hook, cta, Particles, render, camera,
                  back, ease, win, lerp, clamp, rrect, font, W, H, FPS, YEL, WHITE, HEADR)

def head_space(cr, J, p):
    s = p["s"]; hx, hy = J["head"]
    cr.translate(hx, hy); cr.rotate(math.radians(p["lean"] + p["tilt"])); cr.scale(s, s)

# ---------------------------------------------------------------- accessories
def santa_hat(cr, J, p):
    cr.save(); head_space(cr, J, p); r = HEADR
    cr.move_to(-r * 0.95, -r * 0.7); cr.curve_to(-r * 0.6, -r * 2.0, r * 0.6, -r * 2.3, r * 1.45, -r * 1.55)
    cr.curve_to(r * 0.9, -r * 1.4, r * 0.95, -r * 1.0, r * 0.95, -r * 0.7); cr.close_path()
    cr.set_source_rgb(0.85, 0.1, 0.12); cr.fill()
    rrect(cr, -r * 1.1, -r * 0.92, r * 2.2, r * 0.42, r * 0.2); cr.set_source_rgb(1, 1, 1); cr.fill()
    cr.arc(r * 1.45, -r * 1.55, r * 0.28, 0, 2 * math.pi); cr.fill()
    cr.restore()

def fedora(cr, J, p):
    cr.save(); head_space(cr, J, p); r = HEADR
    cr.save(); cr.translate(0, -r * 0.78); cr.scale(1, 0.22); cr.arc(0, 0, r * 1.45, 0, 2 * math.pi); cr.restore()
    cr.set_source_rgb(0.42, 0.3, 0.2); cr.fill()
    rrect(cr, -r * 0.8, -r * 1.65, r * 1.6, r * 0.95, r * 0.3); cr.fill()
    cr.rectangle(-r * 0.8, -r * 0.98, r * 1.6, r * 0.2); cr.set_source_rgb(0.15, 0.1, 0.08); cr.fill()
    cr.restore()

def sunglasses(cr, J, p):
    cr.save(); head_space(cr, J, p)
    for sx in (-1, 1): rrect(cr, sx * 23 - 19, -24, 38, 24, 8)
    cr.set_source_rgb(0.05, 0.05, 0.05); cr.fill()
    cr.set_line_width(5); cr.move_to(-6, -16); cr.line_to(6, -16); cr.stroke()
    cr.restore()

def snocks_shorts(cr, J, p):
    s = p["s"]; hx, hy = J["hip"]
    def along(knee, f): return (hx + (knee[0] - hx) * f, hy + (knee[1] - hy) * f)
    ml, mr = along(J["lf_e"], 0.5), along(J["rf_e"], 0.5)
    pts = [(hx - 52 * s, hy - 42 * s), (hx + 52 * s, hy - 42 * s), (mr[0] + 36 * s, mr[1]), (mr[0] - 26 * s, mr[1] + 6 * s),
           (hx, hy + 34 * s), (ml[0] + 26 * s, ml[1] + 6 * s), (ml[0] - 36 * s, ml[1])]
    cr.move_to(*pts[0])
    for q in pts[1:]: cr.line_to(*q)
    cr.close_path(); cr.set_source_rgb(0.07, 0.07, 0.08); cr.fill_preserve()
    cr.set_source_rgb(0.45, 0.45, 0.5); cr.set_line_width(3); cr.stroke()
    rrect(cr, hx - 54 * s, hy - 46 * s, 108 * s, 24 * s, 6 * s); cr.set_source_rgb(0.16, 0.16, 0.18); cr.fill()
    font(cr, 15 * s); e = cr.text_extents("SNOCKS")
    cr.move_to(hx - e.x_advance / 2, hy - 28.5 * s); cr.set_source_rgb(1, 1, 1); cr.show_text("SNOCKS")

def old_undies(holes, crumble):
    def fn(cr, x, y, h, rot):
        w = h * 1.35
        cr.save(); cr.translate(x, y + crumble * 120); cr.rotate(math.radians(rot + crumble * 40))
        cr.scale(1 - crumble * 0.6, 1 - crumble * 0.6)
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w * 0.47, h / 2), (w * 0.13, h / 2), (0, h * 0.12), (-w * 0.13, h / 2), (-w * 0.47, h / 2)]
        cr.move_to(*pts[0])
        for q in pts[1:]: cr.line_to(*q)
        cr.close_path()
        for (fx, fy, r) in ((-0.25, 0.0, 0.07), (0.22, 0.15, 0.06), (0.05, -0.15, 0.05), (-0.33, 0.3, 0.05), (0.33, -0.1, 0.045)):
            rr = r * h * (0.5 + holes * 1.4)
            cr.new_sub_path(); cr.arc(fx * w, fy * h, rr, 0, 2 * math.pi)
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.set_source_rgba(0.72, 0.7, 0.6, 1 - crumble); cr.fill_preserve()
        cr.set_source_rgba(0.35, 0.33, 0.28, 1 - crumble); cr.set_line_width(4); cr.stroke()
        cr.set_fill_rule(cairo.FILL_RULE_WINDING)
        cr.rectangle(-w / 2, -h / 2, w, h * 0.14); cr.set_source_rgba(0.55, 0.53, 0.45, 1 - crumble); cr.fill()
        cr.restore()
    return fn

def magnifier(cr, x, y, h, rot):
    cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot)); r = h * 0.32
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(r * 0.7, r * 0.7); cr.line_to(r * 1.7, r * 1.7); cr.set_source_rgb(0.35, 0.22, 0.12); cr.set_line_width(r * 0.32); cr.stroke()
    cr.arc(0, 0, r, 0, 2 * math.pi); cr.set_source_rgba(0.7, 0.9, 1, 0.35); cr.fill_preserve()
    cr.set_source_rgb(0.2, 0.2, 0.22); cr.set_line_width(r * 0.2); cr.stroke()
    cr.restore()

def stink(cr, x, y, t):
    cr.set_line_width(7); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(3):
        ph = (t * 1.3 + i / 3) % 1
        cr.set_source_rgba(0.35, 0.7, 0.2, 0.8 * (1 - ph))
        x0, y0 = x - 60 + i * 60, y - ph * 160
        cr.move_to(x0, y0)
        for k in range(1, 7): cr.line_to(x0 + 14 * math.sin(k * 1.3 + t * 6), y0 - k * 14)
        cr.stroke()

def fly(cr, x, y, t):
    fx, fy = x + 120 * math.cos(t * 5), y + 60 * math.sin(t * 7)
    cr.set_source_rgba(0.8, 0.9, 1, 0.8)
    for sx in (-1, 1):
        cr.save(); cr.translate(fx + sx * 9, fy - 8); cr.scale(1, 0.6 + 0.4 * abs(math.sin(t * 60))); cr.arc(0, 0, 9, 0, 2 * math.pi); cr.restore(); cr.fill()
    cr.arc(fx, fy, 8, 0, 2 * math.pi); cr.set_source_rgb(0.1, 0.1, 0.1); cr.fill()

def bedroom_bg(cr, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.78, 0.84, 0.9); g.add_color_stop_rgb(1, 0.6, 0.68, 0.78)
    cr.set_source(g); cr.paint()

# ================================================================ VIDEO 4: SNOCKS
def video_snocks():
    pack = img("snocks.png", 700)
    cw = ["SNOCKS Boxer-", "shorts", "aus", "Bio-", "Baumwolle!", "Meine", "alte", "Unterhose", "ist", "von", "2014.",
          "Sie", "hat", "mehr", "Löcher", "als", "meine", "Ausreden.", "Zeit", "für", "ein", "Upgrade:", "weich,", "schwarz,",
          "passt", "zu", "allem.", "Im", "Mehrfachpack,", "im", "Black-Friday-", "Deal!", "Tipp", "unten", "auf", "den",
          "Waren-", "korb.", "Deine", "Unterhose", "wird's", "dir", "danken!"]
    DARK = (0.1, 0.1, 0.12); RED = (0.9, 0.15, 0.2)
    parts = Particles(7)

    def frame(cr, t, T, total, st):
        T_meine, T_2014, T_sie, T_loch, T_zeit, T_up, T_weich, T_schw, T_passt, T_im, T_black, T_tipp, T_deine = \
            T[5], T[10], T[11], T[14], T[18], T[21], T[22], T[23], T[24], T[27], T[30], T[32], T[38]
        T_crumble = T[17]
        bedroom_bg(cr, t)
        cr.save(); camera(cr, t, [T_crumble, T_im + 0.3, 0.45])
        # window + wardrobe
        rrect(cr, 90, 380, 300, 380, 16); cr.set_source_rgb(0.95, 0.97, 1); cr.fill()
        cr.set_source_rgb(0.5, 0.55, 0.62); cr.set_line_width(10); rrect(cr, 90, 380, 300, 380, 16); cr.stroke()
        cr.move_to(240, 380); cr.line_to(240, 760); cr.move_to(90, 570); cr.line_to(390, 570); cr.stroke()
        rrect(cr, 760, 560, 300, 770, 10); cr.set_source_rgb(0.55, 0.4, 0.28); cr.fill()
        cr.set_source_rgb(0.4, 0.28, 0.18); cr.set_line_width(6); cr.move_to(910, 570); cr.line_to(910, 1320); cr.stroke()
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(0.62, 0.46, 0.32); cr.fill()
        for i in range(12):
            cr.move_to(i * 100 - 20, 1325); cr.line_to(i * 100 - 120, H); cr.set_source_rgba(0, 0, 0, 0.08); cr.set_line_width(4); cr.stroke()

        X = 480
        catch = P(x=X, lh=(-80, -245), rh=(80, -245), mouth="grin", eyes="happy")
        show = P(x=X, lh=(-150, 40), rh=(150, 40), mouth="grin", eyes="happy")
        hold_old = P(x=X - 40, lh=(10, -60), rh=(270, -10), mouth="wavy", eyes="squint", tilt=-10)
        shock = P(x=X - 40, lh=(-100, -150), rh=(270, 10), mouth="open", eyes="wide")
        hips = P(x=X, lh=(-95, 150), rh=(95, 150), mouth="smile", eyes="dot")
        weich = P(x=X, lh=(60, 70), rh=(-60, 70), mouth="smile", eyes="closed", blush=1.0)
        cool = P(x=X, lh=(-95, 150), rh=(200, -60), mouth="smile", eyes="dot", tilt=8)
        dA = P(x=X, lh=(-200, -150), rh=(110, 120), mouth="grin", eyes="happy", lean=-6)
        dB = P(x=X, lh=(-110, 120), rh=(200, -150), mouth="grin", eyes="happy", lean=6)
        ctaP = P(x=X, lh=(-120, -235), rh=(-110, 180), mouth="grin", eyes="happy", lean=-5)
        keys = [(0, catch), (0.6, show), (T_meine, hold_old), (T_sie, hold_old), (T_crumble, shock), (T_zeit, hips),
                (T_weich, weich), (T_schw, cool), (T_passt, dA), (T_passt + 0.4, dB), (T_passt + 0.8, dA),
                (T_im, catch), (T_tipp, ctaP)]
        p = track(keys, t)
        p["y"] += 6 * math.sin(t * 7)
        if t >= T_tipp: p["y"] -= abs(math.sin(t * 6)) * 30
        wearing = t >= T_up - 0.1
        props = []
        if t < T_meine - 0.05 or T_im <= t:
            drop = 1 - ease(t / 0.5) if t < 0.5 else (1 - ease((t - T_im) / 0.35) if t >= T_im and t < T_tipp else 0)
            props.append(dict(surf=pack, at="mid" if t < T_tipp else "lh", h=300, dy=-150 - 900 * drop))
        if T_meine <= t < T_zeit:
            holes = ease((t - T_sie) / (T_crumble - T_sie)); crumble = ease((t - T_crumble) / 0.5)
            props.append(dict(fn=old_undies(holes, crumble), at="rh", h=170, dy=-20, rot=6 * math.sin(t * 3)))
        # spin transition into the new boxers
        spin = clamp((t - (T_up - 0.35)) / 0.6) if T_up - 0.35 <= t < T_up + 0.25 else None
        if spin is not None:
            cr.save(); cr.translate(p["x"], 0); cr.scale(max(0.05, abs(math.cos(spin * math.pi * 2))), 1); cr.translate(-p["x"], 0)
        J = draw_stick(cr, p, t, props, wear=(snocks_shorts,) if wearing else (),
                       hat=sunglasses if T_schw <= t < T_im else None)
        if spin is not None: cr.restore()
        if T_meine <= t < T_crumble + 0.2:
            stink(cr, J["rh"][0] + 10, J["rh"][1] - 120, t); fly(cr, J["rh"][0], J["rh"][1] - 40, t)
        if t >= T_crumble and "dust" not in st:
            st["dust"] = 1; parts.burst(J["rh"][0], J["rh"][1], 50, [(0.72, 0.7, 0.6), (0.55, 0.53, 0.45)], spd=600, life=1.0, size=(6, 14), kind="rect")
        if t >= T_up and "spark" not in st:
            st["spark"] = 1; parts.burst(p["x"], 950, 60, [(1, 0.9, 0.3), (1, 1, 1)], spd=900, life=0.8, size=(5, 10))
        parts.step_draw(cr, 1 / FPS)
        cr.restore()
        hook(cr, "MEINE UNTERHOSE HAT GEKÜNDIGT", t, T_meine)
        if T_2014 <= t < T_sie:
            pill(cr, "BAUJAHR 2014", W / 2, 300, 64, (0.45, 0.43, 0.38), scale=back((t - T_2014) / 0.25), rot=-4)
        if T_sie <= t < T_zeit:
            pill(cr, "LÖCHER: " + str(int(1 + 22 * ease((t - T_loch) / 1.2))), W / 2, 300, 64, RED, scale=back((t - T_loch) / 0.25))
        if T_zeit <= t < T_weich:
            outlined(cr, "UPGRADE!", W / 2, 310, 100, YEL, scale=back((t - T_up) / 0.3))
        for i, (txt, ts) in enumerate((("WEICH", T_weich), ("SCHWARZ", T_schw), ("PASST ZU ALLEM", T_passt))):
            if T_weich <= t < T_im:
                pill(cr, txt, (260, 800, 540)[i], (260, 260, 400)[i], 58, DARK, scale=back((t - ts) / 0.25), rot=(-5, 4, -2)[i])
        if T_im <= t < T_tipp:
            pill(cr, "BLACK FRIDAY DEAL", W / 2, 300, 70, DARK, scale=back((t - T_black) / 0.3), rot=-3)
        if t >= T_deine:
            outlined(cr, "*Unterhose: DANKE*", W / 2, 300, 66, WHITE, scale=back((t - T_deine) / 0.3))
        cta(cr, t, T_tipp, DARK)

    def sfx(T):
        return [(0.0, "whoosh"), (0.45, "boom"), (5, "whoosh"), (10, "pop"), (14, "pop"), (T[17], "crunch"),
                (T[17] + 0.1, "boom"), (T[21] - 0.35, "whoosh"), (21, "tada"), (22, "pop"), (23, "pop"), (24, "pop"),
                (27, "whoosh"), (T[27] + 0.3, "boom"), (32, "ding"), (38, "boing")]
    render("4_snocks_boxershorts", "snocks", cw, frame, sfx)

# ================================================================ VIDEO 5: Weihnachts-Snackbox
def video_snackbox():
    box = img("snackbox.png", 700)
    cw = ["Weihnachtliches", "Überraschungs-", "set:", "23", "Snacks", "und", "Süßigkeiten", "in", "einer", "Box!",
          "Eigentlich", "wollte", "ich", "sie", "verschenken.", "Dann", "hab", "ich", "reingeschaut.", "Und", "jetzt", "ist",
          "es", "ein", "Geschenk.", "Für", "mich.", "Perfekt", "zum", "Verschenken,", "oder", "zum", "Behalten.", "Tipp",
          "unten", "auf", "den", "Waren-", "korb,", "Black-Friday-Deal!"]
    RED = (0.82, 0.1, 0.14); GREEN = (0.1, 0.45, 0.25)
    parts = Particles(9)
    rng = random.Random(3)
    flakes = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(60, 160), rng.uniform(3, 9)) for _ in range(90)]

    def frame(cr, t, T, total, st):
        T_23, T_eig, T_versch, T_dann, T_rein, T_und, T_gesch, T_fuer, T_mich, T_perf, T_oder, T_beh, T_tipp, T_bfd = \
            T[3], T[10], T[14], T[15], T[18], T[19], T[24], T[25], T[26], T[27], T[30], T[32], T[33], T[39]
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.12, 0.2, 0.35); g.add_color_stop_rgb(1, 0.25, 0.12, 0.2)
        cr.set_source(g); cr.paint()
        cr.save(); camera(cr, t, [T_rein, T_oder])
        # string lights
        for i in range(16):
            x = i * 72 + 20; y = 470 + 25 * math.sin(i * 0.9)
            on = (int(t * 4) + i) % 3 != 0
            cols = [(1, 0.3, 0.3), (1, 0.85, 0.3), (0.3, 1, 0.5), (0.4, 0.6, 1)]
            c = cols[i % 4]
            cr.arc(x, y, 14 if on else 10, 0, 2 * math.pi); cr.set_source_rgba(*c, 1 if on else 0.4); cr.fill()
        # tree
        for k, (wd, yy) in enumerate(((330, 1300), (260, 1130), (190, 970))):
            cr.move_to(150 - wd / 2, yy); cr.line_to(150 + wd / 2, yy); cr.line_to(150, yy - 260); cr.close_path()
            cr.set_source_rgb(0.1, 0.5 - k * 0.05, 0.25); cr.fill()
        cr.rectangle(130, 1300, 40, 30); cr.set_source_rgb(0.4, 0.25, 0.1); cr.fill()
        for i in range(10):
            bx = 150 + ((i * 53) % 220 - 110) * (1 - (i % 3) * 0.25); by = 1250 - (i * 37) % 420
            cr.arc(bx, by, 11, 0, 2 * math.pi)
            cr.set_source_rgb(*((1, 0.2, 0.2), (1, 0.85, 0.2), (0.4, 0.7, 1))[i % 3]); cr.fill()
        cr.move_to(150, 690);
        for a in range(10):
            ang = a * math.pi / 5 - math.pi / 2; rr = 34 if a % 2 == 0 else 15
            cr.line_to(150 + rr * math.cos(ang), 720 + rr * math.sin(ang))
        cr.close_path(); cr.set_source_rgb(1, 0.85, 0.2); cr.fill()
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(0.93, 0.95, 1); cr.fill()
        X = 560
        carry = P(x=X, lh=(-125, 215), rh=(125, 215), mouth="grin", eyes="happy")
        wrap_ = P(x=X, lh=(-130, 210), rh=(130, 210), mouth="smile", eyes="happy")
        peek = P(x=X, lh=(-130, 215), rh=(130, 215), mouth="open", eyes="wide", tilt=14, look=4)
        hug = P(x=X, lh=(-120, 200), rh=(120, 200), mouth="grin", eyes="closed", blush=1.0, lean=-4)
        me = P(x=X, lh=(-130, 215), rh=(30, 40), mouth="grin", eyes="happy")
        offer = P(x=X - 60, lh=(-60, 160), rh=(280, 40), mouth="smile", eyes="dot", look=12)
        snatch = P(x=X, lh=(-120, 200), rh=(120, 200), mouth="grin", eyes="squint", lean=-6)
        ctaP = P(x=X, lh=(-80, -245), rh=(-110, 180), mouth="grin", eyes="happy", lean=-5)
        ctaP2 = P(x=X, lh=(-90, -245), rh=(90, -245), mouth="grin", eyes="happy")
        keys = [(0, carry), (T_eig, wrap_), (T_dann, peek), (T_und, hug), (T_mich, me), (T_perf, offer),
                (T_oder, snatch), (T_tipp, ctaP)]
        p = track(keys, t)
        if t < 0.8:
            u = t / 0.8; p["x"] = lerp(-200, X, ease(u))
            p["lf"] = (-62 + 55 * math.sin(t * 18), 318); p["rf"] = (62 - 55 * math.sin(t * 18), 318)
        p["y"] += 6 * math.sin(t * 7)
        if t >= T_tipp: p["y"] -= abs(math.sin(t * 6)) * 30
        bow = back((t - T_eig - 0.3) / 0.35)
        def boxfn(cr, x, y, h, rot):
            draw_img(cr, box, x, y, h, rot)
            if bow > 0:
                wbox = h * box.get_width() / box.get_height()
                cr.save(); cr.translate(x, y); cr.rotate(math.radians(rot))
                cr.set_source_rgba(0.85, 0.1, 0.14, 0.95)
                cr.rectangle(-14, -h / 2, 28, h * bow); cr.fill()
                cr.rectangle(-wbox / 2, -10, wbox * bow, 20); cr.fill()
                cr.save(); cr.translate(0, -h / 2); cr.scale(bow, bow)
                for sx in (-1, 1):
                    cr.save(); cr.translate(sx * 38, -18); cr.rotate(sx * 0.4); cr.scale(1.6, 1); cr.arc(0, 0, 26, 0, 2 * math.pi); cr.restore()
                    cr.set_source_rgb(0.85, 0.1, 0.14); cr.fill()
                cr.arc(0, -10, 16, 0, 2 * math.pi); cr.set_source_rgb(0.65, 0.05, 0.1); cr.fill(); cr.restore()
                cr.restore()
        bh = 290
        if t >= T_tipp: anchor, dy = "lh", -160
        elif T_mich <= t < T_perf: anchor, dy = "lh", 0
        else: anchor, dy = ("rh", -40) if T_perf <= t < T_oder else ("mid", 5)
        if T_tipp <= t and t >= T_bfd: pass
        props = [dict(fn=boxfn, at=anchor, h=bh, dy=dy)]
        J = draw_stick(cr, p, t, props, hat=santa_hat)
        # box glow + flying snacks when peeking
        if T_dann + 0.3 <= t < T_und:
            bx, by = (J["lh"][0] + J["rh"][0]) / 2, (J["lh"][1] + J["rh"][1]) / 2 + 5 - bh / 2
            cr.save(); cr.translate(bx, by)
            for i in range(10):
                cr.rotate(math.pi / 5 + t * 0.05); cr.move_to(0, 0); cr.line_to(-30, -260); cr.line_to(30, -260); cr.close_path()
                cr.set_source_rgba(1, 0.9, 0.4, 0.25); cr.fill()
            cr.restore()
            if "snk" not in st:
                st["snk"] = 1
                parts.burst(bx, by, 26, [(0.9, 0.1, 0.1), (0.1, 0.3, 0.85), (1, 0.8, 0.1), (0.55, 0.2, 0.7), (0.95, 0.95, 0.95)],
                            spd=1100, life=1.3, size=(16, 26), grav=1700, kind="rect")
        parts.step_draw(cr, 1 / FPS)
        # gift tag
        if T_eig + 0.3 <= t < T_tipp:
            k = back((t - T_eig - 0.4) / 0.3)
            tx, ty = J["rh"][0] + 30, J["rh"][1] + 40
            name = "MAMA" if t < T_fuer else "MICH"
            pill(cr, "FÜR: " + name, tx, ty, 40, RED if name == "MICH" else GREEN, scale=k * (1 + 0.2 * max(0, 1 - (t - T_fuer) / 0.2) if t >= T_fuer else k), rot=8)
        # snow
        for x0, y0, v, r in flakes:
            y = (y0 + v * t) % (H + 40) - 20; x = (x0 + 30 * math.sin(t + y0)) % W
            cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(1, 1, 1, 0.85); cr.fill()
        cr.restore()
        hook(cr, "DAS SOLLTE EIN GESCHENK WERDEN…", t, T_23 - 0.1)
        if T_23 <= t < T_eig:
            pill(cr, "23 TEILE", W / 2, 300, 80, RED, scale=back((t - T_23) / 0.3), rot=-4)
        if T_dann <= t < T_und:
            outlined(cr, "…OH NEIN.", W / 2, 300, 90, YEL, scale=back((t - T_rein) / 0.3))
        if T_perf <= t < T_tipp:
            pill(cr, "VERSCHENKEN", 330, 270, 54, GREEN, scale=back((t - T_perf) / 0.25), rot=-4)
            pill(cr, "BEHALTEN", 760, 380, 54, RED, scale=back((t - T_oder) / 0.25), rot=4)
            if t >= T_beh:
                k = ease((t - T_beh) / 0.25); cr.set_source_rgb(0.9, 0.1, 0.1); cr.set_line_width(10)
                cr.move_to(170, 280); cr.line_to(170 + 320 * k, 255); cr.stroke()
        if t >= T_bfd:
            pill(cr, "BLACK FRIDAY DEAL", W / 2, 300, 66, (0.1, 0.1, 0.12), scale=back((t - T_bfd) / 0.3), rot=-3)
        cta(cr, t, T_tipp, RED)

    def sfx(T):
        return [(0.0, "whoosh"), (3, "pop"), (T[10] + 0.4, "pop"), (15, "whoosh"), (T[15] + 0.3, "tada"), (19, "boing"),
                (25, "pop"), (27, "whoosh"), (30, "whoosh"), (32, "pop"), (33, "ding"), (39, "boom")]
    render("5_weihnachts_snackbox", "snackbox", cw, frame, sfx)

# ================================================================ VIDEO 6: Schokoellsen – Detektiv
def cupboard(cr, x, y, sc, op, bar_in=False, bar=None):
    cr.save(); cr.translate(x, y); cr.scale(sc, sc)
    rrect(cr, -150, -210, 300, 420, 10); cr.set_source_rgb(0.55, 0.36, 0.2); cr.fill()
    cr.rectangle(-130, -190, 260, 380); cr.set_source_rgb(0.3, 0.18, 0.1); cr.fill()
    cr.rectangle(-130, 0, 260, 10); cr.set_source_rgb(0.55, 0.36, 0.2); cr.fill()
    if bar_in and bar: draw_img(cr, bar, 0, -40, 70)
    dw = 260 * (1 - op)
    cr.rectangle(-130, -190, dw, 380); cr.set_source_rgb(0.65, 0.44, 0.25); cr.fill()
    if dw > 20: cr.arc(-130 + dw - 22, 0, 10, 0, 2 * math.pi); cr.set_source_rgb(0.9, 0.8, 0.3); cr.fill()
    cr.restore()

def fridge(cr, x, y, sc, op, bar_in=False, bar=None):
    cr.save(); cr.translate(x, y); cr.scale(sc, sc)
    rrect(cr, -150, -280, 300, 560, 22); cr.set_source_rgb(0.92, 0.94, 0.96); cr.fill()
    cr.rectangle(-130, -60, 260, 320); cr.set_source_rgb(0.75, 0.88, 0.95); cr.fill()
    for yy in (40, 150): cr.rectangle(-130, yy, 260, 6); cr.set_source_rgb(0.85, 0.92, 0.97); cr.fill()
    if bar_in and bar: draw_img(cr, bar, 0, 0, 70)
    dw = 260 * (1 - op)
    cr.rectangle(-130, -60, dw, 320); cr.set_source_rgb(0.97, 0.98, 1); cr.fill()
    cr.set_source_rgb(0.7, 0.72, 0.75); cr.set_line_width(4); cr.rectangle(-140, -270, 280, 200); cr.stroke()
    if dw > 30: cr.rectangle(-130 + dw - 30, 0, 10, 90); cr.fill()
    cr.restore()

def bed(cr, x, y, sc, op, bar_in=False, bar=None):
    cr.save(); cr.translate(x, y); cr.scale(sc, sc)
    cr.rectangle(-190, 0, 380, 120); cr.set_source_rgb(0.5, 0.35, 0.6); cr.fill()
    cr.rectangle(-200, -120, 30, 260); cr.set_source_rgb(0.4, 0.27, 0.15); cr.fill()
    cr.rectangle(-190, -20, 380, 40); cr.set_source_rgb(0.95, 0.95, 0.97); cr.fill()
    if bar_in and bar: draw_img(cr, bar, -90, -30, 60)
    cr.save(); cr.translate(-90, -40 - op * 70); cr.rotate(-op * 0.35)
    rrect(cr, -80, -35, 160, 70, 30); cr.set_source_rgb(1, 1, 1); cr.fill_preserve()
    cr.set_source_rgb(0.75, 0.75, 0.8); cr.set_line_width(4); cr.stroke(); cr.restore()
    cr.restore()

def video_schoko2():
    stack = img("schoko.png", 700); bar = img("bar.png", 700)
    cw = ["Schokoellsen", None, "ist", "so", "gut,", "ich", "muss", "sie", "vor", "mir", "selbst", "verstecken.", "Im",
          "Schrank.", "Im", "Kühlschrank.", "Unter", "dem", "Kopf-", "kissen.", "Und", "trotzdem:", "alles", "weg!",
          "Hauptverdächtiger:", "ich.", "Bei", "dieser", "Schokolade", "wird", "nicht", "gelogen.", "Also", "gut:", "Ich",
          "war", "es!", "Tipp", "unten", "auf", "den", "Waren-", "korb,", "bevor", "ich", "das", "nächste", "Versteck", "finde!"]
    RED = (0.85, 0.1, 0.12); BROWN = (0.45, 0.25, 0.12)

    def frame(cr, t, T, total, st):
        T_ich, T_s1, T_s2, T_s3, T_und, T_trotz, T_alles, T_weg, T_haupt, T_ichs, T_bei, T_also, T_war, T_tipp = \
            T[5], T[12], T[14], T[16], T[20], T[21], T[22], T[23], T[24], T[25], T[26], T[32], T[34], T[37]
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 1, 0.93, 0.82); g.add_color_stop_rgb(1, 0.98, 0.8, 0.65)
        cr.set_source(g); cr.paint()
        cr.save(); camera(cr, t, [T_weg, T_war])
        for i in range(40):
            x = (i * 137 + t * 25) % (W + 60) - 30; y = (i * 251) % 1250
            cr.arc(x, y, 10, 0, 2 * math.pi); cr.set_source_rgba(0.85, 0.55, 0.4, 0.25); cr.fill()
        cr.rectangle(-100, 1325, W + 200, 800); cr.set_source_rgb(0.62, 0.38, 0.22); cr.fill()
        # hiding spots (one per quick cut)
        spots = [(T_s1, T_s2, cupboard, 1110), (T_s2, T_s3, fridge, 1045), (T_s3, T_und, bed, 1200)]
        hidden_spot = None
        for a, b, fn, yy in spots:
            if a <= t < b:
                op = win(t, a + 0.05, b - 0.3, 0.15); fn(cr, 800, yy, 1.0, op, bar_in=(t > a + 0.45), bar=bar); hidden_spot = (a, b)
        X = 400 if hidden_spot else 540
        hugb = P(x=X, lh=(60, 70), rh=(-60, 70), mouth="smile", eyes="happy", blush=1.0)
        sneaky = P(x=X, lh=(60, 70), rh=(-60, 70), mouth="flat", eyes="dot", look=-14)
        sneaky2 = P(x=X, lh=(60, 70), rh=(-60, 70), mouth="flat", eyes="dot", look=14)
        reach = P(x=X, lh=(-80, 250), rh=(285, 60), mouth="flat", eyes="squint", look=14)
        panic = P(x=X, lh=(-60, -150), rh=(60, -150), mouth="open", eyes="wide")
        detect = P(x=X, lh=(-80, 250), rh=(170, -20), mouth="flat", eyes="squint", look=10)
        selfcheck = P(x=X, lh=(-80, 250), rh=(40, -50), mouth="open", eyes="wide")
        honest = P(x=X, lh=(40, 90), rh=(180, -20), mouth="smile", eyes="closed")
        surrender = P(x=X, lh=(-160, -200), rh=(160, -200), mouth="grin", eyes="squint")
        ctaP = P(x=X, lh=(-120, -235), rh=(-110, 180), mouth="grin", eyes="happy", lean=-5)
        keys = [(0, hugb), (T_ich, sneaky), (T_ich + 0.7, sneaky2), (T_s1, reach), (T_s2, reach), (T_s3, reach),
                (T_und, panic), (T_haupt, detect), (T_ichs, selfcheck), (T_bei, honest), (T_war, surrender), (T_tipp, ctaP)]
        p = track(keys, t)
        p["y"] += 6 * math.sin(t * 7)
        if hidden_spot:  # small hop into each cut
            d = t - hidden_spot[0]; p["y"] -= 60 * max(0, math.sin(min(d / 0.3, 1) * math.pi))
        if T_und <= t < T_haupt: p["x"] += 8 * math.sin(t * 50)
        if t >= T_tipp: p["y"] -= abs(math.sin(t * 6)) * 30
        p["smear"] = 1.0 if t >= T_ichs else 0.0
        p["sweat"] = win(t, T_war, T_tipp, 0.2)
        props = []
        if t < T_s1: props.append(dict(surf=bar, at="mid", h=140, dy=-20, rot=-10))
        elif hidden_spot and t < hidden_spot[0] + 0.45: props.append(dict(surf=bar, at="rh", h=90, dy=-10))
        if T_haupt <= t < T_bei: props.append(dict(fn=magnifier, at="rh", h=200, dy=-40, rot=-20))
        if T_bei <= t: props.append(dict(surf=stack, at="rh" if t < T_war else "lh", h=230 if t < T_tipp else 250,
                                          dy=-110 if t < T_war else -130))
        hat = fedora if T_haupt <= t < T_bei else None
        J = draw_stick(cr, p, t, props, hat=hat)
        # spotlight in detective section
        if T_haupt <= t < T_bei:
            k = win(t, T_haupt, T_bei - 0.05, 0.2)
            cr.rectangle(-200, -200, W + 400, H + 400)
            cr.new_sub_path(); cr.arc_negative(J["head"][0], J["head"][1] + 150, 330, 2 * math.pi, 0)
            cr.set_source_rgba(0, 0, 0, 0.55 * k); cr.fill()
        cr.restore()
        hook(cr, "ICH VERSTECKE SCHOKO VOR MIR SELBST", t, T_s1 - 0.05)
        for i, (a, b, fn, yy) in enumerate(spots):
            if T_s1 <= t < T_und and a <= t < b:
                pill(cr, f"VERSTECK #{i + 1}", W / 2, 300, 64, BROWN, scale=back((t - a) / 0.2), rot=(-3, 3, -2)[i])
        if T_und <= t < T_haupt:  # empty-check panels
            for i, (fn, ts) in enumerate(((cupboard, T_trotz), (fridge, T_alles), (bed, T_weg))):
                k = back((t - ts) / 0.25)
                if k <= 0: continue
                cx = 200 + i * 340
                cr.save(); cr.translate(cx, 330); cr.scale(k, k)
                rrect(cr, -150, -150, 300, 300, 24); cr.set_source_rgb(1, 1, 1); cr.fill()
                fn(cr, 0, 10 if fn is not bed else 40, 0.45 if fn is not bed else 0.6, 1.0)
                cr.set_source_rgb(0.9, 0.1, 0.1); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
                cr.move_to(-90, -90); cr.line_to(90, 90); cr.move_to(90, -90); cr.line_to(-90, 90); cr.stroke()
                cr.restore()
            outlined(cr, "LEER?!", W / 2, 560, 90, YEL, scale=back((t - T_weg) / 0.25))
        if T_haupt <= t < T_bei:
            pill(cr, "HAUPTVERDÄCHTIGER", W / 2, 300, 60, (0.15, 0.15, 0.18), scale=back((t - T_haupt) / 0.25))
            outlined(cr, "…ICH?!", W / 2, 440, 90, YEL, scale=back((t - T_ichs) / 0.25))
        if T_war <= t < T_tipp:
            pill(cr, "GESTÄNDNIS", W / 2, 300, 72, RED, scale=back((t - T_war) / 0.25), rot=-4)
        if t >= T_tipp:
            pill(cr, "BLACK FRIDAY DEAL", W / 2, 300, 64, RED, scale=back((t - T_tipp - 0.6) / 0.3), rot=-3)
        cta(cr, t, T_tipp, RED)

    def sfx(T):
        return [(0.0, "boing"), (5, "whoosh"), (12, "whoosh"), (T[12] + 0.45, "pop"), (14, "whoosh"), (T[14] + 0.45, "pop"),
                (16, "whoosh"), (T[16] + 0.45, "pop"), (21, "buzz"), (22, "buzz"), (23, "buzz"), (24, "boom"),
                (25, "ding"), (26, "whoosh"), (T[36] + 0.3, "boing"), (37, "boom")]
    render("6_schokoellsen_detektiv", "schoko2", cw, frame, sfx)

if __name__ == "__main__":
    which = sys.argv[1:] or ["snocks", "snackbox", "schoko2"]
    for w_ in which: {"snocks": video_snocks, "snackbox": video_snackbox, "schoko2": video_schoko2}[w_]()
