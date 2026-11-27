"""Suprent Pro clipper – bathroom before a date: huge beard -> trim -> sharp contour, two colours, CTA.
python3 scene.py --test 0.8,2.6,5.0,7.6,9.2,11.6,13.8,15.2 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args()
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(date=1.9, bart=4.12, trim=7.0, reveal=10.55, colors=13.05, cta=14.55, end=16.25)
K.init(); sc = K.sc

# ------------------------------------------------------------------ bathroom (evening)
TILE = K.brick_mat("tile", (0.93, 0.94, 0.95), (0.88, 0.9, 0.92), (0.6, 0.62, 0.64), scale=14, msize=0.01)
FLOOR = K.checker_mat("floor", (0.55, 0.57, 0.6), (0.45, 0.47, 0.5), scale=10, rough=0.3)
COUNTER = K.mat("counter", (0.95, 0.95, 0.94), rough=0.15, coat=0.8)
OAK = K.wood_mat("oak", (0.5, 0.33, 0.18), (0.68, 0.5, 0.3), scale=2.0, dist=5)
MIRROR = K.mat("mirror", (0.92, 0.92, 0.94), rough=0.02, metal=1.0)
LEDS = K.mat("leds", (1, 0.92, 0.8), emit=(1.0, 0.88, 0.7), es=10.0)
TOWEL = K.mat("towel", (0.2, 0.32, 0.5), rough=0.95, sheen=0.6)
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), TILE)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), TILE)
# round mirror with LED ring behind the character (left) + shelf, towel, plant
K.cyl("mirror", 0.48, 0.02, (-0.75, 2.57, 1.75), m=MIRROR, rot=(math.pi / 2, 0, 0), verts=64)
K.torus("ledring", 0.49, 0.012, (-0.75, 2.555, 1.75), m=LEDS, rot=(math.pi / 2, 0, 0))
K.box("shelf", (0.7, 0.16, 0.03), (0.95, 2.5, 1.45), m=OAK, bevel=0.005)
rng = random.Random(7)
for i in range(5):
    m = K.mat(f"btl{i}", [(0.95, 0.95, 0.95), (0.15, 0.15, 0.17), (0.75, 0.55, 0.3), (0.3, 0.45, 0.6), (0.9, 0.9, 0.85)][i], rough=0.2, coat=1.0)
    h = rng.uniform(0.1, 0.2); K.cyl("btl", 0.03, h, (0.72 + i * 0.12, 2.5, 1.465 + h / 2), m=m)
K.box("towelbar", (0.6, 0.02, 0.02), (1.35, 2.55, 1.05), m=K.CHROME)
K.box("towel", (0.45, 0.05, 0.6), (1.35, 2.53, 0.78), m=TOWEL, bevel=0.02, sub=1)
K.cyl("plantpot", 0.12, 0.25, (1.9, 2.25, 0.125), m=K.WHITE)
for i in range(10):
    a = i * 2.3; K.sphere("leaf", 0.1, (1.9 + 0.08 * math.cos(a), 2.25 + 0.08 * math.sin(a), 0.38 + 0.05 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.5 * math.sin(a), 0.5 * math.cos(a), a), seg=12)
# vanity in front of the character
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=OAK, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=COUNTER, bevel=0.005)
TOP = 0.9225
K.cyl("cup", 0.035, 0.1, (-0.7, 0.85, TOP + 0.05), m=K.WHITE)
for i in range(2): K.cyl("brush", 0.006, 0.16, (-0.71 + 0.02 * i, 0.85, TOP + 0.13), m=K.mat(f"tb{i}", [(0.2, 0.6, 0.9), (0.9, 0.3, 0.3)][i]), rot=(0.15, 0.1 - 0.2 * i, 0))
K.cyl("cologne", 0.035, 0.11, (0.75, 0.88, TOP + 0.055), m=K.thin_glass("cg", (0.6, 0.8, 1.0)))
K.box("phone", (0.075, 0.15, 0.008), (-0.4, 0.7, TOP + 0.004), m=K.BLACK, bevel=0.004, rot=(0, 0, 0.3))

# ------------------------------------------------------------------ products
CLIP_H = 0.15
def clipper(name, path, r_to, side_col):
    root = K.empty(name, (0, 0, 0))
    body = K.extrude(name + "_m", path, CLIP_H * 841 / r_to * r_to / 841, 0.044, r_to=r_to); body.parent = root
    return root
pro = clipper("pro", os.path.join(A, "product.png"), 634, (0.9, 0.4, 0.1))
silver = clipper("silver", os.path.join(A, "silver.png"), 634, (0.5, 0.5, 0.55))
FH = CLIP_H * 634 / 841
def stand(name, loc):
    st = K.empty(name, loc)
    K.box(name + "b", (0.095, 0.085, 0.032), (0, 0, 0.016), parent=st, m=K.BLACK, bevel=0.012)
    return st
hero_st = stand("hero_st", (0.0, 0.6, TOP)); silver_st = stand("silver_st", (0.45, 0.68, TOP))
_gl = bpy.data.lights.new("glowl", "POINT"); _gl.color = (1.0, 0.6, 0.25); _gl.shadow_soft_size = 0.01
glow = bpy.data.objects.new("glowl", _gl); sc.collection.objects.link(glow); glow.parent = pro; glow.location = (0, -0.06, CLIP_H * 0.75)
def set_glow(e): _gl.energy = 0.3 * e

CLIPS = [K.sphere(f"cl{i}", 0.005, (0, 0, -5), (1, 1, 2.5), m=K.HAIR, seg=8) for i in range(40)]
crng = random.Random(9)
CLIP_T = sorted(crng.uniform(0, 1) for _ in CLIPS)
CLIP_V = [(crng.uniform(-0.6, 0.6), crng.uniform(-0.9, -0.2), crng.uniform(0.0, 0.4)) for _ in CLIPS]

# ------------------------------------------------------------------ character (date outfit, huge beard)
K.build_character(hair="short", beard="full", tee=(0.95, 0.95, 0.95), shirt=(0.12, 0.16, 0.3), shirt2=(0.16, 0.16, 0.18), hair_col=(0.12, 0.07, 0.04))
BEARD = {o.name: (tuple(o.scale), tuple(o.location)) for o in K.beard_objs}
watch = K.empty("watch", (0, 0, -0.012), K.ARM["L"][2])
K.cyl("watchband", 0.04, 0.02, (0, 0, 0), parent=watch, m=K.BLACK, verts=24)
K.cyl("watchface", 0.016, 0.006, (0.0, -0.04, 0), parent=watch, m=K.CHROME, rot=(math.pi / 2, 0, 0))

K.world((0.95, 0.92, 0.88), 0.3)
K.area("key", (-1.4, -1.4, 2.6), (0.8, -0.5, 0), 270, 2.5, (1, 0.95, 0.88))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 120, 3.0, (0.94, 0.96, 1))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 140, 1.0, (1.0, 0.85, 0.65))
K.point("ledl", (-0.75, 2.4, 1.75), 40, (1, 0.88, 0.7), 0.4)
K.camera(32)

def head_c(): return K.world_of(K.head, (0, 0, 0.16))
def jaw_c(): return K.world_of(K.head, (0, -0.03, 0.04))

def beard_state(p):
    """p 0 -> 1: wild full beard -> sharp short beard"""
    for o in K.beard_objs:
        s0, l0 = BEARD[o.name]
        if o.name.startswith("stub"): continue
        if o.name.startswith("mous"):
            k = lerp(1.15, 0.75, ease(p)); o.scale = (s0[0] * k, s0[1] * k, s0[2] * k); continue
        wild = 1.08 if o.name == "beard" else 1.12
        k = lerp(wild, 0.0, ease((p - (0.0 if o.name == "beard2" else 0.3)) / 0.6))
        o.scale = (s0[0] * max(k, 0.001) * (1 if o.name == "beard2" else 1), s0[1] * max(k, 0.001), s0[2] * max(k, 0.001)); o.hide_render = k < 0.02
        if o.name == "beard2": o.location = (l0[0], l0[1], l0[2] - 0.04 * (1 - ease(p)))

def place_clip(root, contact, d, H):
    d = Vector(d).normalized()
    root.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    root.location = Vector(contact) - d * H
    return Vector(contact) - d * (0.72 * H)

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["date"]
    beard_state(clamp((t - TL["trim"]) / (TL["reveal"] - TL["trim"] - 0.2)))
    set_glow(0)
    pro.location = hero_st.location + Vector((0, 0, 0.032)); pro.rotation_euler = (0, 0, 0)
    silver.location = silver_st.location + Vector((0, 0, 0.032)); silver.rotation_euler = (0, 0, -0.35)
    for i, o in enumerate(CLIPS):
        ts = TL["trim"] + 0.3 + CLIP_T[i] * (TL["reveal"] - TL["trim"] - 0.6)
        if t < ts: o.location = (0, 0, -5); continue
        u = t - ts; v = CLIP_V[i]
        p0 = jaw_c() + Vector((v[0] * 0.08, -0.06, -0.02))
        z = p0.z + v[2] * u - 4.9 * u * u; x = p0.x + v[0] * 0.25 * u; y = p0.y + v[1] * 0.2 * u
        if z < TOP + 0.004: z = TOP + 0.004 if y < 1.08 else max(z, 0.0)
        o.location = (x, y, z); o.rotation_euler = (u * 7, u * 5 + i, 0)
    smile, mopen, brow, squint, look = 0.6, K.talk(t, W_, 0.5), 0.0, 0.0, (0, 0)
    vib = Vector((0.003 * math.sin(t * 190), 0.002 * math.cos(t * 170), 0))
    if t < TL["date"]:
        k = ease((t - 0.5) / 0.4) * (1 - ease((t - 1.5) / 0.3))
        pro.location = hero_st.location + Vector((0, 0, 0.032 + 0.04 * k)); pro.rotation_euler = (0, 0, 2 * math.pi * ease((t - 0.55) / 0.95))
        set_glow(4 + 6 * k)
    elif t < TL["bart"]:
        # Friday evening – check the watch, panic
        u = t - TL["date"]; k = ease(u / 0.35)
        wp = C + vlerp((-0.25, -0.3, 1.05), (-0.05, -0.42, 1.42), k)
        K.free_arm("L", wp, fdir=(1, -0.2, 0.1), palm=(0, 0, -1), g=0.5)
        K.free_arm("R", C + Vector((0.25, -0.3, 1.05)), g=0.4)
        smile, brow, look = 0.2 if u > 0.9 else 0.6, 1.0 if u > 0.9 else 0.3, (-0.4, -0.9)
        K.head.rotation_euler = (0.25, 0, -0.1)
        if u > 1.2: smile, mopen, look = 0.0, max(mopen, 0.5), (0, 0); K.head.rotation_euler = (0.0, 0, 0)
    elif t < TL["trim"]:
        # "and my beard? catastrophe" – both hands stroke the wild beard
        u = t - TL["bart"]
        jc = jaw_c()
        K.free_arm("L", jc + Vector((-0.2, -0.16, -0.06 + 0.015 * math.sin(u * 6))), point=True)
        if u < 1.4: K.free_arm("R", C + Vector((0.27, -0.3, 1.06)), g=0.4)
        else:
            # grab the clipper
            k = ease((u - 1.4) / 0.6)
            p = vlerp(hero_st.location + Vector((0, 0, 0.032 + FH * 0.4)), C + Vector((0.22, -0.42, 1.38)), k)
            K.hold(pro, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); pro.location = p - Vector((0, 0, FH * 0.4))
            set_glow(6 * k)
        smile, brow, squint, look = 0.0, -0.8, 0.3, (0.2, -0.7)
        if u > 1.6: smile, brow, look = 0.5, 0.6, (0.5, 0)
        K.head.rotation_euler = (0.12, 0, 0.08 * math.sin(u * 3))
    elif t < TL["reveal"]:
        # the trim: along the jaw line, both sides, mustache
        u = (t - TL["trim"]) / (TL["reveal"] - TL["trim"])
        jc = jaw_c()
        seg = min(int(u * 4), 3); f = ease(u * 4 - seg)
        paths = [((0.1, -0.02, 0.06), (0.06, -0.08, -0.03)), ((-0.1, -0.02, 0.06), (-0.06, -0.08, -0.03)),
                 ((0.04, -0.1, -0.04), (-0.04, -0.1, -0.04)), ((-0.03, -0.12, 0.035), (0.03, -0.12, 0.035))]
        a0, a1 = paths[seg]; contact = jc + vlerp(a0, a1, f)
        d = Vector((0, 0.5, 1.0 if seg < 3 else 0.2)).normalized()
        if seg in (0, 1): d = Vector((-0.4 * (1 if seg == 0 else -1), 0.4, 0.8)).normalized()
        if seg == 3: d = Vector((0, 1, 0))
        grip_p = place_clip(pro, contact + vib, d, FH)
        fd = d.cross(Vector((1, 0, 0))); fd = fd.normalized() if fd.length > 1e-3 else Vector((0, -1, 0))
        if fd.y > 0: fd = -fd
        K.hold(None, "R", grip_p, approach=(1, 0.0, 0.0), fdir=tuple(fd), g=1.0)
        set_glow(1.5)
        K.free_arm("L", C + Vector((-0.28, -0.32, 1.08)), g=0.4)
        K.head.rotation_euler = (-0.25, 0, (-0.3 if seg == 0 else 0.3 if seg == 1 else 0))
        smile, squint, mopen, brow, look = 0.4, 0.5, 0.0, 0.5, (0, -0.4)
    elif t < TL["colors"]:
        # "only needed five" – smug, collar pop, thumbs up
        u = t - TL["reveal"]
        p = C + Vector((0.3, -0.36, 1.12))
        K.hold(pro, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); pro.location = p - Vector((0, 0, FH * 0.4))
        K.thumbs_up("L", C + Vector((-0.17, -0.45, 1.5 + 0.02 * math.sin(u * 8))))
        K.head.rotation_euler = (-0.1, 0, 0.4 * math.sin(u * 2.6))
        smile, mopen, brow, squint, look = 1.0, max(mopen, 0.2), 0.9, 0.3, (0.4 * math.sin(u * 2.6), 0)
    elif t < TL["cta"]:
        u = t - TL["colors"]; k = ease(u / 0.4)
        pr = C + Vector((0.2, -0.45, 1.5)); pl = C + vlerp((-0.2, -0.38, 1.12), (-0.2, -0.45, 1.5), k)
        K.hold(pro, "R", pr, approach=(1, 0, 0), fdir=(0, -1, 0.15)); pro.location = pr - Vector((0, 0, FH * 0.4))
        K.hold(silver, "L", pl, approach=(-1, 0, 0), fdir=(0, -1, 0.15)); silver.location = pl - Vector((0, 0, FH * 0.4))
        set_glow(5); smile, brow, look = 1.0, 0.7, (0, -0.2)
    else:
        p = C + Vector((0.27, -0.36, 1.56 + 0.03 * math.sin(t * 6)))
        K.hold(pro, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); pro.location = p - Vector((0, 0, FH * 0.4))
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        set_glow(5); smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["date"]:
        a = -0.45 + 0.6 * t / TL["date"]; c = hero_st.location + Vector((0, 0, 0.032 + FH * 0.55))
        cam_p = c + Vector((0.32 * math.sin(a), -0.32 * math.cos(a), 0.02))
        return cam_p, c + Vector((0, 0, -0.005)), c + (cam_p - c).normalized() * 0.03, 5.6
    if t < TL["bart"]:
        u = (t - TL["date"]) / (TL["bart"] - TL["date"])
        return C + Vector((0.2, -1.6 + 0.15 * u, 1.55)), C + Vector((-0.05, 0, 1.42)), C + Vector((0, -0.25, 1.5)), 2.8
    if t < TL["trim"]:
        return C + Vector((0.05, -1.0, 1.6)), C + Vector((0.02, 0, 1.52)), C + Vector((0, -0.15, 1.58)), 2.6
    if t < TL["reveal"]:
        u = (t - TL["trim"]) / (TL["reveal"] - TL["trim"])
        return C + Vector((0.3 - 0.25 * u, -0.85, 1.6)), C + Vector((0.0, 0, 1.56)), C + Vector((0, -0.12, 1.58)), 2.4
    if t < TL["colors"]:
        return C + Vector((-0.05, -1.2, 1.62)), C + Vector((-0.05, 0, 1.5)), C + Vector((0, -0.1, 1.6)), 2.6
    if t < TL["cta"]:
        return C + Vector((0.0, -1.3, 1.58)), C + Vector((0.0, 0, 1.48)), C + Vector((0, -0.45, 1.52)), 3.0
    u = (t - TL["cta"]) / 1.6
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(clipper=K.world_of(pro, (0, 0, FH * 0.55)), silver=K.world_of(silver, (0, 0, FH * 0.55)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.4)
K.run(args, HERE, frame_state, anchor_objs)
