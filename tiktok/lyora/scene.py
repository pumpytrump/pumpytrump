"""LYORA Nerion extrait – evening dressing room, Christmas: spray, compliments, gift box, CTA.
python3 scene.py --test 0.8,3.2,4.8,7.5,10.5,12.8,14.2,15.8 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args("0-401")
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(spray=2.6, ask=3.75, extrait=6.0, elegant=9.3, gift=11.95, you=13.62, cta=15.0, end=16.75)
K.init(); sc = K.sc

# ------------------------------------------------------------------ evening dressing room + Christmas
WALL = K.mat("wall", (0.28, 0.12, 0.16), rough=0.85)                 # deep plum
PANEL = K.mat("panel", (0.22, 0.09, 0.12), rough=0.6)
GOLD = K.mat("gold", (0.95, 0.75, 0.4), rough=0.2, metal=1.0)
MARBLE = K.mat("marble", (0.95, 0.94, 0.93), rough=0.1, coat=1.0)
FLOOR = K.wood_mat("floor", (0.2, 0.12, 0.07), (0.32, 0.2, 0.12), scale=3.0)
BULB = K.mat("bulb", (1, 0.9, 0.7), emit=(1.0, 0.85, 0.6), es=9.0)
FIR = K.mat("fir", (0.06, 0.25, 0.12), rough=0.7, sheen=0.3)
FAIRY = K.mat("fairy", (1, 0.8, 0.4), emit=(1.0, 0.75, 0.35), es=14.0)
ORN = [K.mat(f"orn{i}", c, rough=0.15, metal=0.7) for i, c in enumerate([(0.85, 0.1, 0.15), (0.95, 0.75, 0.35), (0.9, 0.9, 0.95)])]
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
for x in (-1.5, -0.5, 0.5, 1.5):
    K.box("pan", (0.8, 0.02, 1.0), (x, 2.585, 0.6), m=PANEL, bevel=0.01)
    K.box("panr", (0.82, 0.03, 0.02), (x, 2.58, 1.11), m=GOLD)
# vanity mirror with bulbs (behind, right)
K.box("mframe", (0.9, 0.04, 1.1), (0.75, 2.56, 1.75), m=GOLD, bevel=0.01)
K.box("mirror", (0.8, 0.01, 1.0), (0.75, 2.535, 1.75), m=K.mat("mirr", (0.9, 0.9, 0.92), rough=0.02, metal=1.0))
for i in range(5):
    K.sphere("bulb", 0.03, (0.33, 2.52, 1.3 + i * 0.22), m=BULB, seg=16); K.sphere("bulb", 0.03, (1.17, 2.52, 1.3 + i * 0.22), m=BULB, seg=16)
# Christmas tree (left)
rng = random.Random(3)
for i in range(5):
    r = 0.55 - i * 0.1; bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0.02, depth=0.55, vertices=24, location=(-1.25, 2.1, 0.45 + i * 0.32))
    o = bpy.context.object; o.data.materials.append(FIR)
    for p in o.data.polygons: p.use_smooth = True
for i in range(40):
    h = rng.uniform(0.25, 1.9); r = max(0.05, 0.55 * (1 - (h - 0.2) / 1.85)) + 0.01; a = rng.uniform(0, 2 * math.pi)
    K.sphere("fl", 0.012, (-1.25 + r * math.cos(a), 2.1 + r * math.sin(a), h), m=FAIRY, seg=8)
for i in range(14):
    h = rng.uniform(0.3, 1.6); r = max(0.05, 0.5 * (1 - (h - 0.2) / 1.85)) + 0.02; a = rng.uniform(0, 2 * math.pi)
    K.sphere("orn", 0.035, (-1.25 + r * math.cos(a), 2.1 + r * math.sin(a), h), m=ORN[i % 3], seg=16)
K.sphere("star", 0.06, (-1.25, 2.1, 2.08), (1, 0.4, 1), m=K.mat("starm", (1, 0.85, 0.4), emit=(1, 0.8, 0.4), es=10))
# vanity table in front
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=PANEL, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=MARBLE, bevel=0.005)
TOP = 0.9225
K.cyl("tray", 0.16, 0.012, (-0.62, 0.78, TOP + 0.006), m=GOLD, verts=48)
K.cyl("lip", 0.018, 0.08, (-0.66, 0.78, TOP + 0.05), m=K.mat("lipst", (0.6, 0.05, 0.1), rough=0.3, coat=1.0))
K.cyl("cream", 0.04, 0.04, (-0.56, 0.75, TOP + 0.032), m=K.WHITE)
K.box("pearls", (0.2, 0.02, 0.012), (0.62, 0.7, TOP + 0.006), m=K.mat("pearl", (0.95, 0.93, 0.9), rough=0.15, coat=1.0), bevel=0.006, rot=(0, 0, 0.3))
# gift box with ribbon
GIFT = K.mat("gift", (0.08, 0.08, 0.1), rough=0.4, coat=0.5)
RIB = K.mat("ribbon", (0.75, 0.1, 0.15), rough=0.3, sheen=0.5)
gift = K.empty("gift", (0, 0, 0))
K.box("gb", (0.16, 0.12, 0.08), (0, 0, 0.04), parent=gift, m=GIFT, bevel=0.003)
gl = K.empty("giftlid", (0, 0, 0.08), gift)
K.box("gl", (0.165, 0.125, 0.02), (0, 0, 0.01), parent=gl, m=GIFT, bevel=0.003)
K.box("r1", (0.168, 0.02, 0.022), (0, 0, 0.01), parent=gl, m=RIB); K.box("r2", (0.02, 0.128, 0.022), (0, 0, 0.01), parent=gl, m=RIB)
for s_ in (-1, 1): K.sphere("bow", 0.025, (s_ * 0.025, 0, 0.03), (1.2, 0.5, 0.7), parent=gl, m=RIB, rot=(0, s_ * 0.5, 0))
GIFT_SPOT = Vector((0.42, 0.66, TOP))

# ------------------------------------------------------------------ the bottle
BOT_H = 0.13
bottle = K.empty("bottle", (0, 0, 0))
bm_ = K.extrude("lyora_m", os.path.join(A, "product.png"), BOT_H, 0.042, round_k=0.6); bm_.parent = bottle
hero = K.empty("hero", (0.0, 0.6, TOP))
K.cyl("ped", 0.08, 0.03, (0, 0, 0.015), parent=hero, m=GOLD, verts=48, bevel=0.004)
MIST = K.mat("mist", (1, 1, 1), rough=0.5, alpha=0.35)
mist = [K.sphere(f"mist{i}", 0.006, (0, 0, -5), m=MIST, seg=8) for i in range(30)]
mrng = random.Random(5); MIST_V = [(mrng.uniform(-0.25, 0.25), mrng.uniform(-0.25, 0.25), mrng.uniform(0.0, 1.0)) for _ in mist]
SPARK = K.mat("spark", (1, 0.9, 0.6), emit=(1, 0.85, 0.5), es=20.0)
sparks = [K.sphere(f"sp{i}", 0.004, (0, 0, -5), m=SPARK, seg=8) for i in range(18)]

# ------------------------------------------------------------------ character
K.build_character(female=True, hair="long", beard=None, tee=(0.04, 0.035, 0.04), shirt=(0.04, 0.035, 0.04), shirt2=(0.03, 0.03, 0.035),
                  hair_col=(0.1, 0.06, 0.04), skin=(0.82, 0.6, 0.48), iris=(0.25, 0.15, 0.06), open_shirt=False)
K.cyl("necklace", 0.058, 0.006, (0, -0.005, 0.0), parent=K.neck, m=GOLD, cap=False)

K.world((0.4, 0.3, 0.3), 0.25)
K.area("key", (-1.2, -1.4, 2.5), (0.8, -0.45, 0), 230, 2.2, (1, 0.9, 0.8))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 90, 3.0, (1.0, 0.85, 0.8))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 170, 1.0, (1.0, 0.75, 0.5))
K.point("treel", (-1.1, 1.8, 1.2), 50, (1.0, 0.7, 0.35), 0.5)
K.camera(32)

def nozzle(): return K.world_of(bottle, (0, -0.02, BOT_H * 0.82))

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["spray"]
    bottle.location = hero.location + Vector((0, 0, 0.03)); bottle.rotation_euler = (0, 0, 0)
    gift.location = GIFT_SPOT; gift.rotation_euler = (0, 0, -0.3); gl.location = (0, 0, 0.08); gl.rotation_euler = (0, 0, 0)
    for o in mist + sparks: o.location = (0, 0, -5)
    smile, mopen, brow, squint, look = 0.7, K.talk(t, W_, 0.4), 0.2, 0.0, (0, 0)
    def sparkle(center, t0, rad=0.12):
        for i, o in enumerate(sparks):
            ph = (t - t0) * 1.2 + i / len(sparks)
            a = i * 2.4 + t * 1.5; r = rad * (0.6 + 0.4 * math.sin(i * 1.3 + t * 2))
            o.location = center + Vector((r * math.cos(a), -0.02 + 0.03 * math.sin(a), r * math.sin(a) * 0.8 + 0.04 * math.sin(ph * 6)))
            k = abs(math.sin(ph * math.pi)); o.scale = (k, k, k)
    if t < TL["spray"]:
        bottle.rotation_euler = (0, 0, -0.6 + 1.2 * ease(t / TL["spray"]))
        sparkle(hero.location + Vector((0, 0, 0.03 + BOT_H * 0.5)), 0, 0.1)
    elif t < TL["ask"]:
        # pick up and spray the neck
        u = t - TL["spray"]; k = ease(u / 0.35)
        p = vlerp(hero.location + Vector((0, 0, 0.03 + BOT_H * 0.4)), C + Vector((0.16, -0.35, 1.5)), k)
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0.6 * k)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
        n0 = nozzle()
        for i, o in enumerate(mist):
            v = MIST_V[i]; tt = u - 0.45 - v[2] * 0.4
            if 0 < tt < 0.6:
                o.location = n0 + Vector((-0.25 * tt + v[0] * tt, -0.02 + v[1] * tt * 0.4, 0.05 * tt)); s = 1 + 4 * tt; o.scale = (s, s, s)
        smile, squint, look = 0.8, 0.6 if u > 0.45 else 0.0, (0.5, 0.2)
        K.head.rotation_euler = (-0.1, 0, -0.3 * ease((u - 0.3) / 0.3))
    elif t < TL["extrait"]:
        # "everyone asks: what are you wearing?" – eyes closed, blissful sniff of the wrist, then a smug look around
        u = t - TL["ask"]
        p = C + Vector((0.24, -0.34, 1.12))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        mw = K.world_of(K.mouth)
        if u < 1.1:
            K.free_arm("L", C + Vector((-0.04, -0.2, 1.36)), fdir=(1, -0.2, 0.4), palm=(0, 1, 0), g=0.2)
            smile, squint, brow = 0.9, 1.0, 0.6; K.head.rotation_euler = (0.15, 0, 0.1)
        else:
            K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
            smile, brow, look = 1.0, 0.9, (math.sin(u * 3) * 0.9, 0); K.head.rotation_euler = (-0.05, 0, 0.25 * math.sin(u * 3))
    elif t < TL["elegant"]:
        # extrait = most intense – bottle presented next to the face, sparkles
        u = t - TL["extrait"]
        p = C + Vector((0.13, -0.42, 1.6))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0.15 * math.sin(u * 2))); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
        sparkle(K.world_of(bottle, (0, 0, BOT_H * 0.5)), TL["extrait"], 0.11)
        smile, brow, look = 0.9, 0.8, (0.5, 0.3); K.head.rotation_euler = (0, 0, -0.15)
    elif t < TL["gift"]:
        # elegant, classy, unforgettable – slow turn with the bottle at the shoulder
        u = t - TL["elegant"]
        p = C + Vector((0.2, -0.3, 1.55))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0.3)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", K.world_of(K.head, (-0.1, 0.0, 0.0)), fdir=(0.2, 0.1, 1), palm=(1, 0, 0), g=0.3)
        K.spine.rotation_euler = (0, 0, 0.25 * math.sin(u * 1.4)); K.head.rotation_euler = (-0.1, 0, -0.3 * math.sin(u * 1.4))
        smile, squint, brow = 0.85, 0.4, 0.5
    elif t < TL["you"]:
        # the perfect Christmas present – bottle goes into the gift box
        u = t - TL["gift"]
        ko = ease(u / 0.3); gl.location = (0.0, 0.1 * ko, 0.08 + 0.06 * ko); gl.rotation_euler = (-0.9 * ko, 0, 0)
        kin = ease((u - 0.35) / 0.5)
        bp = vlerp(C + Vector((0.2, -0.4, 1.45)), K.world_of(gift, (0, 0, 0.02)) + Vector((0, 0, BOT_H * 0.4)), kin)
        if u < 1.15:
            K.hold(bottle, "R", bp, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, -0.3 * kin)); bottle.location = bp - Vector((0, 0, BOT_H * 0.4))
        else:
            bottle.location = K.world_of(gift, (0, 0, 0.005)); bottle.rotation_euler = (0, 0, -0.3)
            K.free_arm("R", C + Vector((0.25, -0.35, 1.1)), g=0.3)
        K.free_arm("L", GIFT_SPOT + Vector((-0.12, -0.02, 0.06)), fdir=(1, 0, -0.3), palm=(1, 0, 0), g=0.6)
        smile, brow, look = 1.0, 0.7, (0.6, -0.8); K.head.rotation_euler = (0.2, 0, 0)
    elif t < TL["cta"]:
        # "...or just for you" – takes it back out, points at the viewer
        u = t - TL["you"]
        p = C + Vector((0.22, -0.4, 1.4))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.12, -0.62, 1.45)), point=True)
        gl.location = (0.0, 0.1, 0.14); gl.rotation_euler = (-0.9, 0, 0)
        smile, brow, mopen, look = 1.0, 0.6, max(mopen, 0.15), (0, 0)
    else:
        p = C + Vector((0.27, -0.36, 1.56 + 0.03 * math.sin(t * 6)))
        K.hold(bottle, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); bottle.location = p - Vector((0, 0, BOT_H * 0.4))
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        gl.location = (0.0, 0.1, 0.14); gl.rotation_euler = (-0.9, 0, 0)
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["spray"]:
        a = -0.45 + 0.6 * t / TL["spray"]; c = hero.location + Vector((0, 0, 0.03 + BOT_H * 0.5))
        cam_p = c + Vector((0.36 * math.sin(a), -0.36 * math.cos(a), 0.03))
        return cam_p, c + Vector((0, 0, -0.005)), c + (cam_p - c).normalized() * 0.022, 5.6
    if t < TL["extrait"]:
        return C + Vector((0.08, -1.05, 1.62)), C + Vector((0.04, 0, 1.52)), C + Vector((0, -0.12, 1.58)), 2.6
    if t < TL["elegant"]:
        u = (t - TL["extrait"]) / (TL["elegant"] - TL["extrait"])
        return C + Vector((0.12, -0.95 + 0.1 * u, 1.62)), C + Vector((0.08, -0.2, 1.57)), C + Vector((0.13, -0.42, 1.6)), 3.0
    if t < TL["gift"]:
        u = (t - TL["elegant"]) / (TL["gift"] - TL["elegant"])
        return C + Vector((-0.25 + 0.4 * u, -1.2, 1.58)), C + Vector((0.0, 0, 1.5)), C + Vector((0, -0.15, 1.55)), 2.6
    if t < TL["you"]:
        return C + Vector((0.5, -1.4, 1.62)), C + Vector((0.33, -0.3, 1.3)), C + Vector((0.42, -0.7, 1.1)), 3.6
    if t < TL["cta"]:
        return C + Vector((0.0, -1.1, 1.6)), C + Vector((0.0, 0, 1.5)), C + Vector((0, -0.2, 1.55)), 2.6
    u = (t - TL["cta"]) / 1.75
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(bottle=K.world_of(bottle, (0, 0, BOT_H * 0.55)), gift=K.world_of(gift, (0, 0, 0.1)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.3)
K.run(args, HERE, frame_state, anchor_objs)
