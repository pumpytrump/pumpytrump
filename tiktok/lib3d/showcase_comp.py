"""Showcase v2 compositing: reads spec.json + assets/words.json and renders out/<spec.out> via comp_core.
New look vs v1: karaoke-box captions in the product accent, swinging price tag, starburst discount, bloom + vignette grade."""
import difflib, json, math, os, re, sys
import cairo
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comp_core as C
from comp_core import gold_text, pill, outlined, back, ease, W, H, WHITE, font, rrect, RED
from showcase import timeline, hexcol


def norm(w): return re.sub(r"[^a-z0-9äöüß]", "", w.lower())


def align_captions(script, words):
    """Use the script's spelling for each whisper word where the two line up."""
    toks = re.sub(r"\[[^\]]*\]", " ", script).split()
    a = [norm(x) for x in toks]; b = [norm(w[0]) for w in words]
    out = [w[0] for w in words]
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(j2 - j1): out[j1 + k] = toks[i1 + k]
        elif tag == "replace":
            out[j1] = " ".join(toks[i1:i2])
            for k in range(j1 + 1, j2): out[k] = ""
    return out


def make_post(strength=0.35):
    def post(im):
        rgb = im.convert("RGB")
        hi = rgb.point(lambda v: max(0, v - 185) * 3).filter(ImageFilter.GaussianBlur(22))
        rgb = ImageChops.add(rgb, ImageEnhance.Brightness(hi).enhance(strength))
        rgb = ImageEnhance.Contrast(rgb).enhance(1.05); rgb = ImageEnhance.Color(rgb).enhance(1.08)
        return rgb.convert("RGBA")
    return post


VIG = None
def vignette(cr):
    global VIG
    if VIG is None:
        VIG = cairo.RadialGradient(W / 2, H * 0.45, H * 0.3, W / 2, H * 0.45, H * 0.78)
        VIG.add_color_stop_rgba(0, 0, 0, 0, 0); VIG.add_color_stop_rgba(1, 0, 0, 0, 0.38)
    cr.set_source(VIG); cr.paint()


def captions_box(accent):
    def cap(cr, words, t, y=1500):
        chunks, cur = [], []
        for i, (w_, s, e) in enumerate(words):
            cur.append(i); txt = " ".join(words[j][0] for j in cur)
            if len(cur) >= 3 or len(txt) >= 16 or w_[-1] in ".,!?:": chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        act = None
        for ch in chunks:
            if words[ch[0]][1] - 0.02 <= t <= words[ch[-1]][2] + 0.2: act = ch
        if not act: return
        size = 84; font(cr, size); gap = 26
        toks = [words[i][0].upper() for i in act]
        ws = [cr.text_extents(x).x_advance for x in toks]; tot = sum(ws) + gap * (len(ws) - 1)
        if tot > 960: size = int(size * 960 / tot); font(cr, size); ws = [cr.text_extents(x).x_advance for x in toks]; tot = sum(ws) + gap * (len(ws) - 1)
        x = (W - tot) / 2
        for i, tok, wd in zip(act, toks, ws):
            s, e = words[i][1], words[i][2]
            on = s <= t < max(e, s + 0.12) + 0.06
            if on:
                k = back((t - s) / 0.12)
                cr.save(); cr.translate(x + wd / 2, y - size * 0.32); cr.rotate(math.radians(-2)); cr.scale(k, k)
                rrect(cr, -wd / 2 - 16, -size * 0.62, wd + 32, size * 1.22, 18); cr.set_source_rgb(*accent); cr.fill(); cr.restore()
            outlined(cr, tok, x + wd / 2, y, size, WHITE, sw=12, maxw=2000, scale=1.06 if on else 1.0)
            x += wd + gap
    return cap


def price_tag(cr, t, t0, price, old, pct, accent, y0=360):
    k = back((t - t0) / 0.4)
    if k > 0.05:
        sw = math.radians(8 * math.sin((t - t0) * 4) * math.exp(-(t - t0) * 0.8))
        cr.save(); cr.translate(W / 2 + 120, y0 - 40); cr.rotate(sw - 0.05); cr.scale(k, k)
        cr.set_source_rgb(0.95, 0.95, 0.95); cr.set_line_width(5); cr.move_to(0, -150); cr.line_to(-60, -40); cr.stroke()
        font(cr, 104); e = cr.text_extents(price); w = max(e.x_advance + 120, 360)
        cr.move_to(-w / 2 - 50, 60); cr.line_to(-w / 2 + 20, -40); cr.line_to(w / 2, -40); cr.line_to(w / 2, 160); cr.line_to(-w / 2 + 20, 160); cr.close_path()
        cr.set_source_rgba(0, 0, 0, 0.3); cr.save(); cr.translate(8, 10); cr.fill_preserve(); cr.restore(); cr.new_path()
        cr.move_to(-w / 2 - 50, 60); cr.line_to(-w / 2 + 20, -40); cr.line_to(w / 2, -40); cr.line_to(w / 2, 160); cr.line_to(-w / 2 + 20, 160); cr.close_path()
        cr.set_source_rgb(*accent); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(7); cr.stroke()
        cr.arc(-w / 2 - 5, 60, 14, 0, 2 * math.pi); cr.set_source_rgb(1, 1, 1); cr.fill()
        font(cr, 104); cr.move_to(-w / 2 + 40, 100); cr.set_source_rgb(1, 1, 1); cr.show_text(price)
        cr.restore()
    if old:
        k2 = back((t - t0 - 0.35) / 0.3)
        if k2 > 0.05:
            cr.save(); cr.translate(W / 2 - 250, y0 - 150); cr.scale(k2, k2)
            font(cr, 66); e = cr.text_extents(old)
            rrect(cr, -e.x_advance / 2 - 20, -58, e.x_advance + 40, 82, 18); cr.set_source_rgba(1, 1, 1, 0.94); cr.fill()
            cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgb(0.4, 0.4, 0.45); cr.show_text(old)
            sk = ease((t - t0 - 0.5) / 0.25); cr.set_source_rgb(*RED); cr.set_line_width(8)
            cr.move_to(-e.x_advance / 2 - 8, -16); cr.line_to(-e.x_advance / 2 - 8 + (e.x_advance + 16) * sk, -16 - 16 * sk); cr.stroke(); cr.restore()
    if pct:
        k3 = back((t - t0 - 0.2) / 0.3)
        if k3 > 0.05:
            cr.save(); cr.translate(W / 2 - 290, y0 + 80); cr.rotate(math.radians(-12 + 4 * math.sin(t * 3))); cr.scale(k3, k3)
            n = 14
            for i in range(2 * n):
                a = i * math.pi / n; r = 130 if i % 2 == 0 else 104
                (cr.move_to if i == 0 else cr.line_to)(r * math.cos(a), r * math.sin(a))
            cr.close_path(); cr.set_source_rgb(1, 0.82, 0.15); cr.fill_preserve(); cr.set_source_rgb(1, 1, 1); cr.set_line_width(5); cr.stroke()
            font(cr, 58 if len(pct) < 6 else 40); e = cr.text_extents(pct); cr.move_to(-e.x_advance / 2, 20); cr.set_source_rgb(0.15, 0.08, 0.02); cr.show_text(pct)
            cr.restore()


def main(HERE):
    A = os.path.join(HERE, "assets")
    S = json.load(open(os.path.join(HERE, "spec.json")))
    wj = json.load(open(os.path.join(A, "words.json")))
    TL, IDX = timeline(wj, S["kw"])
    accent = hexcol(S["accent"]); dark = tuple(c * 0.55 for c in accent)
    T = [w[1] for w in wj]
    caps = S.get("captions") or align_captions(S["voice"], wj)
    pills = []
    for kw, txt, col in S.get("pills", []):
        from showcase import find
        i = find(wj, kw, IDX["problem"])
        if i is not None: pills.append((T[i], txt, hexcol(col)))
    pills.sort()

    def overlays(cr, t, fi, conf, anc):
        vignette(cr)
        fade = 1 - ease((t - TL["problem"] + 0.15) / 0.2)
        gold_text(cr, S["title"], W / 2, 330, 112, scale=back(t / 0.35) * fade, rot=-3,
                  c1=tuple(min(1, c * 0.5 + 0.55) for c in accent), mid=accent, c2=dark)
        if S.get("deal"): pill(cr, S["deal"], W / 2, 470, 54, RED, scale=back((t - 0.6) / 0.3) * fade, rot=2)
        if fi == 1: conf.burst(W / 2, 600, 120, [accent, (1, 1, 1), (1, 0.85, 0.3)], spd=1500, life=1.8, size=(9, 16), grav=1300, kind="rect")
        for n, (ts, txt, col) in enumerate(pills):
            te = min(pills[n + 1][0] if n + 1 < len(pills) else 99, ts + 2.6, TL["price"] if ts < TL["price"] else TL["cta"])
            if ts <= t < te: pill(cr, txt, W / 2 + (-70, 70)[n % 2], 330 + 105 * (n % 2), 60, col, scale=back((t - ts) / 0.22), rot=(-3, 3)[n % 2])
        if TL["price"] <= t < TL["cta"]:
            if abs(t - TL["price"] - 0.1) < 0.02:
                conf.burst(W / 2, 380, 150, [(1, 0.85, 0.2), (1, 1, 1), accent], spd=1700, life=2.0, size=(9, 16), grav=1200, kind="rect")
            price_tag(cr, t, TL["price"] + 0.1, S["price"], S.get("old", ""), S.get("pct", ""), accent)
        if TL["cta"] <= t < TL["end"]:
            pill(cr, S.get("cta_line", "NUR " + S["price"]), W / 2, 330, 56, RED, scale=back((t - TL["cta"]) / 0.25), rot=-2)
        if S.get("notice") and t < TL["end"]:
            font(cr, 24); e = cr.text_extents(S["notice"]); sc_ = min(1.0, 1000 / e.x_advance)
            cr.save(); cr.translate(W / 2, 1885); cr.scale(sc_, sc_); cr.move_to(-e.x_advance / 2, 0); cr.set_source_rgba(1, 1, 1, 0.92); cr.show_text(S["notice"]); cr.restore()

    cfg = C.Cfg()
    cfg.here = HERE; cfg.TL = TL; cfg.TOTAL = round(TL["end"] + 1.05, 2); cfg.outname = S["out"]
    cfg.product_img = os.path.join(A, "product.png")
    cfg.badge = S["badge"]; cfg.accent = accent
    cfg.card_title = S["card_title"]; cfg.card_lines = S["card_lines"]
    cfg.end_title = S["card_title"]; cfg.end_sub = S["end_sub"]; cfg.end_bg = tuple(min(1, 0.75 + 0.25 * c) for c in accent); cfg.end_img_h = S.get("end_img_h", 640)
    if S.get("notice"): cfg.end_note = S["notice"] if len(S["notice"]) < 75 else S["notice"][:S["notice"].rfind(". ", 0, 75) + 1]
    if S.get("deal_end"): cfg.deal = S["deal_end"]; cfg.deal_t = (-1, -1)
    cfg.captions = caps; cfg.overlays = overlays
    cfg.captions_fn = captions_box(accent); cfg.post = make_post(); cfg.cap_y = 1500
    sfx = [(0.0, "boom"), (0.05, "tada"), (0.5, "whoosh"), (TL["problem"], "whoosh"), (TL["use"], "pop"), (TL["use"] + 0.4, "whoosh"),
           (TL["price"], "whoosh"), (TL["price"] + 0.1, "boom"), (TL["price"] + 0.15, "tada"), (TL["price"] + 0.5, "crack"), (TL["price"] + 0.4, "ding"),
           (TL["cta"], "whoosh"), (TL["cta"] + 0.1, "pop"), (TL["end"], "whoosh"), (TL["end"] + 0.2, "pop")]
    sfx += [(ts, "pop") for ts, _, _ in pills]
    sfx += [(t_, s_) for t_, s_ in S.get("sfx", [])]
    cfg.sfx = sorted(sfx)
    C.run(cfg)
