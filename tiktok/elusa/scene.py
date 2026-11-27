"""Elusa 501 extrait (unisex, sweet) – cosy Christmas living room: spray, ingredients orbit, snow, buy-3 deal, CTA.
python3 scene.py --test 0.8,3.0,5.0,6.5,8.5,11.5,14.0 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args("0-366")
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(spray=2.1, notes=3.9, market=7.25, deal=10.25, cta=13.2, end=15.25)
K.init(); sc = K.sc

# ------------------------------------------------------------------ cosy living room
WALL = K.mat("wall", (0.86, 0.8, 0.7), rough=0.9)
WOOD = K.wood_mat("wood", (0.4, 0.25, 0.13), (0.58, 0.4, 0.22), scale=2.0, dist=6)
FLOOR = K.wood_mat("floor", (0.35, 0.22, 0.12), (0.5, 0.33, 0.18), scale=3.0)
FAIRY = K.mat("fairy", (1, 0.8, 0.45), emit=(1.0, 0.75, 0.4), es=10.0)
KNIT = K.mat("knit", (0.7, 0.12, 0.12), rough=0.95, sheen=0.6)
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
# string lights draped across the wall
lights = []
for j in range(2):
    for i in range(26):
        x = -2.0 + i * 0.16; z = 2.25 - j * 0.45 - 0.12 * math.sin(math.pi * ((i % 13) / 12))
        lights.append(K.sphere("fl", 0.018, (x, 2.55, z), m=FAIRY, seg=8))
# window with snowy night
K.box("wf", (1.1, 0.07, 1.2), (-0.7, 2.57, 1.45), m=K.WHITE, bevel=0.01)
K.plane("pane", 1.0, 1.1, (-0.7, 2.53, 1.45), (math.pi / 2, 0, 0), K.mat("snowsky", (0.2, 0.3, 0.5), emit=(0.25, 0.35, 0.6), es=1.2))
# shelf with candles, wreath
K.box("shelf", (0.9, 0.18, 0.03), (0.9, 2.5, 1.4), m=WOOD, bevel=0.005)
for i in range(3):
    K.cyl("candle", 0.03, 0.08 + 0.04 * i, (0.65 + i * 0.22, 2.5, 1.455 + 0.02 * i), m=K.WHITE)
    K.sphere("flame", 0.012, (0.65 + i * 0.22, 2.5, 1.5 + 0.04 * i + 0.02), (1, 1, 1.8), m=FAIRY, seg=8)
K.torus("wreath", 0.22, 0.06, (0.9, 2.56, 1.95), m=K.mat("wr", (0.08, 0.3, 0.12), rough=0.8), rot=(math.pi / 2, 0, 0))
for i in range(8):
    a = i * math.pi / 4; K.sphere("berry", 0.02, (0.9 + 0.22 * math.cos(a), 2.52, 1.95 + 0.22 * math.sin(a)), m=K.mat("ber", (0.8, 0.05, 0.08), rough=0.2, coat=1), seg=10)
# table in front
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=WOOD, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=WOOD, bevel=0.005)
TOP = 0.9225
K.box("runner", (2.5, 0.25, 0.004), (0, 0.72, TOP + 0.002), m=KNIT)
K.cyl("mug", 0.04, 0.09, (-0.7, 0.8, TOP + 0.045), m=KNIT)
for i in range(5): K.sphere("cookie", 0.03, (0.65 + 0.06 * i, 0.82, TOP + 0.008), (1, 1, 0.25), m=K.mat(f"ck{i}", (0.7, 0.45, 0.2), rough=0.8), seg=16)

# ------------------------------------------------------------------ bottles
BOT_H = 0.12
def make_bottle(name):
    root = K.empty(name, (0, 0, 0))
    m = K.revolve(name + "_m", os.path.join(A, "product.png"), BOT_H, step=3); m.parent = root
    return root
bottle = make_bottle("bottle"); extra = [make_bottle(f"extra{i}") for i in range(2)]
hero = K.empty("hero", (0.0, 0.6, TOP))
K.cyl("ped", 0.075, 0.025, (0, 0, 0.0125), parent=hero, m=WOOD, verts=48, bevel=0.004)
EXTRA_SPOT = [Vector((-0.18, 0.58, TOP)), Vector((0.18, 0.58, TOP))]
MIST = K.mat("mist", (1, 1, 1), rough=0.5, alpha=0.35)
mist = [K.sphere(f"mist{i}", 0.006, (0, 0, -5), m=MIST, seg=8) for i in range(30)]
mrng = random.Random(5); MIST_V = [(mrng.uniform(-0.25, 0.25), mrng.uniform(-0.25, 0.25), mrng.uniform(0.0, 1.0)) for _ in mist]

# ingredients that orbit around
ORANGE = K.mat("orange", (1.0, 0.5, 0.08), rough=0.4, sss=0.3); ORIN = K.mat("orin", (1.0, 0.72, 0.25), rough=0.3, sss=0.4)
VAN = K.mat("vanilla", (0.12, 0.07, 0.04), rough=0.5); ANISE = K.mat("anise", (0.35, 0.18, 0.1), rough=0.7); CINN = K.mat("cinn", (0.5, 0.25, 0.12), rough=0.8)
def orange_slice():
    r = K.empty("ors", (0, 0, -5)); K.cyl("o1", 0.03, 0.008, (0, 0, 0), parent=r, m=ORANGE, verts=32); K.cyl("o2", 0.026, 0.0085, (0, 0, 0), parent=r, m=ORIN, verts=32); return r
def vanilla():
    r = K.empty("van", (0, 0, -5)); K.cyl("v", 0.004, 0.11, (0, 0, 0), parent=r, m=VAN, verts=12, rot=(0, math.pi / 2, 0)); return r
def anise():
    r = K.empty("ani", (0, 0, -5))
    for i in range(8): K.sphere("a", 0.008, (0.013 * math.cos(i * math.pi / 4), 0.013 * math.sin(i * math.pi / 4), 0), (1.6, 0.8, 0.6), parent=r, m=ANISE, rot=(0, 0, i * math.pi / 4), seg=10)
    return r
def cinnamon():
    r = K.empty("cin", (0, 0, -5)); K.cyl("c", 0.006, 0.08, (0, 0, 0), parent=r, m=CINN, verts=12, rot=(0, math.pi / 2, 0.3)); return r
INGR = [(orange_slice(), "orange"), (orange_slice(), "orange"), (vanilla(), "vanilla"), (vanilla(), "vanilla"), (anise(), "spice"), (anise(), "spice"), (cinnamon(), "spice")]
SNOWM = K.mat("snow", (1, 1, 1), rough=0.6, emit=(1, 1, 1), es=0.6)
srng = random.Random(8)
snow = [(K.sphere(f"sn{i}", 0.006, (0, 0, -5), m=SNOWM, seg=8), srng.uniform(-0.8, 0.8), srng.uniform(0.3, 1.2), srng.uniform(0, 1), srng.uniform(0.25, 0.45)) for i in range(70)]

# ------------------------------------------------------------------ character
K.build_character(female=True, hair="long", beard=None, tee=(0.12, 0.32, 0.2), shirt=(0.12, 0.32, 0.2), shirt2=(0.1, 0.25, 0.16),
                  hair_col=(0.55, 0.36, 0.18), skin=(0.85, 0.63, 0.5), iris=(0.2, 0.35, 0.45), open_shirt=False)
K.torus("scarf", 0.07, 0.03, (0, -0.005, 0.01), parent=K.neck, m=KNIT)

K.world((0.95, 0.85, 0.7), 0.3)
K.area("key", (-1.2, -1.4, 2.5), (0.8, -0.45, 0), 240, 2.2, (1, 0.9, 0.78))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 100, 3.0, (1.0, 0.9, 0.85))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 160, 1.0, (1.0, 0.75, 0.45))
K.camera(32)

def nozzle(): return K.world_of(bottle, (0, -0.02, BOT_H * 0.88))

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["spray"]
    bottle.location = hero.location + Vector((0, 0, 0.025)); bottle.rotation_euler = (0, 0, 0)
    for i, e in enumerate(extra): e.location = EXTRA_SPOT[i] if t >= TL["deal"] - 0.05 else Vector((0, 0, -5)); e.rotation_euler = (0, 0, 0.3 * (i - 0.5))
    for o in mist: o.location = (0, 0, -5)
    for o, _ in INGR: o.location = (0, 0, -5)
    K.set_emit(FAIRY, 10.0 + (8.0 * ease((t - TL["market"]) / 0.4) if t >= TL["market"] else 0))
    snowk = ease((t - TL["market"]) / 0.3) * (1 - ease((t - TL["deal"]) / 0.3))
    for o, x, y, ph, v in snow:
        if snowk <= 0.01: o.location = (0, 0, -5); continue
        z = 2.3 - ((t * v + ph * 1.6) % 1.6)
        o.location = (K.CH.location.x + x + 0.03 * math.sin(t * 2 + ph * 9), K.CH.location.y - y, z); o.scale = (snowk,) * 3
    def orbit(center, t0, rad=0.2, which=None, starts=None):
        for i, (o, kind) in enumerate(INGR):
            st = (starts or {}).get(kind, t0)
            if t < st: continue
            k = back((t - st) / 0.35)
            a = i * 2 * math.pi / len(INGR) + (t - t0) * 1.1
            o.location = center + Vector((rad * k * math.cos(a), -0.06 + 0.04 * math.sin(a * 2 + t), rad * 0.85 * k * math.sin(a)))
            o.rotation_euler = (t * 1.3 + i, t * 0.7, i); o.scale = (max(k, 0.01),) * 3
    smile, mopen, brow, squint, look = 0.7, K.talk(t, W_, 0.45), 0.3, 0.0, (0, 0)
    if t < TL["spray"]:
        bottle.rotation_euler = (0, 0, -0.6 + 1.2 * ease(t / TL["spray"]))
        orbit(hero.location + Vector((0, 0, 0.025 + BOT_H * 0.5)), 0.2, 0.14)
    elif t < TL["notes"]:
        u = t - TL["spray"]; k = ease(u / 0.35)
        p = vlerp(hero.location + Vector((0, 0, 0.025 + BOT_H * 0.4)), C + Vector((0.16, -0.38, 1.38)), k)
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0.5 * k)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        wr = C + Vector((-0.05, -0.42, 1.3))
        K.free_arm("L", wr, fdir=(1, -0.3, 0.2), palm=(0, 0, 1), g=0.2)
        n0 = nozzle()
        for i, o in enumerate(mist):
            v = MIST_V[i]; tt = u - 0.5 - v[2] * 0.4
            if 0 < tt < 0.6:
                o.location = n0 + Vector((-0.3 * tt + v[0] * tt, v[1] * tt * 0.3, -0.05 * tt + v[0] * 0.05 * tt)); s = 1 + 4 * tt; o.scale = (s, s, s)
        smile, look, brow = 0.8, (0.3, -0.6), 0.5; K.head.rotation_euler = (0.15, 0, 0)
    elif t < TL["market"]:
        # sniff the wrist – notes appear one by one around her
        u = t - TL["notes"]
        p = C + Vector((0.24, -0.34, 1.12))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.04, -0.2, 1.36)), fdir=(1, -0.2, 0.4), palm=(0, 1, 0), g=0.2)
        orbit(K.world_of(K.head, (0, 0, 0.12)), TL["notes"], 0.27, starts=dict(orange=T[6] - 0.1, vanilla=T[7] - 0.1, spice=T[9] - 0.1))
        smile, squint, brow = 0.95, 1.0 if u < 1.6 else 0.3, 0.7; K.head.rotation_euler = (0.08, 0, 0.12 * math.sin(u * 2))
        if u >= 1.6: look = (math.sin(u * 2) * 0.8, 0.4)
    elif t < TL["deal"]:
        # smells like a Christmas market – lights up, snow, she sways
        u = t - TL["market"]
        p = C + Vector((0.2, -0.32, 1.52))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0.3)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.38, -0.3, 1.45 + 0.05 * math.sin(u * 4))), fdir=(-0.3, -0.3, 1), palm=(0, -1, 0), g=0.1)
        K.spine.rotation_euler = (0, 0.06 * math.sin(u * 3), 0.15 * math.sin(u * 2)); K.head.rotation_euler = (-0.12, 0.08 * math.sin(u * 3), 0)
        smile, mopen, squint, brow, look = 1.0, max(mopen, 0.25), 0.5, 0.8, (0, 0.6)
    elif t < TL["cta"]:
        # buy three – gathers the three bottles
        u = t - TL["deal"]
        k = ease(u / 0.4)
        bp = vlerp(C + Vector((0.2, -0.32, 1.4)), hero.location + Vector((0, 0, 0.025 + BOT_H * 0.4)), k)
        if u < 0.5:
            K.hold(bottle, "R", bp, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = bp - Vector((0, 0, BOT_H * 0.4))
        else:
            for i, e in enumerate(extra): e.location = EXTRA_SPOT[i] + Vector((0, 0, 0.01 * abs(math.sin(u * 8 + i))))
            K.free_arm("R", EXTRA_SPOT[1] + Vector((0.1, -0.02, 0.1)), fdir=(-1, -0.2, -0.4), palm=(-1, 0, 0), g=0.3)
        K.free_arm("L", EXTRA_SPOT[0] + Vector((-0.1, -0.02, 0.1)), fdir=(1, -0.2, -0.4), palm=(1, 0, 0), g=0.3)
        smile, mopen, brow, look = 1.0, max(mopen, 0.2), 1.0, (0, -0.7); K.head.rotation_euler = (0.2, 0, 0)
    else:
        p = C + Vector((0.27, -0.36, 1.56 + 0.03 * math.sin(t * 6)))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["spray"]:
        a = -0.45 + 0.6 * t / TL["spray"]; c = hero.location + Vector((0, 0, 0.025 + BOT_H * 0.5))
        cam_p = c + Vector((0.38 * math.sin(a), -0.38 * math.cos(a), 0.03))
        return cam_p, c + Vector((0, 0, -0.005)), c + (cam_p - c).normalized() * 0.025, 5.6
    if t < TL["notes"]:
        return C + Vector((0.05, -1.15, 1.55)), C + Vector((0.03, -0.1, 1.45)), C + Vector((0, -0.38, 1.45)), 2.8
    if t < TL["market"]:
        u = (t - TL["notes"]) / (TL["market"] - TL["notes"])
        return C + Vector((0.1 - 0.15 * u, -1.15 + 0.15 * u, 1.62)), C + Vector((0.0, 0, 1.55)), C + Vector((0, -0.12, 1.6)), 2.6
    if t < TL["deal"]:
        u = (t - TL["market"]) / (TL["deal"] - TL["market"])
        return C + Vector((0.0, -1.7 + 0.2 * u, 1.6)), C + Vector((0.0, 0, 1.5)), C + Vector((0, -0.2, 1.55)), 3.0
    if t < TL["cta"]:
        return C + Vector((0.0, -1.55, 1.66)), C + Vector((0.0, -0.45, 1.36)), C + Vector((0, -0.8, 1.0)), 3.6
    u = (t - TL["cta"]) / 2.0
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(bottle=K.world_of(bottle, (0, 0, BOT_H * 0.55)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.35)
K.run(args, HERE, frame_state, anchor_objs)
