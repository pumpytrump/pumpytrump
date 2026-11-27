"""Suprent FANGS clipper – barbershop: messy hair -> self cut -> clean fade, AI power, two colours, CTA.
python3 scene.py --test 0.8,2.2,4.2,5.6,7.0,8.2,9.8,11.5,13.6,15.2 --samples 8 --res 640 --out out/test
python3 scene.py --frames 0-393 --res 1280 --samples 12
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp, win
import bpy

args = K.parse_args()
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(barber=3.3, self=5.0, thick=6.65, cut=7.6, zack=9.12, ki=10.75, colors=13.0, cta=14.62, end=16.3)
K.init(); sc = K.sc

# ------------------------------------------------------------------ barbershop
WALL = K.mat("wallg", (0.07, 0.17, 0.15), rough=0.85)
PANEL = K.wood_mat("panel", (0.18, 0.1, 0.05), (0.32, 0.19, 0.1), scale=1.5, dist=8)
FLOOR = K.checker_mat("floor", (0.92, 0.92, 0.9), (0.06, 0.06, 0.07), scale=14)
MARBLE = K.mat("marble", (0.08, 0.08, 0.09), rough=0.12, coat=1.0)
NEON = K.mat("neon", (0.3, 1.0, 0.3), emit=(0.25, 1.0, 0.3), es=12.0)
BULB = K.mat("bulb", (1, 0.9, 0.7), emit=(1.0, 0.85, 0.6), es=8.0)
POLE_W = K.mat("polew", (0.95, 0.95, 0.95), rough=0.2, coat=1.0)
nt = POLE_W.node_tree; b = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "DIAGONAL"
wv.inputs["Scale"].default_value = 3.0; nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = "CONSTANT"
cr.color_ramp.elements[0].color = (0.85, 0.06, 0.06, 1); cr.color_ramp.elements[1].position = 0.33; cr.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1)
e3 = cr.color_ramp.elements.new(0.66); e3.color = (0.05, 0.15, 0.7, 1)
nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
POLE_MAP = wv
MIRROR = K.mat("mirror", (0.9, 0.9, 0.92), rough=0.02, metal=1.0)
LEATHER = K.mat("leather", (0.35, 0.12, 0.06), rough=0.45, coat=0.4)

K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
K.box("wainscot", (6, 0.04, 1.0), (0, 2.58, 0.5), m=PANEL, bevel=0.01)
K.box("rail", (6, 0.07, 0.05), (0, 2.56, 1.02), m=PANEL, bevel=0.01)
# mirror with bulbs (behind character, slightly left)
K.box("mframe", (1.1, 0.04, 0.9), (-0.55, 2.56, 1.75), m=K.BLACK, bevel=0.01)
K.box("mirror", (1.0, 0.01, 0.8), (-0.55, 2.535, 1.75), m=MIRROR)
for i in range(6):
    K.sphere("bulb", 0.028, (-1.08 + i * 0.212, 2.52, 2.22), m=BULB, seg=16)
# neon sign "BARBER" in green (matches the product)
bpy.ops.object.text_add(location=(0.75, 2.55, 2.05), rotation=(math.pi / 2, 0, 0))
tx = bpy.context.object; tx.data.body = "BARBER"; tx.data.size = 0.22; tx.data.extrude = 0.006; tx.data.align_x = "CENTER"
tx.data.bevel_depth = 0.004; tx.data.materials.append(NEON)
# barber pole
K.cyl("polecap", 0.07, 0.05, (1.55, 2.48, 2.0), m=K.CHROME); K.cyl("polecap2", 0.07, 0.05, (1.55, 2.48, 1.3), m=K.CHROME)
pole = K.cyl("pole", 0.055, 0.66, (1.55, 2.48, 1.65), m=POLE_W, verts=32)
# shelf with bottles
K.box("shelf", (0.9, 0.18, 0.03), (1.3, 2.5, 1.25), m=PANEL, bevel=0.005)
rng = random.Random(4)
for i in range(7):
    m = K.mat(f"btl{i}", [(0.1, 0.3, 0.6), (0.7, 0.5, 0.2), (0.9, 0.9, 0.9), (0.2, 0.2, 0.2), (0.6, 0.1, 0.1)][i % 5], rough=0.2, coat=1.0)
    h = rng.uniform(0.12, 0.22); K.cyl("btl", 0.03, h, (0.92 + i * 0.12, 2.5, 1.265 + h / 2), m=m)
# barber chair (left, background)
K.box("seat", (0.55, 0.5, 0.12), (-1.6, 2.0, 0.55), m=LEATHER, bevel=0.04, sub=1)
K.box("back", (0.55, 0.1, 0.65), (-1.6, 2.25, 0.95), m=LEATHER, bevel=0.04, sub=1)
K.cyl("cbase", 0.05, 0.5, (-1.6, 2.0, 0.25), m=K.CHROME); K.cyl("cfoot", 0.25, 0.03, (-1.6, 2.0, 0.015), m=K.CHROME)
# counter in front of the character
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=PANEL, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=MARBLE, bevel=0.005)
TOP = 0.9225
K.box("comb", (0.16, 0.025, 0.006), (-0.55, 0.68, TOP + 0.003), m=K.BLACK, rot=(0, 0, 0.3))
K.cyl("spray", 0.03, 0.15, (-0.85, 0.85, TOP + 0.075), m=K.mat("spr", (0.1, 0.4, 0.8), rough=0.2, coat=1.0))
K.cyl("towel", 0.06, 0.18, (0.85, 0.85, TOP + 0.06), m=K.WHITE, rot=(0, math.pi / 2, 0.2), sub=1)

# ------------------------------------------------------------------ products
CLIP_H = 0.17
def clipper(name, path, r_to=None):
    root = K.empty(name, (0, 0, 0))
    body = K.extrude(name + "_m", path, CLIP_H, 0.046, r_to=r_to); body.parent = root
    from PIL import Image
    im = Image.open(path); Wp, Hp = im.size; hh = CLIP_H * (r_to or Hp) / Hp
    return root, hh
def stand(name, loc):
    st = K.empty(name, loc)
    K.box(name + "b", (0.1, 0.085, 0.034), (0, 0, 0.017), parent=st, m=K.BLACK, bevel=0.012)
    K.box(name + "l", (0.08, 0.004, 0.004), (0, -0.044, 0.006), parent=st, m=NEON)
    return st
fangs, FH = clipper("fangs", os.path.join(A, "product.png"))
pink, PH = clipper("pink", os.path.join(A, "pink.png"), r_to=795)
hero_st = stand("hero_st", (0.0, 0.6, TOP))
pink_st = stand("pink_st", (0.42, 0.66, TOP))
DISPLAY = K.mat("display", (0.2, 1.0, 0.3), emit=(0.2, 1.0, 0.3), es=0.0)
_gl = bpy.data.lights.new("glowl", "POINT"); _gl.color = (0.3, 1.0, 0.35); _gl.shadow_soft_size = 0.01
glow = bpy.data.objects.new("glowl", _gl); sc.collection.objects.link(glow); glow.parent = fangs; glow.location = (0, -0.06, CLIP_H * 0.62)
class _G:
    hide_render = True
def _set_glow(e): _gl.energy = 0.35 * e

# hair clippings
CLIPS = [K.sphere(f"cl{i}", 0.006, (0, 0, -5), (1, 1, 2.5), m=K.HAIR, seg=8) for i in range(36)]
crng = random.Random(9)
CLIP_T = sorted(crng.uniform(0, 1) for _ in CLIPS)
CLIP_V = [(crng.uniform(-0.6, 0.6), crng.uniform(-0.9, -0.2), crng.uniform(0.0, 0.6)) for _ in CLIPS]

# ------------------------------------------------------------------ character
K.build_character(hair="messy", beard="stubble", tee=(0.12, 0.12, 0.13), shirt=(0.55, 0.14, 0.1), shirt2=(0.18, 0.2, 0.28))
hairtop = K.hair_objs[0]; tufts = [o for o in K.hair_objs if o.name.startswith("tuft")]
BASE = {o.name: tuple(o.scale) for o in K.hair_objs}
order = sorted(tufts, key=lambda o: (o.location.y, -o.location.z))
TUFT_TH = {o.name: i / len(order) * 0.85 for i, o in enumerate(order)}

K.world((0.9, 0.85, 0.8), 0.25)
K.area("key", (-1.4, -1.4, 2.6), (0.8, -0.5, 0), 280, 2.5, (1, 0.95, 0.88))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 110, 3.0, (0.92, 0.96, 1))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 160, 1.0, (0.5, 1.0, 0.55))
K.point("neonl", (0.75, 2.35, 2.05), 60, (0.3, 1.0, 0.35), 0.3)
K.camera(32)

# ------------------------------------------------------------------ choreography
def head_c(): return K.world_of(K.head, (0, 0, 0.16))

def place_clip(root, contact, d, H):
    d = Vector(d).normalized()
    root.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    root.location = Vector(contact) - d * H
    return Vector(contact) - d * (0.72 * H)

def hair_state(p):
    """p: 0 messy -> 1 clean fade"""
    for o in tufts:
        k = 1 - ease((p - TUFT_TH[o.name]) / 0.12)
        s = BASE[o.name]; o.scale = (s[0] * max(k, 0.001), s[1] * max(k, 0.001), s[2] * max(k, 0.001)); o.hide_render = k < 0.02
    s = BASE[hairtop.name]
    hairtop.scale = tuple(vlerp((s[0] * 1.1, s[1] * 1.12, s[2] * 1.15), (s[0] * 0.97, s[1] * 1.0, s[2] * 0.72), ease(p)))
    hairtop.location.z = lerp(0.2, 0.19, ease(p))

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    POLE_MAP.inputs["Phase Offset"].default_value = t * 4.0
    pcut = clamp((t - TL["cut"]) / (TL["zack"] - TL["cut"] - 0.15))
    hair_state(pcut)
        # resting places
    fangs.location = hero_st.location + Vector((0, 0, 0.034)); fangs.rotation_euler = (0, 0, 0)
    pink.location = pink_st.location + Vector((0, 0, 0.034)); pink.rotation_euler = (0, 0, -0.35)
    for i, o in enumerate(CLIPS):
        ts = TL["cut"] + CLIP_T[i] * (TL["zack"] - TL["cut"] - 0.2)
        if t < ts: o.location = (0, 0, -5); continue
        u = t - ts; v = CLIP_V[i]
        p0 = head_c() + Vector((v[0] * 0.12, -0.05, 0.02))
        z = p0.z + v[2] * u - 4.9 * u * u
        x = p0.x + v[0] * 0.25 * u; y = p0.y + v[1] * 0.25 * u
        if z < TOP + 0.004: z = TOP + 0.004 if y < 1.08 else max(z, 0.0)
        o.location = (x, y, z); o.rotation_euler = (u * 7, u * 5 + i, 0)
    smile, mopen, brow, squint, look = 0.6, K.talk(t, W_, 0.5), 0.0, 0.0, (0, 0)
    vib = Vector((0.003 * math.sin(t * 190), 0.002 * math.cos(t * 170), 0))
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["barber"]
    if t < TL["barber"]:
        # hook: clipper spins up off its stand
        k = ease((t - 1.35) / 0.35) * (1 - ease((t - 2.6) / 0.4))
        fangs.location = hero_st.location + Vector((0, 0, 0.034 + 0.05 * k))
        fangs.rotation_euler = (0, 0, 2 * math.pi * ease((t - 1.5) / 1.1))
        _set_glow( 3.0 + 5.0 * k)
        K.free_arm("L", C + Vector((0.12, -0.2, 1.42)), g=0.6); K.free_arm("R", C + Vector((-0.12, -0.18, 1.38)), g=0.6)
    elif t < TL["self"]:
        # "my barber is on vacation" – shrug
        k = ease((t - TL["barber"]) / 0.35)
        K.free_arm("L", C + vlerp((-0.25, -0.2, 1.05), (-0.42, -0.25, 1.28), k), fdir=(-0.6, -0.4, 0.3), palm=(0, 0, -1), g=0.1)
        K.free_arm("R", C + vlerp((0.25, -0.2, 1.05), (0.42, -0.25, 1.28), k), fdir=(0.6, -0.4, 0.3), palm=(0, 0, -1), g=0.1)
        smile, brow, look = 0.35, 0.9, (-0.6, 0.3); K.head.rotation_euler = (0.05, 0.18 * k, 0.1)
        K.spine.rotation_euler = (0, 0, 0)
    elif t < TL["thick"]:
        # grab the clipper from the stand, hold it up
        u = t - TL["self"]
        k = ease(u / 0.45); lift = ease((u - 0.45) / 0.4)
        p = vlerp(hero_st.location + Vector((0, 0, 0.034 + FH * 0.4)), C + Vector((0.2, -0.42, 1.45)), lift)
        K.hold(fangs, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0, 0, 0))
        fangs.location = p - Vector((0, 0, FH * 0.4)) + vib * lift
        _set_glow( 6.0 * lift)
        K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.5)
        smile, brow, squint, look = 0.8, -0.5 + 1.2 * lift, 0.3, (0.6, 0.2)
    elif t < TL["cut"]:
        # "thick hair?" – left hand grabs the hair, clipper ready
        p = C + Vector((0.22, -0.42, 1.42))
        K.hold(fangs, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); fangs.location = p - Vector((0, 0, FH * 0.4)) + vib
        _set_glow( 6.0)
        hc = head_c()
        K.free_arm("L", hc + Vector((-0.05, -0.02, 0.09)), fdir=(0.3, 0.2, 1), palm=(0, 0, -1), g=0.8)
        smile, brow, look = 0.3, 1.0, (-0.3, 1.0); K.head.rotation_euler = (-0.1, 0, 0.05)
    elif t < TL["zack"]:
        # the cut: passes over top and sides
        u = (t - TL["cut"]) / (TL["zack"] - TL["cut"])
        hc = head_c()
        seg = min(int(u * 4), 3); f = (u * 4) - seg
        paths = [((0.03, -0.12, 0.05), (0.03, 0.05, 0.13)), ((0.12, -0.06, 0.02), (0.12, 0.08, 0.09)),
                 ((-0.06, -0.1, 0.09), (-0.04, 0.06, 0.14)), ((0.1, -0.04, -0.02), (0.11, 0.1, 0.06))]
        a0, a1 = paths[seg]; ff = ease(f)
        contact = hc + vlerp(a0, a1, ff)
        d = (hc - contact).normalized()
        grip_p = place_clip(fangs, contact + vib, d, FH)
        fd = d.cross(Vector((0, 0, 1)))
        fd = fd.normalized() if fd.length > 1e-3 else Vector((0, -1, 0))
        if fd.y > 0: fd = -fd
        K.hold(None, "R", grip_p, approach=(1, 0.2, 0.1), fdir=tuple(fd), g=1.0)
        _set_glow( 8.0)
        K.free_arm("L", C + Vector((-0.3, -0.32, 1.1)), g=0.4)
        smile, squint, mopen, brow = 0.7, 0.7, max(mopen, 0.15), 0.2
        K.head.rotation_euler = (0.12 * math.sin(t * 6), 0, 0.15 * math.sin(t * 4))
    elif t < TL["ki"]:
        # "zack, clean fade" – turn head, rub hand over fresh cut
        u = t - TL["zack"]
        p = C + Vector((0.3, -0.36, 1.12))
        K.hold(fangs, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); fangs.location = p - Vector((0, 0, FH * 0.4))
        hc = head_c()
        K.thumbs_up("L", C + Vector((-0.17, -0.45, 1.52 + 0.02 * math.sin(u * 8))))
        K.head.rotation_euler = (-0.05, 0, 0.5 * math.sin(u * 3.2))
        smile, mopen, brow, squint, look = 1.0, max(mopen, 0.3), 0.9, 0.2, (0.4 * math.sin(u * 3.2), 0)
    elif t < TL["colors"]:
        # "AI adapts the power" – show the display, it glows and pulses
        u = t - TL["ki"]
        p = C + Vector((0.14, -0.42, 1.46))
        K.hold(fangs, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15), obj_rot=(0.15, 0, 0.12)); fangs.location = p - Vector((0, 0, FH * 0.4)) + vib
        _set_glow( 6.0 + 6.0 * (0.5 + 0.5 * math.sin(u * 9)))
        K.free_arm("L", C + Vector((-0.26, -0.3, 1.08)), g=0.4)
        smile, brow, look = 0.9, 0.8, (0.4, -0.2)
    elif t < TL["cta"]:
        # two colours: black-green right, pink left
        u = t - TL["colors"]; k = ease(u / 0.4)
        pr = C + Vector((0.2, -0.45, 1.5)); pl = C + vlerp((-0.2, -0.38, 1.12), (-0.2, -0.45, 1.5), k)
        K.hold(fangs, "R", pr, approach=(1, 0, 0), fdir=(0, -1, 0.15)); fangs.location = pr - Vector((0, 0, FH * 0.4))
        if u < 0.25:
            pl = pink_st.location + Vector((0, 0, 0.034 + PH * 0.4)); pl = vlerp(pl, C + Vector((-0.26, -0.4, 1.48)), ease(u / 0.25) * 0)
        K.hold(pink, "L", pl, approach=(-1, 0, 0), fdir=(0, -1, 0.15)); pink.location = pl - Vector((0, 0, PH * 0.4))
        _set_glow( 6.0)
        smile, brow, look = 1.0, 0.7, (0, -0.2)
    else:
        u = t - TL["cta"]
        p = C + Vector((0.27, -0.36, 1.56 + 0.03 * math.sin(t * 6)))
        K.hold(fangs, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.15)); fangs.location = p - Vector((0, 0, FH * 0.4))
        _set_glow( 6.0)
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["barber"]:
        a = -0.45 + 0.6 * t / TL["barber"]; c = hero_st.location + Vector((0, 0, 0.034 + FH * 0.55))
        cam_p = c + Vector((0.36 * math.sin(a), -0.36 * math.cos(a), 0.02))
        return cam_p, c + Vector((0, 0, -0.005)), c + (cam_p - c).normalized() * 0.03, 5.6
    if t < TL["self"]:
        u = (t - TL["barber"]) / (TL["self"] - TL["barber"])
        return C + Vector((0.25, -1.75 + 0.1 * u, 1.55)), C + Vector((-0.05, 0, 1.4)), C + Vector((0, -0.2, 1.5)), 2.8
    if t < TL["cut"]:
        return C + Vector((0.1, -1.25, 1.6)), C + Vector((0.05, 0, 1.5)), C + Vector((0, -0.3, 1.55)), 2.6
    if t < TL["zack"]:
        u = (t - TL["cut"]) / (TL["zack"] - TL["cut"])
        return C + Vector((0.35 - 0.2 * u, -0.85, 1.72)), C + Vector((0.0, 0, 1.62)), C + Vector((0, -0.1, 1.65)), 2.4
    if t < TL["ki"]:
        return C + Vector((-0.05, -1.2, 1.62)), C + Vector((-0.05, 0, 1.5)), C + Vector((0, -0.1, 1.6)), 2.6
    if t < TL["colors"]:
        return C + Vector((0.12, -1.0, 1.58)), C + Vector((0.1, -0.3, 1.52)), C + Vector((0.14, -0.42, 1.55)), 3.2
    if t < TL["cta"]:
        return C + Vector((0.0, -1.3, 1.58)), C + Vector((0.0, 0, 1.48)), C + Vector((0, -0.45, 1.52)), 3.0
    u = (t - TL["cta"]) / 1.6
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(clipper=K.world_of(fangs, (0, 0, FH * 0.55)), pink=K.world_of(pink, (0, 0, PH * 0.55)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.3)
K.run(args, HERE, frame_state, anchor_objs)
