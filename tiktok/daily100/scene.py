"""More DAILY100 – bright morning kitchen: open the monthly box, sachet into water bottle, shake, drink, -50% shock, CTA.
python3 scene.py --test 0.8,2.5,4.2,5.2,6.5,8.2,10.0,11.5,13.5,15.5 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args("0-390")
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(box=1.65, sachet=3.6, mix=4.85, drink=5.65, weeks=7.05, tease=9.35, price=10.5, cta=14.7, end=16.25)
K.init(); sc = K.sc

# ------------------------------------------------------------------ bright morning kitchen
WALL = K.mat("wall", (0.93, 0.86, 0.9), rough=0.9)                   # soft blush
TILE = K.brick_mat("tile", (0.97, 0.96, 0.96), (0.93, 0.92, 0.93), (0.75, 0.73, 0.75), scale=14)
OAK = K.wood_mat("oak", (0.62, 0.45, 0.3), (0.8, 0.64, 0.45), scale=2.0, dist=5)
FLOOR = K.wood_mat("floor", (0.55, 0.4, 0.27), (0.72, 0.56, 0.38), scale=3.0)
COUNTER = K.mat("counter", (0.97, 0.97, 0.97), rough=0.15, coat=0.8)
SKY = K.mat("sky", (0.9, 0.95, 1.0), emit=(1.0, 0.95, 0.85), es=6.0)
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
for (w, h, x, z) in ((1.4, 0.05, -0.8, 2.35), (1.4, 0.05, -0.8, 1.05), (0.05, 1.3, -1.5, 1.7), (0.05, 1.3, -0.1, 1.7)):
    K.box("wf", (w, 0.06, h), (x, 2.57, z), m=K.WHITE)
K.plane("pane", 1.38, 1.28, (-0.8, 2.598, 1.7), (math.pi / 2, 0, 0), SKY)
K.box("backsplash", (1.6, 0.02, 0.6), (0.9, 2.585, 1.2), m=TILE)
K.box("bcounter", (1.6, 0.5, 0.9), (0.9, 2.35, 0.45), m=K.WHITE, bevel=0.01)
K.box("bctop", (1.65, 0.55, 0.04), (0.9, 2.35, 0.92), m=OAK, bevel=0.005)
for i, c in enumerate([(0.9, 0.3, 0.45), (0.95, 0.75, 0.3), (0.4, 0.65, 0.4)]):
    K.sphere("fruit", 0.05, (0.6 + i * 0.12, 2.3, 0.99), m=K.mat(f"fr{i}", c, rough=0.4, sss=0.2), seg=16)
K.cyl("kettle", 0.08, 0.2, (1.25, 2.35, 1.04), m=K.mat("kettle", (0.95, 0.75, 0.8), rough=0.3, coat=0.6))
K.cyl("plantpot", 0.12, 0.25, (1.9, 2.25, 0.125), m=K.POT)
for i in range(10):
    a = i * 2.3; K.sphere("leaf", 0.1, (1.9 + 0.08 * math.cos(a), 2.25 + 0.08 * math.sin(a), 0.38 + 0.05 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.5 * math.sin(a), 0.5 * math.cos(a), a), seg=12)
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=K.WHITE, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=COUNTER, bevel=0.005)
TOP = 0.9225
K.cyl("vase", 0.04, 0.14, (-0.75, 0.85, TOP + 0.07), m=K.thin_glass("vase"))
for i in range(3): K.sphere("tulip", 0.025, (-0.75 + 0.03 * (i - 1), 0.85, TOP + 0.25 + 0.02 * i), (1, 1, 1.3), m=K.mat(f"tl{i}", (0.95, 0.4, 0.55), rough=0.4), seg=12)

# ------------------------------------------------------------------ the DAILY100 box
PINK = K.mat("pink", (0.86, 0.45, 0.62), rough=0.45, coat=0.3)
MAG = K.mat("mag", (0.6, 0.15, 0.4), rough=0.45, coat=0.3)
BW, BD, BH = 0.3, 0.22, 0.11
box = K.empty("box", (0, 0, 0))
K.box("bbody", (BW, BD, BH), (0, 0, BH / 2), parent=box, m=PINK, bevel=0.002)
K.plane("bfront", BW * 0.98, BH * 0.95, (0, -BD / 2 - 0.0012, BH / 2), (math.pi / 2, 0, 0), K.tex_mat("sidet", os.path.join(A, "side.png"), rough=0.45, coat=0.3), parent=box)
K.plane("bweeks", BW * 0.82, BD * 0.95, (-BW * 0.08, 0, BH + 0.0012), (0, 0, 0), K.tex_mat("weekst", os.path.join(A, "weeks.png"), rough=0.5, coat=0.2), parent=box)
K.cyl("bbottle", 0.022, 0.19, (BW * 0.42, 0, BH + 0.01), parent=box, m=K.BLACK, rot=(math.pi / 2, 0, 0))
hinge = K.empty("hinge", (0, BD / 2, BH), box)
K.box("blid", (BW, BD, 0.008), (0, -BD / 2, 0.004), parent=hinge, m=PINK, bevel=0.002)
lidtip = K.empty("lidtip", (0, -BD, 0.01), hinge)
K.plane("blidin", BW * 0.96, BD * 0.94, (0, -BD / 2, -0.0002), (math.pi, 0, 0), K.tex_mat("lidt", os.path.join(A, "lid.png"), rough=0.5), parent=hinge)
BOX_SPOT = Vector((0.0, 0.62, TOP))
# sachet
SACH = K.tex_mat("sacht", os.path.join(A, "sachet.png"), rough=0.35, coat=0.6)
sachet = K.empty("sachet", (0, 0, -5))
K.box("sbody", (0.06, 0.004, 0.09), (0, 0, 0), parent=sachet, m=K.mat("sachb", (0.85, 0.4, 0.58), rough=0.35, coat=0.6), bevel=0.0015)
K.plane("sfront", 0.058, 0.088, (0, -0.0025, 0), (math.pi / 2, 0, 0), SACH, parent=sachet)
# drinking bottle (black More bottle) with water -> pink smoothie
bottle = K.empty("bottle", (0, 0, 0))
BOT = K.thin_glass("botglass", (0.95, 0.95, 0.97))
K.cyl("bglass", 0.035, 0.17, (0, 0, 0.085), parent=bottle, m=BOT, cap=False, verts=48)
K.cyl("bbase", 0.035, 0.004, (0, 0, 0.002), parent=bottle, m=BOT, verts=48)
bcap = K.cyl("bcap", 0.037, 0.03, (0, 0, 0.185), parent=bottle, m=K.BLACK, verts=48, bevel=0.004)
LIQ = K.mat("liq", (0.85, 0.92, 1.0), rough=0.05, trans=0.6, ior=1.33)
bliq = K.cyl("bliq", 0.032, 1.0, (0, 0, 0.5), parent=bottle, m=LIQ, verts=48)
BOTTLE_SPOT = Vector((0.35, 0.62, TOP))
POWDER = K.mat("powder", (0.9, 0.4, 0.6), rough=0.9)
pdots = [K.sphere(f"pd{i}", 0.0035, (0, 0, -5), m=POWDER, seg=8) for i in range(30)]
CONF = [K.mat(f"cf{i}", c, rough=0.4) for i, c in enumerate([(0.95, 0.3, 0.55), (1, 0.85, 0.3), (1, 1, 1)])]
crng = random.Random(4)
confetti = [(K.box(f"cf{i}", (0.012, 0.012, 0.002), (0, 0, -5), m=CONF[i % 3]), crng.uniform(-0.5, 0.5), crng.uniform(0.6, 1.4), crng.uniform(-0.3, 0.3), crng.uniform(0, 6)) for i in range(60)]

# ------------------------------------------------------------------ character
K.build_character(female=True, hair="long", beard=None, tee=(0.3, 0.45, 0.72), shirt=(0.3, 0.45, 0.72), shirt2=(0.22, 0.34, 0.56),
                  hair_col=(0.6, 0.42, 0.22), skin=(0.85, 0.64, 0.52), iris=(0.25, 0.4, 0.3), open_shirt=False)

K.world((0.98, 0.95, 0.95), 0.35)
K.area("key", (-1.4, -1.4, 2.6), (0.8, -0.5, 0), 260, 2.5, (1, 0.96, 0.92))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 120, 3.0, (0.96, 0.95, 1))
K.area("window", (-0.8, 3.2, 1.7), (-math.pi / 2, 0, 0), 350, 1.6, (1, 0.95, 0.85))
sunl = bpy.data.lights.new("sun", "SUN"); sunl.energy = 3.5; sunl.color = (1, 0.92, 0.8); sunl.angle = 0.05
so = bpy.data.objects.new("sun", sunl); sc.collection.objects.link(so); so.rotation_euler = (math.radians(-55), math.radians(-28), 0)
K.camera(32)

def set_liq(h):
    bliq.scale = (1, 1, max(h, 0.0005)); bliq.location.z = 0.004 + max(h, 0.0005) / 2

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["box"]
    box.location = BOX_SPOT; box.rotation_euler = (0, 0, 0)
    lid_open = ease((t - 0.5) / 0.6) if t < TL["box"] else ease((t - TL["box"] - 0.3) / 0.5)
    if TL["box"] <= t < TL["box"] + 0.3: lid_open = 1 - ease((t - TL["box"]) / 0.01)
    hinge.rotation_euler = (-1.95 * lid_open, 0, 0)
    bottle.location = BOTTLE_SPOT; bottle.rotation_euler = (0, 0, 0); bcap.location.z = 0.185
    sachet.location = (0, 0, -5)
    for o in pdots: o.location = (0, 0, -5)
    pink_k = ease((t - TL["mix"] - 0.35) / 0.5)
    K.set_col(LIQ, tuple(vlerp((0.85, 0.92, 1.0), (0.85, 0.25, 0.45), pink_k)))
    LIQ.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = lerp(0.6, 0.05, pink_k)
    drunk = clamp((t - TL["drink"] - 0.6) / 0.7) * 0.35
    set_liq(0.12 * (1 - drunk))
    for o, x, v, y, ph in confetti:
        tt = t - TL["price"] - 0.05
        if tt < 0 or tt > 3.5: o.location = (0, 0, -5); continue
        o.location = (C.x + x + 0.2 * tt * math.sin(ph), C.y - 0.6 + y, 2.2 + v * 0.3 - 0.35 * tt - 0.05 * math.sin(tt * 6 + ph)); o.rotation_euler = (tt * 5 + ph, tt * 3, ph)
    smile, mopen, brow, squint, look = 0.7, K.talk(t, W_, 0.45), 0.3, 0.0, (0, 0)
    if t < TL["box"]:
        box.rotation_euler = (0, 0, -0.5 + 1.0 * ease(t / TL["box"]))
    elif t < TL["sachet"]:
        # opens the box, peeks in
        u = t - TL["box"]
        if u < 0.85: K.free_arm("R", K.world_of(lidtip) + Vector((0.04, -0.02, 0.03)), fdir=(0, 0.3, -1), palm=(0, 0, -1), g=0.4)
        else: K.free_arm("R", C + Vector((0.25, -0.35, 1.05)), g=0.4)
        K.free_arm("L", BOX_SPOT + Vector((-BW / 2 - 0.03, 0, BH * 0.7)), fdir=(1, 0, -0.3), palm=(1, 0, 0), g=0.4)
        smile, brow, look = 0.9, 0.8, (0, -0.9); K.head.rotation_euler = (0.25, 0, 0); K.spine.rotation_euler = (0.1, 0, 0)
    elif t < TL["mix"]:
        # takes one sachet out of "week 1"
        u = t - TL["sachet"]; k = ease(u / 0.6)
        sp = vlerp(K.world_of(box, (-BW * 0.28, -BD * 0.2, BH - 0.01)), C + Vector((0.05, -0.45, 1.42)), k)
        K.hold(sachet, "R", sp, approach=(1, 0, 0), fdir=(0, -0.3, 1), g=0.7, palm_off=0.02, obj_rot=(0, 0, 0)); sachet.location = sp
        K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
        smile, brow, look = 1.0, 0.9, (0.2, -0.3 + 0.4 * k)
    elif t < TL["drink"]:
        # tears it and pours the powder into the bottle
        u = t - TL["mix"]
        top = BOTTLE_SPOT + Vector((0, 0, 0.24))
        bcap.location.z = 0.32
        sp = top + Vector((-0.02, 0, 0.04))
        K.hold(sachet, "R", sp, approach=(1, 0, 0), fdir=(0, -0.3, 1), g=0.7, palm_off=0.02, obj_rot=(0, -2.2 * ease(u / 0.2), 0)); sachet.location = sp
        K.free_arm("L", BOTTLE_SPOT + Vector((-0.07, 0, 0.09)), fdir=(1, 0, 0.1), palm=(1, 0, 0), g=0.8)
        for i, o in enumerate(pdots):
            tt = u - 0.2 - i * 0.012
            if tt > 0:
                z = top.z - 4.9 * tt * tt
                if z > BOTTLE_SPOT.z + 0.13: o.location = (top.x + 0.006 * math.sin(i * 3), top.y + 0.006 * math.cos(i * 2), z)
        smile, look = 0.8, (0.3, -0.9); K.head.rotation_euler = (0.25, 0, 0)
    elif t < TL["weeks"]:
        # quick shake, then drink
        u = t - TL["drink"]
        mw = K.world_of(K.mouth)
        if u < 0.55:
            c0 = C + Vector((0.12, -0.42, 1.42)) + Vector((0, 0, 0.05 * math.sin(u * 45)))
            K.hold(bottle, "R", c0 + Vector((0, 0, 0.09)), approach=(1, 0, 0), fdir=(0, -1, 0.2)); bottle.location = c0
            K.free_arm("L", c0 + Vector((-0.06, 0, 0.18)), fdir=(1, 0, -0.2), palm=(1, 0, 0), g=0.8)
            smile, mopen, squint = 1.0, 0.4, 0.5
        else:
            k = ease((u - 0.55) / 0.3)
            gp = vlerp(C + Vector((0.12, -0.42, 1.42)), mw + Vector((0.0, -0.06, -0.2)), k)
            K.hold(bottle, "R", gp + Vector((0, 0, 0.09)), approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(-1.3 * k, 0, 0)); bottle.location = gp
            K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
            smile, squint = 0.5, 0.9 * k
    elif t < TL["tease"]:
        # "four weeks" – points at the four week compartments, bottle in hand
        u = t - TL["weeks"]
        gp = C + Vector((0.25, -0.38, 1.25))
        K.hold(bottle, "R", gp + Vector((0, 0, 0.09)), approach=(1, 0, 0), fdir=(0, -1, 0.2)); bottle.location = gp
        K.free_arm("L", K.world_of(box, (-0.05, -0.12, BH + 0.12)), point=True)
        smile, brow, look = 1.0, 0.8, (0.0, -0.8 if u < 1.1 else 0.0)
    elif t < TL["price"]:
        # "and now..." – leans in, whispering
        u = t - TL["tease"]
        K.spine.rotation_euler = (0.22 * ease(u / 0.4), 0, 0)
        K.free_arm("L", K.world_of(K.mouth, (-0.11, -0.02, -0.05)), fdir=(0.2, -0.1, 1), palm=(1, 0, 0), g=0.1)
        K.free_arm("R", C + Vector((0.25, -0.3, 1.05)), g=0.4)
        smile, brow, squint, look = 0.8, 0.9, 0.4, (0.5, 0)
    elif t < TL["cta"]:
        # -50 %! hands on cheeks, then jumps with the box
        u = t - TL["price"]
        if u < 1.4:
            hc = K.world_of(K.head, (0, -0.05, 0.08))
            K.free_arm("L", hc + Vector((-0.1, -0.03, -0.04)), fdir=(0.2, 0, 1), palm=(1, 0, 0), g=0.2)
            K.free_arm("R", hc + Vector((0.1, -0.03, -0.04)), fdir=(-0.2, 0, 1), palm=(-1, 0, 0), g=0.2)
            smile, mopen, brow, look = 0.6, 0.9, 1.0, (0, 0)
            K.head.rotation_euler = (-0.1, 0, 0.1 * math.sin(u * 9))
        else:
            k = ease((u - 1.4) / 0.4)
            bc = vlerp(BOX_SPOT + Vector((0, 0, BH / 2)), C + Vector((0, -0.45, 1.5)), k)
            hinge.rotation_euler = (-1.95 * (1 - k), 0, 0)
            box.location = bc - Vector((0, 0, BH / 2)); box.rotation_euler = (0.2 * k, 0, 0)
            K.free_arm("L", K.world_of(box, (-BW / 2 - 0.02, 0, BH * 0.5)), fdir=(0.2, -0.3, 1), palm=(1, 0, 0), g=0.5)
            K.free_arm("R", K.world_of(box, (BW / 2 + 0.02, 0, BH * 0.5)), fdir=(-0.2, -0.3, 1), palm=(-1, 0, 0), g=0.5)
            K.hips.location.z += 0.03 * abs(math.sin(u * 7)) * k
            smile, mopen, brow, squint = 1.0, max(mopen, 0.4), 1.0, 0.4
    else:
        u = t - TL["cta"]
        bc = C + Vector((0.22, -0.4, 1.45 + 0.03 * math.sin(t * 6)))
        hinge.rotation_euler = (0, 0, 0)
        box.location = bc - Vector((0, 0, BH / 2)); box.rotation_euler = (0.2, 0, -0.3)
        K.free_arm("R", K.world_of(box, (BW / 2 + 0.02, 0, BH * 0.5)), fdir=(-0.2, -0.3, 1), palm=(-1, 0, 0), g=0.5)
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["box"]:
        a = -0.45 + 0.6 * t / TL["box"]; c = BOX_SPOT + Vector((0, 0, BH * 0.8))
        cam_p = c + Vector((0.55 * math.sin(a), -0.55 * math.cos(a), 0.22))
        return cam_p, c, c + (cam_p - c).normalized() * 0.03, 5.6
    if t < TL["mix"]:
        return C + Vector((0.05, -1.35, 1.65)), C + Vector((0.0, -0.3, 1.32)), C + Vector((0, -0.6, 1.2)), 3.2
    if t < TL["drink"]:
        c = BOTTLE_SPOT + Vector((0, 0, 0.2))
        return c + Vector((0.05, -0.6, 0.12)), c, c, 3.2
    if t < TL["weeks"]:
        return C + Vector((0.05, -1.05, 1.6)), C + Vector((0.03, -0.1, 1.5)), C + Vector((0, -0.3, 1.55)), 2.6
    if t < TL["tease"]:
        return C + Vector((0.0, -1.4, 1.62)), C + Vector((0.0, -0.35, 1.3)), C + Vector((0, -0.6, 1.2)), 3.4
    if t < TL["price"]:
        u = (t - TL["tease"]) / (TL["price"] - TL["tease"])
        return C + Vector((0.0, -1.0 + 0.25 * u, 1.62)), C + Vector((0.0, 0, 1.58)), C + Vector((0, -0.12, 1.6)), 2.2
    if t < TL["cta"]:
        u = (t - TL["price"]) / (TL["cta"] - TL["price"])
        return C + Vector((0.0, -1.25 - 0.2 * u, 1.6)), C + Vector((0.0, 0, 1.5)), C + Vector((0, -0.3, 1.55)), 2.8
    u = (t - TL["cta"]) / 1.55
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(box=K.world_of(box, (0, 0, BH * 0.6)), bottle=K.world_of(bottle, (0, 0, 0.1)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.4)
K.run(args, HERE, frame_state, anchor_objs)
