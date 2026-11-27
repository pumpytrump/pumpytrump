"""More Protein Iced Coffee – café kitchen: powder, milk, ice, shake, pour, sip; espresso machine 'gets fired'.
python3 scene.py --test 0.8,3.0,5.2,6.0,6.8,7.6,8.3,9.0,10.5,13.2,15.2 --samples 8 --res 640 --out out/test
"""
import math, os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import core as K
from core import Vector, ease, back, lerp, vlerp, clamp
import bpy

args = K.parse_args()
W_ = json.load(open(os.path.join(A, "words.json"))); T = [w[1] for w in W_]
TL = dict(intro=1.75, yes=4.6, powder=5.65, milk=6.45, ice=7.2, shake=7.95, pour=8.6, sip=9.3, barista=12.15, cta=14.65, end=16.25)
K.init(); sc = K.sc

# ------------------------------------------------------------------ café kitchen
WALL = K.mat("wall", (0.82, 0.5, 0.36), rough=0.9)                      # terracotta
TILE = K.brick_mat("tile", (0.96, 0.95, 0.92), (0.92, 0.9, 0.86), (0.7, 0.68, 0.64), scale=16)
OAK = K.wood_mat("oak", (0.55, 0.38, 0.22), (0.72, 0.54, 0.34), scale=2.0, dist=5)
FLOOR = K.checker_mat("floor", (0.9, 0.88, 0.84), (0.3, 0.28, 0.27), scale=12, rough=0.3)
COUNTER = K.mat("counter", (0.93, 0.93, 0.92), rough=0.2, coat=0.6)
K.plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
K.plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
K.plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
K.box("backsplash", (3.2, 0.02, 0.7), (0, 2.585, 1.25), m=TILE)
K.box("bcounter", (3.2, 0.5, 0.9), (0, 2.35, 0.45), m=OAK, bevel=0.01)
K.box("bctop", (3.25, 0.55, 0.04), (0, 2.35, 0.92), m=COUNTER, bevel=0.005)
for z in (1.75, 2.15):
    K.box("shelf", (1.2, 0.2, 0.03), (0.9, 2.5, z), m=OAK, bevel=0.005)
    for i in range(4):
        K.cyl("jar", 0.045, 0.13, (0.5 + i * 0.26, 2.5, z + 0.08), m=K.thin_glass(f"jar{i}{z}", (0.95, 0.9, 0.8)))
        K.cyl("beans", 0.04, 0.07, (0.5 + i * 0.26, 2.5, z + 0.05), m=K.mat(f"bean{i}", (0.25, 0.13, 0.06), rough=0.6))
# espresso machine (the barista) on the back counter
ESP = K.empty("esp", (-0.75, 2.35, 0.94))
K.box("espbody", (0.5, 0.36, 0.38), (0, 0, 0.19), parent=ESP, m=K.CHROME, bevel=0.02)
K.box("esptop", (0.5, 0.36, 0.04), (0, 0, 0.4), parent=ESP, m=K.BLACK, bevel=0.01)
ESPL = K.mat("espl", (1, 0.3, 0.2), emit=(1.0, 0.3, 0.15), es=8.0)
esp_lights = [K.sphere("espl", 0.012, (-0.12 + 0.08 * i, -0.185, 0.3), parent=ESP, m=ESPL, seg=12) for i in range(4)]
K.cyl("group", 0.04, 0.05, (0, -0.2, 0.14), parent=ESP, m=K.BLACK)
for i in range(3): K.cyl("cupb", 0.03, 0.05, (-0.15 + 0.15 * i, -0.02, 0.43), parent=ESP, m=K.WHITE)
K.cyl("plantpot", 0.12, 0.25, (1.9, 2.25, 0.125), m=K.POT)
for i in range(10):
    a = i * 2.3; K.sphere("leaf", 0.1, (1.9 + 0.08 * math.cos(a), 2.25 + 0.08 * math.sin(a), 0.38 + 0.05 * i), (1, 0.4, 1.5), m=K.GREEN, rot=(0.5 * math.sin(a), 0.5 * math.cos(a), a), seg=12)
# island in front
K.box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=OAK, bevel=0.01)
K.box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=COUNTER, bevel=0.005)
TOP = 0.9225
K.box("board", (0.35, 0.22, 0.02), (-0.75, 0.75, TOP + 0.01), m=OAK, bevel=0.004, rot=(0, 0, 0.2))

# ------------------------------------------------------------------ props
TUB_H = 0.16
tub = K.empty("tub", (0, 0, 0))
tb = K.revolve("tub_m", os.path.join(A, "product.png"), TUB_H, r_from=96, step=4); tb.parent = tub
from PIL import Image as _I
_im = _I.open(os.path.join(A, "product.png")); _w, _h = _im.size
_xs = [x for x in range(_w) if _im.getpixel((x, 50))[3] > 140]; _lr = (_xs[-1] - _xs[0]) / 2 * TUB_H / _h
_lh = 100 * TUB_H / _h
K.cyl("tub_lid", _lr, _lh, (0, 0, TUB_H - _lh / 2), parent=tub, m=K.mat("tublid", (0.96, 0.96, 0.95), rough=0.35, coat=0.3), verts=64, bevel=0.004)
hero = K.empty("hero", (0.0, 0.6, TOP))
K.cyl("coaster", 0.1, 0.012, (0, 0, 0.006), parent=hero, m=OAK, bevel=0.003, verts=48)
TUB_SPOT = Vector((-0.42, 0.66, TOP))
# shaker
SHAK = K.thin_glass("shaker", (0.95, 0.97, 1.0))
shaker = K.empty("shaker", (0, 0, 0))
K.cyl("shk", 0.04, 0.17, (0, 0, 0.085), parent=shaker, m=SHAK, cap=False, verts=48)
K.cyl("shkb", 0.04, 0.004, (0, 0, 0.002), parent=shaker, m=SHAK, verts=48)
shlid = K.empty("shlid", (0, 0, 0.17), shaker)
K.cyl("shlidm", 0.043, 0.04, (0, 0, 0.02), parent=shlid, m=K.BLACK, verts=48, bevel=0.004)
MILKC = K.mat("milkcof", (0.93, 0.9, 0.85), rough=0.15, sss=0.4)
shliq = K.cyl("shliq", 0.037, 1.0, (0, 0, 0.5), parent=shaker, m=MILKC, verts=48)
POWDER = K.mat("powder", (0.55, 0.38, 0.25), rough=0.9)
powder_layer = K.cyl("powl", 0.037, 0.02, (0, 0, 0.012), parent=shaker, m=POWDER, verts=48)
shake_ice = [K.box(f"si{i}", (0.022, 0.022, 0.022), (0, 0, -5), m=K.ICE, bevel=0.003) for i in range(4)]
SHAKER_SPOT = Vector((0.0, 0.62, TOP))
# scoop + powder particles
scoop = K.empty("scoop", (0, 0, -5))
K.cyl("scb", 0.022, 0.03, (0, 0, 0.0), parent=scoop, m=K.WHITE, verts=24)
K.box("sch", (0.012, 0.09, 0.006), (0, 0.06, 0.012), parent=scoop, m=K.WHITE, bevel=0.002)
pdots = [K.sphere(f"pd{i}", 0.004, (0, 0, -5), m=POWDER, seg=8) for i in range(24)]
# milk carton + stream
MILKM = K.mat("milkbox", (0.95, 0.95, 0.97), rough=0.5)
milk = K.empty("milk", (0, 0, 0))
K.box("mb", (0.07, 0.07, 0.19), (0, 0, 0.095), parent=milk, m=MILKM, bevel=0.004)
K.box("mlabel", (0.072, 0.072, 0.06), (0, 0, 0.09), parent=milk, m=K.mat("mlab", (0.2, 0.45, 0.85), rough=0.5))
K.box("mtop", (0.07, 0.03, 0.04), (0, 0, 0.205), parent=milk, m=MILKM, rot=(0.6, 0, 0))
MILK_SPOT = Vector((0.45, 0.72, TOP))
MILKW = K.mat("milkw", (0.97, 0.97, 0.96), rough=0.1, sss=0.5)
stream = K.cyl("stream", 0.006, 1.0, (0, 0, -5), m=MILKW, verts=12)
ice_drop = [K.box(f"id{i}", (0.022, 0.022, 0.022), (0, 0, -5), m=K.ICE, bevel=0.003) for i in range(4)]
# serving glass with iced coffee
glass = K.empty("glass", (0, 0, 0))
bm_g = K.cyl("glassm", 0.042, 0.14, (0, 0, 0.07), parent=glass, m=K.GLASS, cap=False, verts=48)
K.cyl("glassb", 0.042, 0.006, (0, 0, 0.003), parent=glass, m=K.GLASS, verts=48)
COF = K.mat("icedcof", (0.42, 0.24, 0.13), rough=0.1, sss=0.3)
gliq = K.cyl("gliq", 0.038, 1.0, (0, 0, 0.5), parent=glass, m=COF, verts=48)
FOAM = K.mat("foam", (0.93, 0.85, 0.72), rough=0.6, sss=0.3)
gfoam = K.cyl("gfoam", 0.038, 0.015, (0, 0, -5), parent=glass, m=FOAM, verts=48)
gice = [K.box(f"gi{i}", (0.024, 0.024, 0.024), (0, 0, -5), parent=glass, m=K.ICE, bevel=0.003, rot=(0.3 * i, 0.5 * i, 0.2)) for i in range(3)]
straw = K.cyl("straw", 0.004, 0.2, (0.015, 0, -5), parent=glass, m=K.BLACK, rot=(0, 0.15, 0))
GLASS_SPOT = Vector((0.32, 0.6, TOP))
# pour stream (coffee)
cstream = K.cyl("cstream", 0.008, 1.0, (0, 0, -5), m=COF, verts=12)

# ------------------------------------------------------------------ character (barista apron)
K.build_character(hair="short", beard="stubble", tee=(0.95, 0.95, 0.93), shirt=(0.35, 0.5, 0.65), shirt2=(0.25, 0.25, 0.28),
                  apron=(0.35, 0.22, 0.12), open_shirt=False)

K.world((0.98, 0.94, 0.88), 0.35)
K.area("key", (-1.4, -1.4, 2.6), (0.8, -0.5, 0), 280, 2.5, (1, 0.95, 0.88))
K.area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 120, 3.0, (0.94, 0.96, 1))
K.area("rim", (0.6, 2.3, 2.3), (-2.3, 0, 0.3), 150, 1.0, (1.0, 0.85, 0.65))
sunl = bpy.data.lights.new("sun", "SUN"); sunl.energy = 3.0; sunl.color = (1, 0.9, 0.75); sunl.angle = 0.05
so = bpy.data.objects.new("sun", sunl); sc.collection.objects.link(so); so.rotation_euler = (math.radians(-50), math.radians(-30), 0)
K.camera(32)

def set_liq(obj, z0, h):
    obj.scale = (1, 1, max(h, 0.0005)); obj.location.z = z0 + max(h, 0.0005) / 2; obj.hide_render = h < 0.001

def frame_state(t):
    C = K.CH.location
    K.idle(t)
    for o in [K.CH] + list(K.CH.children_recursive): o.hide_render = t < TL["intro"]
    # defaults
    tub.location = TUB_SPOT if t >= TL["intro"] else hero.location + Vector((0, 0, 0.012)); tub.rotation_euler = (0, 0, 0.25 if t >= TL["intro"] else 0)
    shaker.location = SHAKER_SPOT if t >= TL['intro'] else Vector((0, 0, -5)); shaker.rotation_euler = (0, 0, 0); shlid.location = (0, 0, 0.17); shlid.rotation_euler = (0, 0, 0)
    shlid.hide_render = t < TL["shake"] - 0.15
    milk.location = MILK_SPOT; milk.rotation_euler = (0, 0, -0.3)
    glass.location = GLASS_SPOT + Vector((0.08, 0.02, 0)); glass.rotation_euler = (0, 0, 0)
    scoop.location = (0, 0, -5); stream.location = (0, 0, -5); cstream.location = (0, 0, -5)
    for o in pdots + ice_drop: o.location = (0, 0, -5)
    # fill levels
    pw = clamp((t - TL["powder"] - 0.35) / 0.3); set_liq(powder_layer, 0.004, 0.02 * pw)
    mk = clamp((t - TL["milk"] - 0.25) / 0.45); set_liq(shliq, 0.004, 0.11 * mk)
    if t >= TL["shake"]: MILKC.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*vlerp((0.93, 0.9, 0.85), (0.5, 0.3, 0.17), ease((t - TL["shake"]) / 0.4)), 1)
    else: MILKC.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.93, 0.9, 0.85, 1)
    if t >= TL["shake"]: powder_layer.hide_render = True
    for i, o in enumerate(shake_ice):
        o.parent = shaker if t >= TL["ice"] + 0.35 + 0.08 * i else None
        o.location = (0.012 * math.cos(i * 1.7), 0.012 * math.sin(i * 1.7), 0.03 + 0.025 * i) if o.parent else (0, 0, -5)
        o.rotation_euler = (i, i * 0.7, 0)
    pr = clamp((t - TL["pour"] - 0.15) / 0.5); dr = clamp((t - TL["sip"] - 0.5) / 0.8) * 0.4
    set_liq(gliq, 0.006, 0.1 * pr * (1 - dr)); gfoam.location.z = (0.006 + 0.1 * pr * (1 - dr) + 0.004) if pr > 0.3 else -5
    for i, o in enumerate(gice): o.location = (0.014 * math.cos(i * 2.1), 0.014 * math.sin(i * 2.1), 0.02 + 0.03 * i) if t >= TL["pour"] else (0, 0, -5)
    straw.location = (0.015, 0, 0.12) if t >= TL["sip"] - 0.2 else (0, 0, -5)
    if t >= TL["shake"]: set_liq(shliq, 0.004, 0.11 * (1 - pr * 0.9))
    esp_on = t < TL["barista"] + 0.7
    K.set_emit(ESPL, 8.0 if esp_on else 0.0)
    smile, mopen, brow, squint, look = 0.6, K.talk(t, W_, 0.5), 0.0, 0.0, (0, 0)
    if t < TL["intro"]:
        tub.rotation_euler = (0, 0, -0.5 + 1.0 * ease(t / TL["intro"]))
    elif t < TL["yes"]:
        # holds the tub, reads label: "almost 20 g protein??"
        u = t - TL["intro"]; k = ease(u / 0.4)
        p = vlerp(TUB_SPOT + Vector((0, 0, TUB_H * 0.5)), C + Vector((-0.05, -0.45, 1.38)), k)
        K.hold(tub, "L", p, approach=(-1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, 0.1)); tub.location = p - Vector((0, 0, TUB_H * 0.5))
        K.free_arm("R", p + Vector((0.11, -0.04, 0.02)), point=True)
        smile, brow, look = 0.5, 0.9 if u > 1.0 else 0.4, (-0.3, -0.5)
        if u > 1.6: smile, mopen, look = 0.9, max(mopen, 0.4), (0, 0)
    elif t < TL["powder"]:
        # "Ja, bitte!" – hugs the tub
        u = t - TL["yes"]
        p = C + Vector((0.0, -0.3, 1.32))
        K.hold(tub, "L", p, approach=(-1, 0.3, 0), fdir=(0.3, -1, 0.3), obj_rot=(0, 0, 0.1)); tub.location = p - Vector((0, 0, TUB_H * 0.5))
        K.free_arm("R", p + Vector((0.1, -0.05, 0.0)), fdir=(-1, -0.2, 0.3), g=0.5)
        smile, mopen, squint, brow = 1.0, max(mopen, 0.4), 0.8, 0.8; K.head.rotation_euler = (0.05, 0, 0.25 * math.sin(u * 6))
    elif t < TL["milk"]:
        # scoop powder into the shaker
        u = t - TL["powder"]
        K.free_arm("L", TUB_SPOT + Vector((-0.08, -0.02, 0.06)), g=0.6)
        k = ease(u / 0.3); top = SHAKER_SPOT + Vector((0, 0, 0.2))
        sp = vlerp(TUB_SPOT + Vector((0, 0, TUB_H + 0.04)), top, k)
        tilt = 1.8 * ease((u - 0.35) / 0.2)
        scoop.location = sp; scoop.rotation_euler = (tilt, 0, 0)
        K.hold(None, "R", sp + Vector((0.0, 0.1, 0.012)), approach=(0, 0, 1), fdir=(0, 1, 0.2), g=0.9)
        for i, o in enumerate(pdots):
            tt = u - 0.4 - i * 0.012
            if tt > 0: o.location = top + Vector((0.01 * math.sin(i * 3), 0.01 * math.cos(i * 2), -4.9 * tt * tt - 0.02))
            if o.location.z < SHAKER_SPOT.z + 0.01: o.location = (0, 0, -5)
        smile, look = 0.8, (0.2, -0.9); K.head.rotation_euler = (0.25, 0, 0)
    elif t < TL["ice"]:
        # pour milk from the carton
        u = t - TL["milk"]; k = ease(u / 0.25)
        mp = vlerp(MILK_SPOT + Vector((0, 0, 0.1)), SHAKER_SPOT + Vector((0.07, 0, 0.3)), k)
        K.hold(milk, "R", mp, approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(0, -1.9 * k, 0)); milk.location = mp - Vector((0, 0, 0.1))
        if u > 0.25:
            mouth_p = K.world_of(milk, (0, 0, 0.21)); bot = SHAKER_SPOT + Vector((0, 0, 0.02 + 0.11 * mk))
            ln = max(mouth_p.z - bot.z, 0.01); stream.location = (mouth_p.x * 0.5, mouth_p.y, bot.z + ln / 2); stream.scale = (1, 1, ln)
            stream.location.x = (mouth_p.x + SHAKER_SPOT.x) / 2
        K.free_arm("L", SHAKER_SPOT + Vector((-0.07, -0.02, 0.08)), g=0.8)
        smile, look = 0.8, (0.2, -0.9); K.head.rotation_euler = (0.25, 0, 0)
    elif t < TL["shake"]:
        # ice cubes – dropped one by one from the left hand
        u = t - TL["ice"]
        hand = SHAKER_SPOT + Vector((-0.02, -0.02, 0.32))
        K.free_arm("L", hand + Vector((-0.03, 0, 0.04)), fdir=(0.3, -0.3, -1), palm=(0, 0, -1), g=0.5)
        for i, o in enumerate(ice_drop):
            tt = u - 0.08 * i
            if 0 < tt < 0.35: o.location = hand + Vector((0, 0, -4.9 * tt * tt)); o.rotation_euler = (tt * 9, tt * 7, 0)
        K.free_arm("R", C + Vector((0.25, -0.3, 1.05)), g=0.4)
        smile, look, brow = 0.9, (0, -0.9), 0.5; K.head.rotation_euler = (0.25, 0, 0)
    elif t < TL["pour"]:
        # SHAKE!
        u = t - TL["shake"]; k = ease(u / 0.15)
        c0 = vlerp(SHAKER_SPOT + Vector((0, 0, 0.1)), C + Vector((0.05, -0.42, 1.48)), k) + Vector((0.02 * math.sin(u * 50), 0, 0.05 * math.sin(u * 42) * k))
        K.hold(shaker, "R", c0 + Vector((0, 0, 0.03)), approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(0, 0.25 * math.sin(u * 42) * k, 0))
        shaker.location = c0 - Vector((0, 0, 0.1))
        K.free_arm("L", K.world_of(shlid, (-0.04, 0, 0.02)), fdir=(1, -0.2, -0.2), palm=(1, 0, 0), g=0.8)
        smile, mopen, squint, brow = 1.0, 0.5, 0.6, 0.9; K.head.rotation_euler = (0.0, 0, 0.12 * math.sin(u * 30))
        K.hips.location.z += 0.012 * math.sin(u * 42)
    elif t < TL["sip"]:
        # pour into the glass
        u = t - TL["pour"]; k = ease(u / 0.2)
        sp = GLASS_SPOT + Vector((-0.06, 0, 0.26))
        K.hold(shaker, "R", sp, approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(0, -1.9 * k, 0)); shaker.location = sp - Vector((0, 0, 0.08))
        shlid.hide_render = True
        if u > 0.15:
            mouth_p = K.world_of(shaker, (0, 0, 0.17)); bot = glass.location + Vector((0, 0, 0.006 + 0.1 * pr))
            ln = max(mouth_p.z - bot.z, 0.01); cstream.location = ((mouth_p.x + glass.location.x) / 2, glass.location.y, bot.z + ln / 2); cstream.scale = (1, 1, ln)
        K.free_arm("L", glass.location + Vector((-0.07, 0, 0.07)), fdir=(1, 0, 0.1), palm=(1, 0, 0), g=0.8)
        smile, look = 0.8, (0.3, -0.9); K.head.rotation_euler = (0.25, 0, 0)
    elif t < TL["barista"]:
        # sip through the straw, then show the tub ("choose your flavour")
        u = t - TL["sip"]
        mw = K.world_of(K.mouth)
        if u < 1.4:
            k = ease(u / 0.35)
            gp = vlerp(GLASS_SPOT + Vector((0.08, 0.02, 0.07)), mw + Vector((-0.015, -0.05, -0.19)), k)
            K.hold(glass, "R", gp, approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(0, -0.1 * k, 0)); glass.location = gp - Vector((0, 0, 0.07))
            K.free_arm("L", C + Vector((-0.25, -0.3, 1.05)), g=0.4)
            smile, squint, mopen = 0.5, 0.9 * k, 0.05; look = (0, -0.6)
        else:
            gp = C + Vector((0.24, -0.38, 1.3))
            K.hold(glass, "R", gp, approach=(1, 0, 0), fdir=(0, -1, 0.2)); glass.location = gp - Vector((0, 0, 0.07))
            k = ease((u - 1.4) / 0.35)
            p = vlerp(TUB_SPOT + Vector((0, 0, TUB_H * 0.5)), C + Vector((-0.2, -0.45, 1.42)), k)
            K.hold(tub, "L", p, approach=(-1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, 0.15)); tub.location = p - Vector((0, 0, TUB_H * 0.5))
            smile, brow, look = 1.0, 0.8, (-0.3, 0)
    elif t < TL["cta"]:
        # "my barista is officially unemployed" – the espresso machine powers down; he toasts with the glass
        u = t - TL["barista"]
        gp = C + Vector((0.2, -0.42, 1.48 + 0.03 * math.sin(u * 5)))
        K.hold(glass, "R", gp, approach=(1, 0, 0), fdir=(0, -1, 0.2), obj_rot=(0, 0.15 * math.sin(u * 5), 0)); glass.location = gp - Vector((0, 0, 0.07))
        K.free_arm("L", C + Vector((-0.4, -0.25, 1.32)), point=True)
        smile, mopen, brow, look = 1.0, max(mopen, 0.2), 0.9, (-0.9, 0.1); K.head.rotation_euler = (0, 0, 0.45)
    else:
        p = C + Vector((0.27, -0.36, 1.5 + 0.03 * math.sin(t * 6)))
        K.hold(tub, "R", p, approach=(1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, -0.1)); tub.location = p - Vector((0, 0, TUB_H * 0.5))
        K.free_arm("L", C + Vector((-0.42, -0.4, 1.08)), point=True)
        glass.location = GLASS_SPOT
        smile, brow, look = 1.0, 0.8, (-0.5, -0.6)
    K.face(smile, mopen, brow, look, squint, t)
    K.set_shot(*shot(t))

def shot(t):
    C = K.CH.location
    if t < TL["intro"]:
        a = -0.45 + 0.6 * t / TL["intro"]; c = hero.location + Vector((0, 0, TUB_H * 0.55))
        cam_p = c + Vector((0.42 * math.sin(a), -0.42 * math.cos(a), 0.04))
        return cam_p, c + Vector((0, 0, -0.005)), c + (cam_p - c).normalized() * 0.04, 5.6
    if t < TL["powder"]:
        u = (t - TL["intro"]) / (TL["powder"] - TL["intro"])
        return C + Vector((0.1, -1.4 + 0.25 * u, 1.55)), C + Vector((-0.03, -0.1, 1.42)), C + Vector((0, -0.4, 1.45)), 2.8
    if t < TL["shake"]:
        # over-the-counter close-up on the shaker
        c = SHAKER_SPOT + Vector((0, 0, 0.15))
        return c + Vector((0.12, -0.62, 0.3)), c + Vector((0, 0, 0.0)), c, 3.2
    if t < TL["pour"]:
        return C + Vector((0.05, -1.05, 1.55)), C + Vector((0.03, -0.1, 1.48)), C + Vector((0, -0.4, 1.5)), 2.6
    if t < TL["sip"]:
        c = GLASS_SPOT + Vector((0, 0, 0.12))
        return c + Vector((0.05, -0.6, 0.18)), c, c, 3.2
    if t < TL["barista"]:
        return C + Vector((0.02, -1.2, 1.56)), C + Vector((0.0, -0.1, 1.45)), C + Vector((0, -0.4, 1.5)), 2.8
    if t < TL["cta"]:
        u = (t - TL["barista"]) / (TL["cta"] - TL["barista"])
        return C + Vector((0.55, -1.7, 1.55)), C + Vector((-0.35, 0.2, 1.3)), C + Vector((0, -0.3, 1.5)), 4.0
    u = (t - TL["cta"]) / 1.6
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def anchor_objs():
    return dict(tub=K.world_of(tub, (0, 0, TUB_H * 0.55)), glass=K.world_of(glass, (0, 0, 0.08)), shaker=K.world_of(shaker, (0, 0, 0.1)),
                esp=K.world_of(ESP, (0, 0, 0.3)), head=K.world_of(K.head, (0, 0, 0.14)))

K.setup_render(args, exposure=-0.4)
K.run(args, HERE, frame_state, anchor_objs)
