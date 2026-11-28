"""Showcase v2: one data-driven 3D product video scene (spec.json per product).
Beats: hook (product on glowing turntable) -> problem (character + mood) -> use (action with the product)
       -> price (product next to face, confetti) -> cta (point down-left) ; end card is drawn in comp.
python3 scene.py --test 0.8,3,6,9,12,14 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

TOP = 0.9225


def find(words, kw, start=0):
    kw = kw.lower()
    for i in range(start, len(words)):
        w = words[i][0].lower().strip(".,!?:;…\"'")
        if w.startswith(kw): return i
    return None


def timeline(words, kw):
    TL, idx, s = {}, {}, 1
    for k in ("problem", "use", "price", "cta"):
        i = find(words, kw[k], s)
        if i is None: raise SystemExit(f"keyword {k}={kw[k]!r} not found in {[w[0] for w in words]}")
        idx[k] = i; TL[k] = max(words[i][1] - 0.06, 0.0); s = i + 1
    TL["end"] = words[-1][2] + 0.35
    return TL, idx


def hexcol(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ rooms
def room(kind, accent):
    M = K.mat
    if kind in ("kitchen", "cafe"):
        wall = M("wall", (0.95, 0.9, 0.86) if kind == "kitchen" else (0.55, 0.32, 0.25), rough=0.9)
        back = K.brick_mat("tile", (0.97, 0.96, 0.95), (0.92, 0.91, 0.9), (0.72, 0.7, 0.7), scale=14) if kind == "kitchen" else \
            K.brick_mat("brick", (0.62, 0.3, 0.22), (0.5, 0.24, 0.18), (0.82, 0.78, 0.72), scale=10, coat=0.1)
        floor = K.wood_mat("floor", (0.55, 0.4, 0.27), (0.72, 0.56, 0.38), scale=3.0)
    elif kind == "gym":
        wall = M("wall", (0.18, 0.19, 0.22), rough=0.85); back = M("wallb", (0.12, 0.13, 0.15), rough=0.7)
        floor = K.checker_mat("floor", (0.08, 0.08, 0.09), (0.11, 0.11, 0.12), scale=4, rough=0.6, coat=0.1)
    elif kind == "bedroom":
        wall = M("wall", (0.62, 0.7, 0.8), rough=0.95); back = M("wallb", (0.7, 0.76, 0.84), rough=0.95)
        floor = K.wood_mat("floor", (0.6, 0.47, 0.34), (0.75, 0.6, 0.45), scale=3.0)
    elif kind == "xmas":
        wall = M("wall", (0.72, 0.18, 0.2), rough=0.9); back = M("wallb", (0.85, 0.78, 0.66), rough=0.9)
        floor = K.wood_mat("floor", (0.45, 0.3, 0.2), (0.6, 0.42, 0.28), scale=3.0)
    elif kind == "dressing":
        wall = M("wall", (0.36, 0.16, 0.24), rough=0.85); back = M("wallb", (0.42, 0.2, 0.28), rough=0.85)
        floor = M("floor", (0.85, 0.82, 0.8), rough=0.15, coat=0.8)
    elif kind == "bath":
        wall = K.brick_mat("tile", (0.9, 0.95, 0.96), (0.85, 0.92, 0.93), (0.7, 0.75, 0.76), scale=16)
        back = wall; floor = K.checker_mat("floor", (0.85, 0.87, 0.9), (0.3, 0.33, 0.38), scale=8)
    else:  # office
        wall = M("wall", (0.86, 0.88, 0.84), rough=0.9); back = M("wallb", (0.3, 0.42, 0.38), rough=0.9)
        floor = M("floor", (0.35, 0.36, 0.4), rough=0.9)
    K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), floor)
    K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), wall)
    K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), wall)
    K.box("feature", (2.2, 0.02, 2.0), (0.5, 2.585, 1.6), m=back)
    ACC = M("acc", accent, rough=0.35, coat=0.5)
    NEON = M("neon", accent, emit=accent, es=6.0)
    # counter / table every scene stands behind
    top_m = {"kitchen": M("counter", (0.97, 0.97, 0.97), rough=0.15, coat=0.8), "cafe": K.wood_mat("oak", (0.5, 0.34, 0.2), (0.66, 0.48, 0.3), scale=2.0),
             "gym": M("counter", (0.15, 0.15, 0.17), rough=0.3, coat=0.6), "office": K.wood_mat("oak", (0.62, 0.45, 0.3), (0.8, 0.64, 0.45), scale=2.0)
             }.get(kind, M("counter", (0.96, 0.95, 0.94), rough=0.2, coat=0.7))
    body_m = {"gym": M("body", (0.1, 0.1, 0.12), rough=0.5), "cafe": M("body", (0.2, 0.14, 0.1), rough=0.6), "xmas": M("body", (0.95, 0.93, 0.9), rough=0.5),
              "dressing": M("body", (0.2, 0.08, 0.12), rough=0.4, coat=0.5)}.get(kind, K.WHITE)
    K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=body_m, bevel=0.01)
    K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=top_m, bevel=0.005)
    K.box("strip", (2.4, 0.01, 0.025), (0, 0.415, 0.85), m=NEON)         # glowing accent strip on the counter edge
    rng = random.Random(7)
    if kind in ("kitchen", "cafe"):
        K.box("bcounter", (1.6, 0.5, 0.9), (0.9, 2.35, 0.45), m=body_m, bevel=0.01)
        K.box("bctop", (1.65, 0.55, 0.04), (0.9, 2.35, 0.92), m=top_m, bevel=0.005)
        K.cyl("kettle", 0.08, 0.2, (1.25, 2.35, 1.04), m=ACC)
        for i, c in enumerate([(0.9, 0.3, 0.3), (0.95, 0.75, 0.3), (0.4, 0.65, 0.4)]):
            K.sphere("fruit", 0.05, (0.55 + i * 0.12, 2.3, 0.99), m=K.mat(f"fr{i}", c, rough=0.4, sss=0.2), seg=16)
        for i in range(3): K.box("shelf", (0.6, 0.18, 0.025), (-1.1 + i * 0.0, 2.5, 1.5 + i * 0.35), m=top_m)
        for i in range(6): K.cyl("jar", 0.045, 0.12 + 0.03 * (i % 2), (-1.3 + 0.1 * (i % 3), 2.48, 1.53 + 0.35 * (i // 3) + 0.06), m=K.thin_glass(f"jar{i}"))
        if kind == "cafe":
            K.box("menu", (0.9, 0.03, 0.6), (-0.6, 2.56, 1.9), m=M("board", (0.08, 0.09, 0.08), rough=0.9))
            for i in range(4): K.box("chalk", (0.5 - 0.08 * i, 0.005, 0.03), (-0.65, 2.54, 2.08 - 0.1 * i), m=M(f"ch{i}", (0.9, 0.9, 0.85), emit=(1, 1, 0.95), es=0.6))
    elif kind == "gym":
        for i in range(6):
            y = 2.2; x = -1.0 + 0.3 * i
            K.cyl("db", 0.05, 0.22, (x, y, 1.0), m=K.BLACK, rot=(0, math.pi / 2, 0))
            for s in (-1, 1): K.cyl("plate", 0.085, 0.05, (x + s * 0.1, y, 1.0), m=ACC, rot=(0, math.pi / 2, 0))
        K.box("rack", (2.0, 0.3, 0.05), (-0.25, 2.2, 0.9), m=K.CHROME)
        for i in range(3): K.box("neonbar", (1.5, 0.02, 0.03), (0.6, 2.56, 1.3 + 0.35 * i), m=NEON)
        K.box("mirror", (1.2, 0.02, 1.2), (-1.0, 2.57, 1.7), m=K.CHROME)
    elif kind == "bedroom":
        K.box("bed", (1.8, 1.4, 0.45), (0.9, 2.0, 0.22), m=M("sheet", (0.95, 0.95, 0.97), rough=0.9, sheen=0.5), bevel=0.08, sub=1)
        K.box("headb", (1.9, 0.12, 0.9), (0.9, 2.62, 0.6), m=ACC, bevel=0.04)
        for x in (0.5, 1.2): K.box("pillow", (0.5, 0.3, 0.14), (x, 2.4, 0.52), m=M("pil", (0.98, 0.98, 1.0), rough=0.9, sheen=0.6), bevel=0.06, sub=1)
        K.cyl("lamp", 0.13, 0.22, (-0.6, 2.4, 1.3), m=M("shade", (1, 0.9, 0.7), emit=(1, 0.85, 0.6), es=3.0))
        K.box("night", (0.4, 0.35, 0.5), (-0.6, 2.4, 0.25), m=M("nt", (0.85, 0.78, 0.68), rough=0.6))
        for i in range(30):
            K.sphere("star", 0.012, (rng.uniform(-1.6, 1.8), 2.56, rng.uniform(1.6, 2.6)), m=M(f"st{i}", (1, 0.95, 0.8), emit=(1, 0.95, 0.8), es=8), seg=8)
    elif kind == "xmas":
        for i in range(7):
            r = 0.55 - 0.07 * i
            K.cyl("tree", r, 0.3, (-1.3, 2.1, 0.25 + 0.27 * i), m=K.mat("pine", (0.08, 0.32, 0.14), rough=0.7), verts=12)
        for i in range(40):
            a = rng.uniform(0, 6.28); z = rng.uniform(0.3, 2.0); r = 0.55 * (1 - (z - 0.25) / 2.1)
            c = [(1, 0.85, 0.4), (1, 0.3, 0.3), (0.4, 0.7, 1)][i % 3]
            K.sphere("bulb", 0.022, (-1.3 + r * math.cos(a), 2.1 + r * math.sin(a), z), m=K.mat(f"bl{i}", c, emit=c, es=10), seg=8)
        K.box("sofa", (1.6, 0.6, 0.45), (1.0, 2.2, 0.22), m=K.mat("sofa", (0.25, 0.4, 0.3), rough=0.9, sheen=0.5), bevel=0.08, sub=1)
        for i in range(24):
            K.sphere("fairy", 0.012, (-0.4 + i * 0.09, 2.56, 2.2 + 0.08 * math.sin(i * 0.7)), m=K.mat(f"fl{i}", (1, 0.9, 0.6), emit=(1, 0.85, 0.5), es=12), seg=8)
    elif kind == "dressing":
        K.box("mirror", (0.9, 0.02, 1.1), (0.0, 2.56, 1.7), m=K.CHROME)
        for i in range(10):
            a = i / 10 * 2 * math.pi
            K.sphere("bulb", 0.03, (0.52 * math.cos(a), 2.54, 1.7 + 0.62 * math.sin(a)), m=K.mat(f"mb{i}", (1, 0.95, 0.85), emit=(1, 0.92, 0.8), es=10), seg=10)
        for i in range(5): K.cyl("bottle", 0.03, 0.1, (-1.1 + 0.12 * i, 2.4, 0.97), m=K.mat(f"pb{i}", accent if i % 2 else (0.9, 0.85, 0.75), rough=0.1, coat=1.0))
        K.box("vanity", (1.6, 0.5, 0.9), (-0.8, 2.35, 0.45), m=body_m, bevel=0.01)
    elif kind == "bath":
        K.box("mirror", (1.1, 0.02, 0.9), (0.2, 2.56, 1.75), m=K.CHROME)
        K.box("sink", (1.2, 0.5, 0.85), (0.2, 2.35, 0.42), m=K.WHITE, bevel=0.02)
        K.cyl("tap", 0.02, 0.2, (0.2, 2.45, 0.95), m=K.CHROME)
        K.box("lightbar", (1.0, 0.03, 0.04), (0.2, 2.54, 2.25), m=K.mat("lb", (1, 1, 1), emit=(1, 0.97, 0.92), es=8))
        K.cyl("plantpot", 0.1, 0.22, (1.1, 2.4, 0.96), m=K.POT)
        for i in range(8): K.sphere("leaf", 0.08, (1.1 + 0.06 * math.cos(i * 2.3), 2.4 + 0.06 * math.sin(i * 2.3), 1.2 + 0.04 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.4, 0.3, i), seg=12)
    else:  # office
        K.box("monitor", (0.7, 0.04, 0.42), (0.75, 1.9, 1.35), m=K.BLACK, bevel=0.01)
        K.box("screen", (0.66, 0.005, 0.38), (0.75, 1.875, 1.35), m=K.mat("scr", (0.3, 0.5, 0.9), emit=(0.35, 0.55, 1.0), es=2.5))
        K.box("desk", (1.6, 0.8, 0.04), (0.6, 2.0, 0.92), m=top_m)
        K.cyl("plantpot", 0.1, 0.22, (-1.1, 2.3, 0.11), m=K.POT)
        for i in range(10): K.sphere("leaf", 0.1, (-1.1 + 0.08 * math.cos(i * 2.3), 2.3 + 0.08 * math.sin(i * 2.3), 0.35 + 0.06 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.5, 0.4, i), seg=12)
        for i in range(4): K.box("files", (0.06, 0.25, 0.32), (-0.9 + 0.07 * i, 2.45, 1.75), m=K.mat(f"fi{i}", [(0.9, 0.3, 0.3), (0.3, 0.5, 0.9), (0.95, 0.8, 0.3), (0.3, 0.7, 0.5)][i], rough=0.6))
        K.box("shelf", (0.8, 0.3, 0.025), (-0.75, 2.45, 1.58), m=top_m)
    return NEON


# ------------------------------------------------------------------ containers
def container(kind, col):
    g = K.empty("cont", (0, 0, -5)); h = 0.1
    LQ = K.mat("contliq", col, rough=0.1, coat=0.6)
    if kind == "bowl":
        K.cyl("bowl", 0.075, 0.05, (0, 0, 0.025), parent=g, m=K.WHITE, verts=48, bevel=0.01)
        K.cyl("bfill", 0.068, 0.005, (0, 0, 0.049), parent=g, m=LQ, verts=48); h = 0.05
    elif kind == "mug":
        K.cyl("mug", 0.045, 0.1, (0, 0, 0.05), parent=g, m=K.mat("mugm", (0.95, 0.95, 0.93), rough=0.3, coat=0.6), verts=48, bevel=0.004)
        K.torus("handle", 0.03, 0.009, (0.05, 0, 0.055), parent=g, m=K.mat("mugm2", (0.95, 0.95, 0.93), rough=0.3), rot=(math.pi / 2, 0, 0))
        K.cyl("coffee", 0.041, 0.004, (0, 0, 0.094), parent=g, m=LQ, verts=48)
    elif kind == "shaker":
        K.cyl("shk", 0.04, 0.16, (0, 0, 0.08), parent=g, m=K.thin_glass("shk"), verts=48, cap=False)
        K.cyl("shkliq", 0.036, 0.09, (0, 0, 0.047), parent=g, m=LQ, verts=48)
        K.cyl("shkcap", 0.042, 0.035, (0, 0, 0.175), parent=g, m=K.BLACK, verts=48, bevel=0.005); h = 0.19
    elif kind == "glass":
        K.cyl("gl", 0.04, 0.13, (0, 0, 0.065), parent=g, m=K.thin_glass("gl"), verts=48, cap=False)
        K.cyl("glbase", 0.04, 0.004, (0, 0, 0.002), parent=g, m=K.thin_glass("glb"), verts=48)
        K.cyl("glliq", 0.036, 0.09, (0, 0, 0.047), parent=g, m=LQ, verts=48); h = 0.13
    elif kind == "plate":
        K.cyl("plate", 0.12, 0.015, (0, 0, 0.008), parent=g, m=K.WHITE, verts=48, bevel=0.005)
        fr = K.mat("fries", (0.95, 0.72, 0.25), rough=0.5)
        rr = random.Random(3)
        for i in range(18): K.box("fry", (0.012, 0.012, 0.08), (rr.uniform(-0.06, 0.06), rr.uniform(-0.06, 0.06), 0.025), parent=g, m=fr, rot=(rr.uniform(1.2, 1.9), 0, rr.uniform(0, 3.1)))
        h = 0.04
    elif kind == "pizza":
        K.cyl("pz", 0.14, 0.015, (0, 0, 0.008), parent=g, m=K.mat("dough", (0.88, 0.7, 0.42), rough=0.7), verts=48, bevel=0.006)
        K.cyl("sauce", 0.12, 0.004, (0, 0, 0.017), parent=g, m=K.mat("sauce", (0.75, 0.15, 0.08), rough=0.5), verts=48)
        rr = random.Random(4)
        for i in range(12): K.cyl("top", 0.016, 0.006, (rr.uniform(-0.09, 0.09), rr.uniform(-0.09, 0.09), 0.021), parent=g, m=K.mat(f"tp{i}", [(0.8, 0.2, 0.15), (0.2, 0.5, 0.2), (0.95, 0.9, 0.7)][i % 3]), verts=16)
        h = 0.025
    return g, h


# ------------------------------------------------------------------ main
def main(HERE):
    A = os.path.join(HERE, "assets")
    S = json.load(open(os.path.join(HERE, "spec.json")))
    args = K.parse_args(S.get("frames", "0-393"))
    W_ = json.load(open(os.path.join(A, "words.json")))
    TL, IDX = timeline(W_, S["kw"])
    K.init(); sc = K.sc
    accent = hexcol(S["accent"]); pcol = hexcol(S.get("particle", S["accent"]))
    NEON = room(S["room"], accent)

    # product
    from PIL import Image
    im = Image.open(os.path.join(A, "product.png")); ar = im.size[0] / im.size[1]
    PH = S["h"]; PW = PH * ar; TH = S.get("thick", min(0.35 * PW, 0.08))
    prod = K.extrude("prod", os.path.join(A, "product.png"), PH, TH, side_col=(0.9, 0.9, 0.9), round_k=S.get("round", 0.45))
    PROD_SPOT = Vector((0.32, 0.68, TOP)); HOOK = Vector((0, 0.62, TOP))
    # glowing turntable for the hook
    ped = K.empty("ped", HOOK)
    K.cyl("pedb", max(PW, TH) * 0.75 + 0.05, 0.05, (0, 0, 0.025), parent=ped, m=K.mat("pedm", (0.05, 0.05, 0.06), rough=0.15, coat=1.0), verts=64, bevel=0.01)
    K.torus("pedring", max(PW, TH) * 0.75 + 0.05, 0.006, (0, 0, 0.05), parent=ped, m=NEON)
    cont = None; CH_ = 0.1
    if S.get("container"):
        cont, CH_ = container(S["container"], hexcol(S.get("liquid", "#e8d2b0")))
    CONT_SPOT = Vector((-0.3, 0.68, TOP))
    # particles (pour / mist / sparkles / steam)
    PM = K.mat("part", pcol, rough=0.4, emit=pcol if S.get("glow_particles") else None, es=2.0 if S.get("glow_particles") else 0.0)
    parts = [K.sphere(f"p{i}", 0.006, (0, 0, -5), m=PM, seg=8) for i in range(40)]
    SPK = K.mat("spark", (1, 0.95, 0.8), emit=(1, 0.93, 0.75), es=25)
    sparks = [K.sphere(f"s{i}", 0.006, (0, 0, -5), m=SPK, seg=8) for i in range(14)]
    CONF = [K.mat(f"cf{i}", c, rough=0.4) for i, c in enumerate([accent, (1, 0.85, 0.3), (1, 1, 1)])]
    crng = random.Random(4)
    confetti = [(K.box(f"cf{i}", (0.012, 0.012, 0.002), (0, 0, -5), m=CONF[i % 3]), crng.uniform(-0.55, 0.55), crng.uniform(0.6, 1.4), crng.uniform(-0.3, 0.3), crng.uniform(0, 6)) for i in range(70)]
    zz = []
    if S["action"] == "hug":
        ZM = K.mat("zz", (1, 1, 1), emit=(0.9, 0.95, 1), es=4)
        for i in range(3): zz.append(K.box(f"z{i}", (0.03, 0.005, 0.03), (0, 0, -5), m=ZM, rot=(0, 0.4, 0)))

    ch = dict(female=False, hair="short", beard="stubble", tee=(0.93, 0.92, 0.88), shirt=(0.3, 0.4, 0.6), skin=(0.82, 0.6, 0.47), hair_col=(0.15, 0.09, 0.05), open_shirt=True)
    for k, v in S.get("char", {}).items(): ch[k] = tuple(v) if isinstance(v, list) else v
    K.build_character(**ch)
    SKIN0 = tuple(ch["skin"])

    # lights: soft key + fill + coloured rims (accent) for a punchier, more "premium" look
    K.world(tuple(hexcol(S.get("world", "#f2ece6"))), S.get("world_s", 0.2))
    K.area("key", (-1.4, -1.5, 2.6), (0.8, -0.5, 0), S.get("key", 200), 2.2, (1, 0.96, 0.92))
    K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 60, 3.0, (0.94, 0.95, 1))
    K.area("rimL", (-1.2, 2.0, 2.2), (-1.0, -0.5, 0), 260, 1.0, accent)
    K.area("rimR", (1.2, 2.0, 2.2), (-1.0, 0.5, 0), 200, 1.0, (1, 0.95, 0.9))
    K.point("prodglow", (0, 0.3, TOP + 0.4), 25, accent, 0.2)
    K.camera(30)

    mood = S.get("mood", "sad"); action = S["action"]

    def pour_parts(src, dst_z, u, spread=0.006, n=40, rate=0.014):
        for i, o in enumerate(parts[:n]):
            tt = (u - i * rate) % 0.55
            if u - i * rate < 0: o.location = (0, 0, -5); continue
            z = src.z - 3.5 * tt * tt
            if z < dst_z: o.location = (0, 0, -5); continue
            o.location = (src.x + spread * math.sin(i * 3.1), src.y + spread * math.cos(i * 2.3), z)

    def hide_parts():
        for o in parts: o.location = (0, 0, -5)

    def frame_state(t):
        C = K.CH.location
        K.idle(t)
        for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["problem"]
        ped.location = HOOK if t < TL["problem"] else Vector((0, 0, -5))
        prod.location = PROD_SPOT; prod.rotation_euler = (0, 0, -0.25)
        if cont: cont.location = CONT_SPOT; cont.rotation_euler = (0, 0, 0)
        hide_parts()
        for o in sparks: o.location = (0, 0, -5)
        for o in zz: o.location = (0, 0, -5)
        K.set_col(K.SKIN, SKIN0)
        for o, x, v, y, ph in confetti:
            tt = t - TL["price"] - 0.05
            if tt < 0 or tt > 3.5: o.location = (0, 0, -5); continue
            o.location = (C.x + x + 0.2 * tt * math.sin(ph), C.y - 0.6 + y, 2.2 + v * 0.3 - 0.35 * tt - 0.05 * math.sin(tt * 6 + ph)); o.rotation_euler = (tt * 5 + ph, tt * 3, ph)
        smile, mopen, brow, squint, look = 0.7, K.talk(t, W_, 0.5), 0.3, 0.0, (0, 0)
        HAND_R_REST = C + Vector((0.25, -0.3, 1.05)); HAND_L_REST = C + Vector((-0.25, -0.3, 1.05))

        if t < TL["problem"]:
            # HOOK: product spins on the glowing turntable, sparkles orbit
            u = t / max(TL["problem"], 0.5)
            prod.location = HOOK + Vector((0, 0, 0.05 + 0.01 * math.sin(t * 3)))
            prod.rotation_euler = (0, 0, -0.7 + 1.1 * ease(u))
            for i, o in enumerate(sparks):
                a = t * 1.6 + i * 2 * math.pi / len(sparks); r = max(PW, TH) * 0.8 + 0.06
                o.location = HOOK + Vector((r * math.cos(a), r * math.sin(a), 0.08 + PH * (0.5 + 0.45 * math.sin(a * 2 + i))))
        elif t < TL["use"]:
            # PROBLEM: mood pose, product waits on the counter
            u = t - TL["problem"]
            if mood == "tired":
                K.head.rotation_euler = (0.15, 0, 0.18); smile, brow, squint = 0.25, -0.3, 1.25
                K.free_arm("L", K.world_of(K.mouth, (-0.02, -0.05, -0.04)), fdir=(0.3, -0.2, 1), palm=(0, -1, 0), g=0.6)
                K.free_arm("R", HAND_R_REST, g=0.4)
            elif mood == "pain":
                K.head.rotation_euler = (0.1, 0, -0.25); smile, brow, squint = 0.15, -0.8, 1.1
                K.free_arm("L", K.world_of(K.head, (-0.05, 0.06, -0.03)), fdir=(0.3, 0.2, 1), palm=(1, 0, 0), g=0.3)
                K.free_arm("R", HAND_R_REST, g=0.4)
            elif mood == "annoyed":
                smile, brow, look = 0.12, -1.0, (0.4, 0)
                K.free_arm("L", C + Vector((0.1, -0.22, 1.26)), fdir=(1, 0, 0.2), palm=(0, 1, 0), g=0.6)
                K.free_arm("R", C + Vector((-0.1, -0.25, 1.22)), fdir=(-1, 0, 0.2), palm=(0, 1, 0), g=0.6)
            elif mood == "hot":
                smile, mopen, brow = 0.5, max(mopen, 0.6), 1.0
                K.free_arm("L", K.world_of(K.head, (-0.14, -0.06, 0.05)), fdir=(0.3, -0.3, 1), palm=(1, 0, 0), g=0.1)
                K.free_arm("R", K.world_of(K.head, (0.14, -0.06, 0.05)), fdir=(-0.3, -0.3, 1), palm=(-1, 0, 0), g=0.1)
            elif mood == "excited":
                smile, brow = 1.0, 0.9
                K.free_arm("L", C + Vector((-0.38, -0.25, 1.55 + 0.05 * math.sin(t * 9))), fdir=(0, -0.2, 1), palm=(0, -1, 0), g=0.0)
                K.free_arm("R", HAND_R_REST, g=0.4)
            else:  # sad / bored: chin on hand, sigh
                K.head.rotation_euler = (0.18, 0, 0.12); smile, brow, look = 0.12, -0.5, (0.5, -0.4)
                K.spine.rotation_euler = (0.12, 0, 0)
                K.free_arm("L", K.world_of(K.head, (0.0, -0.05, -0.06)), fdir=(0, 0, 1), palm=(0, 1, 0), g=0.7)
                K.free_arm("R", HAND_R_REST, g=0.4)
        elif t < TL["price"]:
            # USE: pick product up and perform the action
            u = t - TL["use"]; dur = TL["price"] - TL["use"]; k = ease(u / 0.45)
            grabR = vlerp(PROD_SPOT + Vector((0, 0, PH / 2)), C + Vector((0.2, -0.42, 1.3)), k)
            if action in ("pour", "pour_drink"):
                cup_at = C + Vector((-0.06, -0.45, 1.12))
                if cont:
                    ck = ease(u / 0.4); cp = vlerp(CONT_SPOT, cup_at, ck)
                    K.hold(None, "L", cp + Vector((0, 0, CH_ * 0.5)), approach=(-1, 0, 0), fdir=(0, -1, 0.2), g=0.9); cont.location = cp
                drink_t = 0.58 * dur if action == "pour_drink" else 99
                if u < drink_t:
                    pk = ease((u - 0.35) / 0.35)
                    pc = vlerp(grabR, cup_at + Vector((0.07, 0, CH_ + PH * 0.55 + 0.05)), pk)
                    K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.9)
                    prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, -1.9 * pk, 0)
                    if pk > 0.9: pour_parts(cup_at + Vector((0.0, 0, CH_ + 0.2)), cup_at.z + CH_ * 0.6, u - 0.7)
                    smile, look = 0.9, (0.3, -0.9); K.head.rotation_euler = (0.22, 0, 0)
                else:
                    # drink: cup to mouth, product held low in R
                    dk = ease((u - drink_t) / 0.35)
                    pc = C + Vector((0.24, -0.38, 1.12))
                    K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.9); prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, 0, -0.2)
                    mw = K.world_of(K.mouth)
                    cp = vlerp(cup_at, mw + Vector((0.0, -0.06, -CH_ * 0.85)), dk)
                    if cont:
                        K.hold(None, "L", cp + Vector((0, 0, CH_ * 0.5)), approach=(-1, 0, 0), fdir=(0, -1, 0.2), g=0.9)
                        cont.location = cp; cont.rotation_euler = (-1.1 * dk, 0, 0)
                    smile, squint = 0.6, 0.9 * dk
            elif action == "spray":
                pc = vlerp(grabR, C + Vector((0.16, -0.36, 1.48)), ease((u - 0.3) / 0.4))
                K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.85); prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, 0.5, 0.4)
                K.free_arm("L", HAND_L_REST, g=0.4)
                if u > 0.8:
                    for i, o in enumerate(parts):
                        tt = (u - 0.8 - i * 0.02) % 0.9
                        o.location = pc + Vector((-0.06 - 0.25 * tt + 0.01 * math.sin(i), -0.02 * math.cos(i * 2), 0.06 + 0.05 * math.sin(i * 1.7) * tt))
                smile, squint, look = 1.0, 0.8, (-0.4, 0); K.head.rotation_euler = (-0.1, 0, -0.15)
            elif action == "apply":
                top = K.world_of(K.head, (0.02, -0.02, 0.32))
                if u < dur * 0.55:
                    pk = ease((u - 0.3) / 0.4); pc = vlerp(grabR, top + Vector((0.04, 0, PH * 0.4)), pk)
                    K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.85); prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, -2.6 * pk, 0)
                    if pk > 0.9: pour_parts(top + Vector((0, 0, 0.1)), top.z - 0.05, u - 0.7, n=12, rate=0.06)
                    K.free_arm("L", HAND_L_REST, g=0.4); look = (0, 1)
                else:
                    pc = C + Vector((0.24, -0.38, 1.12))
                    K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.9); prod.location = pc - Vector((0, 0, PH / 2))
                    K.free_arm("L", top + Vector((-0.02 + 0.03 * math.sin(t * 14), -0.02, -0.04)), fdir=(0.2, 0.2, 1), palm=(0, 0, -1), g=0.4)
                    smile, squint = 1.0, 0.8
            elif action == "hug":
                hk = ease((u - 0.2) / 0.45)
                pc = vlerp(PROD_SPOT + Vector((0, 0, PH / 2)), C + Vector((0.0, -0.34, 1.3)), hk)
                prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0.15 * hk, 0, 0)
                K.free_arm("L", pc + Vector((-PW / 2 - 0.02, 0, 0)), fdir=(0.3, -0.2, 1), palm=(1, 0, 0), g=0.5)
                K.free_arm("R", pc + Vector((PW / 2 + 0.02, 0, 0)), fdir=(-0.3, -0.2, 1), palm=(-1, 0, 0), g=0.5)
                K.head.rotation_euler = (0.1, 0, 0.3 * hk); smile, squint = 0.9, 1.3 * hk
                for i, o in enumerate(zz):
                    tt = (u * 0.7 + i * 0.33) % 1.0
                    o.location = K.world_of(K.head, (0.15 + 0.15 * tt, -0.05, 0.25 + 0.3 * tt)); o.scale = (0.6 + tt, 1, 0.6 + tt)
            else:  # show / fire: both hands present it, turning gently
                hk = ease((u - 0.15) / 0.45)
                pc = vlerp(PROD_SPOT + Vector((0, 0, PH / 2)), C + Vector((0.0, -0.45, 1.25)), hk)
                prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, 0, 0.35 * math.sin(u * 1.5) * hk)
                K.free_arm("L", pc + Vector((-PW / 2 - 0.02, 0, -PH * 0.1)), fdir=(0.3, -0.3, 1), palm=(1, 0, 0), g=0.5)
                K.free_arm("R", pc + Vector((PW / 2 + 0.02, 0, -PH * 0.1)), fdir=(-0.3, -0.3, 1), palm=(-1, 0, 0), g=0.5)
                smile, brow, look = 1.0, 0.7, (0, -0.4)
                if cont and S["container"] in ("plate", "pizza"):
                    cont.location = Vector((-0.05, 0.58, TOP))
                if action == "fire" and u > dur * 0.45:
                    fk = ease((u - dur * 0.45) / 0.4)
                    K.set_col(K.SKIN, tuple(vlerp(SKIN0, (0.95, 0.25, 0.2), fk)))
                    smile, mopen, brow, squint = 0.4, 0.9, 1.0, 0.6
                    for i, o in enumerate(parts[:24]):
                        tt = (u * 1.3 + i * 0.05) % 0.8; side = 1 if i % 2 else -1
                        o.location = K.world_of(K.head, (side * (0.13 + 0.1 * tt), 0.0, 0.14 + 0.3 * tt))
        elif t < TL["cta"]:
            # PRICE: product next to the face, confetti rain
            u = t - TL["price"]; k = ease(u / 0.35)
            big = PW > 0.24
            pc = vlerp(C + Vector((0.2, -0.42, 1.25)), C + (Vector((0.12, -0.42, 1.3)) if big else Vector((0.24, -0.36, 1.55))) + Vector((0, 0, 0.02 * math.sin(t * 5))), k)
            K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.9); prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, 0, -0.15)
            K.free_arm("L", C + Vector((-0.36, -0.28, 1.5 + 0.04 * math.sin(t * 8))), fdir=(0, -0.2, 1), palm=(0, -1, 0), g=0.0)
            smile, brow, mopen = 1.0, 1.0, max(mopen, 0.25)
            for i, o in enumerate(sparks):
                a = t * 2.2 + i * 2 * math.pi / len(sparks)
                o.location = pc + Vector((0.11 * math.cos(a), 0.05 * math.sin(a) - 0.03, 0.1 * math.sin(a * 1.3)))
        else:
            # CTA: hold product, point down-left
            pc = C + Vector((0.25, -0.4, 1.3 + 0.02 * math.sin(t * 6)))
            K.hold(None, "R", pc, approach=(1, 0, 0), fdir=(0, -1, 0.2), g=0.9); prod.location = pc - Vector((0, 0, PH / 2)); prod.rotation_euler = (0, 0, -0.2)
            K.free_arm("L", C + Vector((-0.42, -0.42, 1.05)), point=True)
            smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
        K.face(smile, mopen, brow, look, squint, t)
        K.set_shot(*shot(t))

    def shot(t):
        C = K.CH.location
        if t < TL["problem"]:
            u = t / max(TL["problem"], 0.5); a = -0.55 + 0.75 * ease(u); c = HOOK + Vector((0, 0, 0.05 + PH * 0.5))
            d = max(0.5, PH * 2.1 + 0.18)
            cam_p = c + Vector((d * math.sin(a), -d * math.cos(a), 0.12 - 0.08 * u))
            return cam_p, c, c + (cam_p - c).normalized() * 0.03, 4.0
        if t < TL["use"]:
            u = (t - TL["problem"]) / max(TL["use"] - TL["problem"], 0.5)
            return C + Vector((0.05, -1.15 + 0.15 * u, 1.62)), C + Vector((0.0, -0.2, 1.42)), C + Vector((0, -0.3, 1.5)), 2.4
        if t < TL["price"]:
            u = (t - TL["use"]) / max(TL["price"] - TL["use"], 0.5)
            if action in ("hug", "show", "fire"):
                return C + Vector((0.12 - 0.1 * u, -1.25, 1.55)), C + Vector((0.0, -0.3, 1.36)), C + Vector((0, -0.45, 1.3)), 2.6
            return C + Vector((0.25 - 0.2 * u, -1.15, 1.5)), C + Vector((0.02, -0.35, 1.3)), C + Vector((0.05, -0.42, 1.3)), 2.6
        if t < TL["cta"]:
            u = (t - TL["price"]) / max(TL["cta"] - TL["price"], 0.5)
            return C + Vector((0.08, -1.0 - 0.2 * u, 1.62)), C + Vector((0.08, -0.2, 1.5)), C + Vector((0.12, -0.36, 1.52)), 2.4
        u = (t - TL["cta"]) / max(TL["end"] - TL["cta"], 0.5)
        return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

    def anchor_objs():
        return dict(prod=K.world_of(prod, (0, 0, PH * 0.5)), head=K.world_of(K.head, (0, 0, 0.14)))

    K.setup_render(args, exposure=S.get("exposure", -0.8))
    K.run(args, HERE, frame_state, anchor_objs)
