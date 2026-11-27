"""FGN Tunnelblick caffeine pouches – late-night desk: tired -> pouch -> wide awake typing, CTA.
python3 scene.py --test 0.8,3.5,5.0,6.6,7.8,8.6,10.5,13.4,15.2 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args()
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(tired=1.95, coffee=5.95, pouch=7.3, facts=8.9, zack=12.7, cta=14.5, end=16.15)
K.init(); sc = K.sc

# ------------------------------------------------------------------ home office at night
WALL = K.mat("wall", (0.22, 0.27, 0.38), rough=0.9)
DESK = K.wood_mat("desk", (0.35, 0.22, 0.12), (0.5, 0.33, 0.18), scale=2.0, dist=6)
FLOOR = K.wood_mat("floor", (0.25, 0.17, 0.1), (0.38, 0.26, 0.15), scale=3.0)
NIGHT = K.mat("night", (0.05, 0.08, 0.2), emit=(0.08, 0.12, 0.3), es=1.5)
CITY = K.mat("city", (1, 0.8, 0.5), emit=(1.0, 0.8, 0.45), es=6.0)
SCREEN = K.mat("screen", (0.6, 0.8, 1.0), emit=(0.55, 0.75, 1.0), es=2.5)
CODE = K.mat("code", (0.4, 1.0, 0.6), emit=(0.4, 1.0, 0.6), es=4.0)
MUG = [K.mat(f"mug{i}", c, rough=0.3, coat=0.6) for i, c in enumerate([(0.9, 0.9, 0.88), (0.15, 0.2, 0.35), (0.8, 0.3, 0.2), (0.95, 0.8, 0.3), (0.2, 0.5, 0.35)])]
COFFEE = K.mat("coffee", (0.12, 0.06, 0.03), rough=0.1)
LAMPM = K.mat("lampm", (0.1, 0.1, 0.11), rough=0.3, metal=0.6)
LAMPB = K.mat("lampb", (1, 0.85, 0.6), emit=(1.0, 0.8, 0.5), es=20.0)
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
# night window with city lights
for (w, h, x, z) in ((1.6, 0.06, -0.6, 2.4), (1.6, 0.06, -0.6, 0.95), (0.06, 1.5, -1.4, 1.67), (0.06, 1.5, 0.2, 1.67), (0.04, 1.5, -0.6, 1.67)):
    K.box("wf", (w, 0.07, h), (x, 2.57, z), m=K.WHITE)
K.plane("pane", 1.58, 1.42, (-0.6, 2.598, 1.67), (math.pi / 2, 0, 0), NIGHT)
rng = random.Random(2)
for i in range(40):
    K.box("cl", (0.012, 0.004, 0.016), (rng.uniform(-1.35, 0.15), 2.592, rng.uniform(1.0, 1.75)), m=CITY)
# poster + plant + shelf
K.box("poster", (0.5, 0.02, 0.7), (1.2, 2.58, 1.7), m=K.mat("poster", (0.85, 0.35, 0.3), rough=0.6), bevel=0.005)
K.cyl("plantpot", 0.12, 0.25, (1.9, 2.25, 0.125), m=K.POT)
for i in range(10):
    a = i * 2.3; K.sphere("leaf", 0.1, (1.9 + 0.08 * math.cos(a), 2.25 + 0.08 * math.sin(a), 0.38 + 0.05 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.5 * math.sin(a), 0.5 * math.cos(a), a), seg=12)
# desk in front of the character
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=K.BLACK, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=DESK, bevel=0.005)
TOP = 0.9225
# laptop facing the character (we see its back + glow), keyboard side toward him
lap = K.empty("laptop", (0.0, 0.95, TOP))
K.box("lbase", (0.34, 0.23, 0.014), (0, 0, 0.007), parent=lap, m=K.CHROME, bevel=0.004)
lid = K.empty("lid", (0, -0.11, 0.014), lap); lid.rotation_euler = (-1.85, 0, 0)
K.box("lback", (0.34, 0.012, 0.22), (0, 0, 0.11), parent=lid, m=K.CHROME, bevel=0.004)
K.plane("lscreen", 0.31, 0.19, (0, 0.0065, 0.11), (math.pi / 2, 0, math.pi), SCREEN, parent=lid)
K.sphere("logo", 0.012, (0, -0.0065, 0.12), (1, 0.2, 1), parent=lid, m=K.WHITE)
# desk lamp
K.cyl("lampbase", 0.07, 0.015, (-0.8, 0.95, TOP + 0.008), m=LAMPM)
K.cyl("lamparm", 0.008, 0.35, (-0.8, 0.95, TOP + 0.18), m=LAMPM, rot=(0.25, 0, 0))
K.cyl("lamphead", 0.06, 0.09, (-0.8, 0.91, TOP + 0.36), m=LAMPM, rot=(0.9, 0, 0), cap=False)
K.sphere("lampbulb", 0.025, (-0.8, 0.885, TOP + 0.34), m=LAMPB)
# coffee mugs (the "fifth coffee")
MUGS = []
for i, (x, y) in enumerate(((-0.55, 0.65), (-0.38, 0.85), (0.45, 0.82), (0.62, 0.62), (0.28, 0.56))):
    mg = K.empty(f"mug{i}", (x, y, TOP))
    K.cyl("mugb", 0.04, 0.09, (0, 0, 0.045), parent=mg, m=MUG[i], cap=True)
    K.cyl("mugc", 0.036, 0.004, (0, 0, 0.082), parent=mg, m=COFFEE)
    K.torus("handle", 0.025, 0.007, (0.045, 0, 0.045), parent=mg, m=MUG[i], rot=(math.pi / 2, 0, 0))
    MUGS.append(mg)
MUG_POS = [m.location.copy() for m in MUGS]

# ------------------------------------------------------------------ product: the can
def gen_tex(name, path, rough=0.35):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(path); tx.extension = "EXTEND"
    nt.links.new(tc.outputs["Generated"], tx.inputs["Vector"]); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = 0.5
    return m
CAN_R, CAN_H = 0.034, 0.02
LIDM = gen_tex("lidtex", os.path.join(A, "lid.png"))
SIDE = K.mat("side", (0.95, 0.95, 0.95), rough=0.35, coat=0.4)
RING = K.mat("ring", (0.6, 0.85, 0.75), rough=0.3, coat=0.5)
can = K.empty("can", (0, 0, 0))
K.cyl("canb", CAN_R * 0.97, CAN_H * 0.7, (0, 0, CAN_H * 0.35), parent=can, m=SIDE, verts=64, bevel=0.002)
canlid = K.empty("canlid", (0, 0, CAN_H * 0.62), can)
K.cyl("lidside", CAN_R, CAN_H * 0.4, (0, 0, CAN_H * 0.2), parent=canlid, m=RING, verts=64, bevel=0.002, cap=False)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=CAN_R, fill_type="NGON", location=(0, 0, CAN_H * 0.4))
top = bpy.context.object; top.parent = canlid; top.data.materials.append(LIDM)
POUCHM = K.mat("pouch", (0.97, 0.97, 0.96), rough=0.9, sheen=0.4)
pouches = [K.box(f"p{i}", (0.03, 0.014, 0.006), (0.0, -0.012 + 0.012 * (i % 3), CAN_H * 0.45 + 0.006 * (i // 3)), parent=can, m=POUCHM, bevel=0.003) for i in range(6)]
pouch = K.box("pouch", (0.03, 0.014, 0.006), (0, 0, -5), m=POUCHM, bevel=0.003)
hero = K.empty("hero", (0.0, 0.6, TOP))
K.cyl("coaster", 0.06, 0.01, (0, 0, 0.005), parent=hero, m=K.BLACK, verts=48, bevel=0.003)

# ------------------------------------------------------------------ character
K.build_character(hair="short", beard="stubble", tee=(0.15, 0.17, 0.25), shirt=(0.8, 0.55, 0.15), shirt2=(0.2, 0.22, 0.3), hair_col=(0.15, 0.1, 0.06))
bags = [K.sphere("bag", 0.018, (x * 0.041, -0.11, 0.112), (1.3, 0.35, 0.6), parent=K.head, m=K.mat("bagm", (0.55, 0.4, 0.45), rough=0.6)) for x in (-1, 1)]

K.world((0.15, 0.18, 0.3), 0.25)
K.area("key", (-1.0, -1.2, 2.4), (0.8, -0.4, 0), 140, 2.0, (1.0, 0.85, 0.65))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 60, 3.0, (0.6, 0.7, 1.0))
scr = K.area("screenl", (0.0, 0.85, 1.2), (-1.2, 0, 0), 18, 0.35, (0.6, 0.78, 1.0))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 100, 1.0, (0.5, 0.6, 1.0))
K.point("lampl", (-0.8, 0.85, TOP + 0.3), 25, (1.0, 0.8, 0.5), 0.05)
K.camera(32)

def mouth_w(): return K.world_of(K.mouth)

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["tired"]
    awake = ease((t - TL["facts"] - 0.4) / 3.2)
    if t >= TL["zack"]: awake = 1.0
    for b in bags: b.hide_render = awake > 0.8 or t < TL["tired"]
    can.location = hero.location + Vector((0, 0, 0.01)); can.rotation_euler = (0, 0, 0); canlid.location = (0, 0, CAN_H * 0.62); canlid.rotation_euler = (0, 0, 0)
    pouch.location = (0, 0, -5); pouch.parent = None
    for i, m in enumerate(MUGS): m.location = MUG_POS[i]
    K.set_emit(SCREEN, 2.5 + (2.0 * (0.5 + 0.5 * math.sin(t * 30)) if t >= TL["zack"] else 0))
    smile, mopen, brow, squint, look = 0.6, K.talk(t, W_, 0.5), 0.0, 0.0, (0, 0)
    sleepy = (1 - awake) if t >= TL["tired"] else 0
    if t < TL["tired"]:
        k = ease((t - 0.7) / 0.3) * (1 - ease((t - 1.6) / 0.25))
        can.location = hero.location + Vector((0, 0, 0.01 + 0.03 * k)); can.rotation_euler = (0, 0, 2 * math.pi * ease((t - 0.2) / 1.4))
        canlid.location = (0, 0, CAN_H * 0.62 + 0.03 * k)
    elif t < TL["coffee"]:
        # Monday, deadline – head propped on hand, eyes half shut, nodding off
        u = t - TL["tired"]
        nod = max(0, math.sin(u * 2.2)) ** 3
        K.upd(); K.free_arm("R", K.world_of(K.head, (0.075, -0.06, 0.0)) + Vector((0.0, 0.0, -0.05)), fdir=(-0.2, 0.1, 1), palm=(-1, 0, 0.3), g=0.6)
        K.free_arm("L", C + Vector((-0.2, -0.45, 1.0)), fdir=(0.3, -1, -0.3), g=0.5)
        K.spine.rotation_euler = (0.18, 0, 0); K.head.rotation_euler = (0.25 + 0.25 * nod, 0.15, 0.1)
        smile, brow, squint, look = 0.2, -0.6, 1.35 + 0.4 * nod, (0, -0.4)
    elif t < TL["pouch"]:
        # "instead of the fifth coffee" – push a mug away with a sigh, reach for the can
        u = t - TL["coffee"]
        k = ease(u / 0.6)
        mg = MUGS[4]; mg.location = MUG_POS[4] + Vector((0.18 * k, 0.12 * k, 0))
        K.free_arm("R", mg.location + Vector((-0.03, -0.06, 0.06)), fdir=(1, 0.3, -0.2), palm=(1, 0, 0), g=0.2)
        if u > 0.7:
            kk = ease((u - 0.7) / 0.5)
            cp = vlerp(hero.location + Vector((0, 0, 0.02)), C + Vector((-0.12, -0.45, 1.3)), kk)
            K.hold(can, "L", cp, approach=(0, 0, -1), fdir=(0.3, -1, 0.05), obj_rot=(0.5 * kk, 0, 0), g=0.5, palm_off=0.03)
        else: K.free_arm("L", C + Vector((-0.22, -0.45, 1.0)), g=0.4)
        smile, brow, squint, look = 0.2, 0.2, 1.1, (0.5, -0.6)
    elif t < TL["facts"]:
        # lid off, pinch a pouch, under the lip
        u = t - TL["pouch"]
        cp = C + Vector((-0.12, -0.45, 1.3))
        K.hold(can, "L", cp, approach=(0, 0, -1), fdir=(0.3, -1, 0.05), obj_rot=(0.5, 0, 0), g=0.5, palm_off=0.03)
        mw = mouth_w()
        if u < 0.4:
            k = ease(u / 0.35); canlid.location = (0.0, 0.05 * k, CAN_H * 0.62 + 0.04 * k); canlid.rotation_euler = (-1.2 * k, 0, 0)
            K.free_arm("R", K.world_of(canlid, (0.02, -0.03, 0.02)), fdir=(-1, -0.3, -0.2), g=0.7)
        else:
            canlid.location = (0.0, 0.05, CAN_H * 0.62 + 0.04); canlid.rotation_euler = (-1.2, 0, 0)
            k = ease((u - 0.45) / 0.7)
            pp = vlerp(K.world_of(can, (0, 0, CAN_H * 0.6)), mw + Vector((0, -0.012, 0.012)), k)
            K.hold(pouch, "R", pp, approach=(0.3, 0.3, -1), fdir=(-0.7, -0.6, 0.4), g=0.3, palm_off=0.02)
            pouch.location = pp; pouch.rotation_euler = (1.2, 0, 0)
            if u > 1.35: pouch.location = (0, 0, -5)
        smile, brow, squint, look, mopen = 0.3, 0.4, 0.9, (0.6, -0.8), max(mopen, 0.35 if u > 0.9 else 0)
    elif t < TL["zack"]:
        # facts: can toward camera, eyes slowly opening
        u = t - TL["facts"]
        cp = C + Vector((0.2, -0.42, 1.5))
        K.hold(can, "R", cp, approach=(0, 1, 0), fdir=(0, -0.2, 1), obj_rot=(1.35, math.pi, 0), g=0.12, palm_off=0.05)
        canlid.location = (0, 0, CAN_H * 0.62); canlid.rotation_euler = (0, 0, 0)
        K.free_arm("L", C + Vector((-0.22, -0.4, 1.32)), point=True) if u < 2.2 else K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
        smile, brow, squint, look = 0.6 + 0.4 * awake, 0.3 + 0.6 * awake, 1.0 - awake, (0.2, -0.1)
        K.spine.rotation_euler = (0.18 * (1 - awake), 0, 0)
    elif t < TL["cta"]:
        # ZACK – Tunnelblick: wide eyes, typing at light speed
        u = t - TL["zack"]
        for side, x in (("L", -0.12), ("R", 0.12)):
            ty = 0.012 * math.sin(u * 60 + (0 if side == "L" else 1.7))
            K.free_arm(side, Vector((x, 0.86, TOP + 0.05 + abs(ty))), fdir=(0, 1, -0.4), palm=(0, 0, -1), g=0.35)
        K.spine.rotation_euler = (0.22, 0, 0); K.head.rotation_euler = (0.1, 0, 0)
        smile, mopen, brow, squint, look = 0.9, 0.15, 1.0, 0.0, (0, -0.5)
        hold_can = False
    else:
        p = C + Vector((0.27, -0.36, 1.56 + 0.03 * math.sin(t * 6)))
        K.hold(can, "R", p, approach=(0, 1, 0), fdir=(0, -0.2, 1), obj_rot=(1.35, math.pi, 0), g=0.12, palm_off=0.05)
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t, blink=sleepy < 0.5)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["tired"]:
        a = -0.35 + 0.5 * t / TL["tired"]; c = hero.location + Vector((0, 0, 0.02))
        cam_p = c + Vector((0.17 * math.sin(a), -0.17 * math.cos(a), 0.15))
        return cam_p, c, c + (cam_p - c).normalized() * 0.0, 4.0
    if t < TL["coffee"]:
        u = (t - TL["tired"]) / (TL["coffee"] - TL["tired"])
        return C + Vector((0.25, -1.5 + 0.35 * u, 1.5)), C + Vector((0.0, -0.1, 1.38)), C + Vector((0, -0.25, 1.45)), 2.6
    if t < TL["facts"]:
        return C + Vector((-0.1, -1.05, 1.52)), C + Vector((-0.05, -0.2, 1.4)), C + Vector((-0.05, -0.4, 1.4)), 2.8
    if t < TL["zack"]:
        return C + Vector((0.1, -1.05, 1.56)), C + Vector((0.08, -0.2, 1.47)), C + Vector((0.2, -0.42, 1.5)), 3.2
    if t < TL["cta"]:
        u = (t - TL["zack"]) / (TL["cta"] - TL["zack"])
        return C + Vector((0.45 - 0.1 * u, -1.15 + 0.15 * u, 1.62)), C + Vector((0.0, -0.3, 1.35)), C + Vector((0, -0.2, 1.45)), 3.5
    u = (t - TL["cta"]) / 1.6
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(can=K.world_of(can, (0, 0, CAN_H * 0.5)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.15)
K.run(args, HERE, frame_state, anchor_objs)
