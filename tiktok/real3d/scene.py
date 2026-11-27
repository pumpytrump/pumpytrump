"""Blender (bpy) scene for the 3D Schokoellsen video.
python3 scene.py --frames 0-383 --res 720 --samples 24 --out out/frames   (renders PNGs + anchors json)
python3 scene.py --test 1.0,4.6,5.5,7.0,9.0,11.0,13.5,15.4 --samples 8      (quick stills)
"""
import bpy, math, json, os, sys, random, argparse
from mathutils import Vector, Euler, Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
FPS = 24
TL = dict(hook=0.0, drawer=3.44, burst=4.55, wide=5.0, board=6.26, b2=7.06, buero=8.32, eat=10.06,
          clockspin=10.8, witz=12.36, bfd=13.96, cta=15.02, end=16.0)

ap = argparse.ArgumentParser()
ap.add_argument("--frames", default="0-383"); ap.add_argument("--res", type=int, default=720)
ap.add_argument("--samples", type=int, default=24); ap.add_argument("--out", default=os.path.join(HERE, "out", "frames"))
ap.add_argument("--test", default="")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
rnd = random.Random(4)

# ------------------------------------------------------------------ helpers
def mat(name, col, rough=0.5, sss=0.0, metal=0.0, emit=None, es=0.0, coat=0.0, sheen=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.02
    if coat: b.inputs["Coat Weight"].default_value = coat
    if sheen: b.inputs["Sheen Weight"].default_value = sheen
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = es
    return m

def img_mat(name, path):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.35; b.inputs["Coat Weight"].default_value = 0.3
    return m, t.image

def link(o, parent=None, m=None, smooth=True, sub=0, bevel=0.0, seg=3):
    if parent: o.parent = parent
    if m: o.data.materials.append(m)
    if smooth and o.type == "MESH":
        for p in o.data.polygons: p.use_smooth = True
    if bevel:
        md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = seg; md.limit_method = "NONE"
    if sub:
        md = o.modifiers.new("sub", "SUBSURF"); md.levels = 1; md.render_levels = sub
    return o

def box(name, dims, loc, parent=None, m=None, bevel=0.0, rot=(0, 0, 0), sub=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.data.transform(Matrix.Diagonal((dims[0], dims[1], dims[2], 1.0)))
    o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=bool(bevel), bevel=bevel, sub=sub)

def sphere(name, r, loc, scale=(1, 1, 1), parent=None, m=None, rot=(0, 0, 0), sub=0, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, rotation=rot, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = name; o.scale = scale
    return link(o, parent, m, sub=sub)

def cyl(name, r, depth, loc, parent=None, m=None, rot=(0, 0, 0), verts=32, bevel=0.0, sub=0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name
    return link(o, parent, m, smooth=True, bevel=bevel, sub=sub)

def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o)
    o.location = loc; o.parent = parent; o.empty_display_size = 0.05
    return o

def plane(name, w, h, loc, rot, m, parent=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.transform(Matrix.Diagonal((w, h, 1.0, 1.0)))
    o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=False)

# ------------------------------------------------------------------ materials
SKIN = mat("skin", (0.78, 0.55, 0.42), rough=0.45, sss=0.25)
LIP = mat("lip", (0.55, 0.25, 0.22), rough=0.4, sss=0.2)
MOUTH = mat("mouth", (0.18, 0.04, 0.04), rough=0.6)
TEETH = mat("teeth", (0.95, 0.93, 0.88), rough=0.3)
HAIR = mat("hair", (0.09, 0.055, 0.035), rough=0.55, sheen=0.4)
BROW = mat("brow", (0.08, 0.05, 0.03), rough=0.7)
EYEW = mat("eyew", (0.95, 0.95, 0.95), rough=0.15, coat=1.0)
IRIS = mat("iris", (0.22, 0.12, 0.05), rough=0.1, coat=1.0)
PUPIL = mat("pupil", (0.01, 0.01, 0.01), rough=0.05, coat=1.0)
HOOD = mat("hoodie", (0.05, 0.08, 0.16), rough=0.8, sheen=0.15)
HOOD2 = mat("hoodie2", (0.035, 0.055, 0.11), rough=0.8, sheen=0.15)
JEANS = mat("jeans", (0.16, 0.2, 0.3), rough=0.8, sheen=0.1)
SHOE = mat("shoe", (0.93, 0.93, 0.92), rough=0.5)
SOLE = mat("sole", (0.2, 0.2, 0.2), rough=0.7)
STRING = mat("string", (0.9, 0.9, 0.88), rough=0.7)
FLOOR = mat("floor", (0.5, 0.36, 0.24), rough=0.35)
WALL = mat("wall", (0.86, 0.85, 0.82), rough=0.9)
DESK = mat("desk", (0.93, 0.93, 0.92), rough=0.25, coat=0.3)
METAL = mat("metal", (0.25, 0.25, 0.27), rough=0.3, metal=1.0)
BLACK = mat("black", (0.02, 0.02, 0.025), rough=0.15, coat=1.0)
SCREEN = mat("screen", (0.05, 0.1, 0.2), rough=0.2, emit=(0.25, 0.55, 0.95), es=2.5)
GOLD = mat("gold", (1.0, 0.75, 0.3), rough=0.2, metal=1.0)
RED = mat("boxred", (0.75, 0.04, 0.06), rough=0.4, coat=0.3)
WHITE = mat("white", (0.95, 0.95, 0.95), rough=0.4)
GREEN = mat("leaf", (0.12, 0.38, 0.12), rough=0.5, sss=0.1)
POT = mat("pot", (0.85, 0.82, 0.78), rough=0.6)
SKY = mat("sky", (0.8, 0.9, 1.0), emit=(0.85, 0.93, 1.0), es=4.0)
WOODD = mat("woodd", (0.35, 0.22, 0.12), rough=0.5)
FRONT, _ = img_mat("bar_front", os.path.join(A, "bar.png"))
CHOC = mat("choc", (0.32, 0.17, 0.08), rough=0.35, coat=0.2)

# wood grain on the floor
nt = FLOOR.node_tree; b = nt.nodes["Principled BSDF"]
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3; wv.inputs["Distortion"].default_value = 4
cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.42, 0.29, 0.18, 1); cr.color_ramp.elements[1].color = (0.6, 0.44, 0.3, 1)
nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])

# ------------------------------------------------------------------ room
plane("floor", 14, 14, (0, 2, 0), (0, 0, 0), FLOOR)
plane("wall", 14, 6, (0, 3.0, 3), (math.pi / 2, 0, 0), WALL)
plane("wallL", 8, 6, (-2.6, 0, 3), (math.pi / 2, 0, math.pi / 2), WALL)
# window
for (w, h, x, z) in ((1.3, 0.06, -1.25, 2.35), (1.3, 0.06, -1.25, 1.0), (0.06, 1.4, -1.9, 1.67), (0.06, 1.4, -0.6, 1.67), (0.04, 1.4, -1.25, 1.67)):
    box("wf", (w, 0.08, h), (x, 2.96, z), m=WHITE)
plane("pane", 1.28, 1.32, (-1.25, 2.995, 1.67), (math.pi / 2, 0, 0), SKY)
# baseboard
box("base", (14, 0.03, 0.1), (0, 2.985, 0.05), m=WHITE)
# desk
box("desktop", (1.8, 0.8, 0.045), (0, 0.6, 0.76), m=DESK, bevel=0.01)
for x in (-0.85, 0.85):
    for y in (0.25, 0.95): box("leg", (0.04, 0.04, 0.74), (x, y, 0.37), m=METAL, bevel=0.005)
box("unit", (0.46, 0.62, 0.52), (0.6, 0.6, 0.47), m=DESK, bevel=0.01)
drawer = box("drawer", (0.42, 0.58, 0.15), (0.6, 0.6, 0.62), m=DESK, bevel=0.008)
box("dhandle", (0.2, 0.02, 0.02), (0, -0.3, 0.0), parent=drawer, m=METAL, bevel=0.005)
box("d2", (0.42, 0.02, 0.15), (0.6, 0.29, 0.43), m=DESK, bevel=0.008); box("h2", (0.2, 0.02, 0.02), (0.6, 0.275, 0.43), m=METAL)
box("d3", (0.42, 0.02, 0.15), (0.6, 0.29, 0.27), m=DESK, bevel=0.008); box("h3", (0.2, 0.02, 0.02), (0.6, 0.275, 0.27), m=METAL)
# monitor, keyboard, mug
box("mon", (0.62, 0.035, 0.38), (-0.62, 0.8, 1.12), m=BLACK, bevel=0.01, rot=(0, 0, 0.35))
plane("scr", 0.58, 0.34, (-0.626, 0.781, 1.125), (math.pi / 2, 0, 0.35), SCREEN)
box("monstand", (0.05, 0.05, 0.2), (-0.6, 0.84, 0.88), m=METAL); box("monfoot", (0.22, 0.16, 0.012), (-0.6, 0.82, 0.79), m=METAL)
box("kb", (0.44, 0.14, 0.018), (-0.55, 0.5, 0.79), m=BLACK, bevel=0.004, rot=(0, 0, 0.2))
cyl("mug", 0.045, 0.1, (0.55, 0.42, 0.83), m=WHITE); cyl("coffee", 0.04, 0.01, (0.55, 0.42, 0.875), m=CHOC)
# plant
cyl("pot", 0.17, 0.36, (-1.9, 2.4, 0.18), m=POT)
for i in range(14):
    a = i * 2.4; r = 0.12 + 0.06 * (i % 3)
    sphere("leaf", 0.13, (-1.9 + r * math.cos(a), 2.4 + r * math.sin(a), 0.55 + 0.06 * i), (1, 0.4, 1.4), m=GREEN, rot=(0.4 * math.sin(a), 0.4 * math.cos(a), a), seg=16)
# wall clock
clock = empty("clock", (0.55, 2.975, 2.05))
cyl("clockrim", 0.22, 0.04, (0, 0, 0), parent=clock, m=BLACK, rot=(math.pi / 2, 0, 0))
cyl("clockface", 0.2, 0.045, (0, -0.002, 0), parent=clock, m=WHITE, rot=(math.pi / 2, 0, 0))
for i in range(12):
    a = i * math.pi / 6; box("tick", (0.012, 0.01, 0.035), (0.17 * math.sin(a), -0.03, 0.17 * math.cos(a)), parent=clock, m=BLACK, rot=(0, a, 0))
hh = empty("hourhand", (0, -0.035, 0), clock); box("hh", (0.016, 0.008, 0.1), (0, 0, 0.045), parent=hh, m=BLACK)
mh = empty("minhand", (0, -0.04, 0), clock); box("mh", (0.01, 0.008, 0.15), (0, 0, 0.07), parent=mh, m=BLACK)
# whiteboard on stand
wb = empty("whiteboard", (0.98, 1.75, 0))
box("wbframe", (1.02, 0.04, 0.74), (0, 0, 1.58), parent=wb, m=METAL, bevel=0.01)
box("wbboard", (0.96, 0.045, 0.68), (0, -0.003, 1.58), parent=wb, m=WHITE)
for x in (-0.4, 0.4): box("wbleg", (0.03, 0.03, 1.25), (x, 0.05, 0.62), parent=wb, m=METAL)
box("wbtray", (0.8, 0.06, 0.02), (0, -0.04, 1.23), parent=wb, m=METAL)
WB_CORNERS = [(-0.48, -0.03, 1.92), (0.48, -0.03, 1.92), (0.48, -0.03, 1.24), (-0.48, -0.03, 1.24)]
# pedestal (hook)
ped = empty("pedestal", (0, -0.55, 0))
cyl("pedbody", 0.32, 0.86, (0, 0, 0.43), parent=ped, m=BLACK, bevel=0.01)
bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.018, location=(0, 0, 0.87)); t = bpy.context.object; link(t, ped, GOLD)
bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.012, location=(0, 0, 0.05)); t = bpy.context.object; link(t, ped, GOLD)

# ------------------------------------------------------------------ product boxes (real packaging on front & back)
BW, BH, BD = 0.30, 0.104, 0.024
def choco_box(name, loc=(0, 0, 0), parent=None):
    root = empty(name, loc, parent)
    box(name + "_b", (BW, BD, BH), (0, 0, 0), parent=root, m=RED, bevel=0.002)
    plane(name + "_f", BW * 0.995, BH * 0.99, (0, -BD / 2 - 0.0008, 0), (math.pi / 2, 0, 0), FRONT, parent=root)
    plane(name + "_k", BW * 0.995, BH * 0.99, (0, BD / 2 + 0.0008, 0), (math.pi / 2, 0, math.pi), FRONT, parent=root)
    return root

stack = empty("stack", (0, 0, 0.88), ped)
stack_boxes = []
for i in range(4):
    b = choco_box(f"st{i}", ((i - 1.5) * 0.02, 0.03 * i, BH / 2 + 0.002 + i * 0.065), stack)
    b.rotation_euler = (0.0, 0.0, 0.0)
    stack_boxes.append(b)
# bars in drawer + flying bars
fly = []
for i in range(16):
    b = choco_box(f"fly{i}", (0, 0, -5)); fly.append(b)
DESK_SPOTS = [(-0.75 + (i % 6) * 0.29 + rnd.uniform(-0.05, 0.05), 0.33 + (i // 6) * 0.2 + rnd.uniform(-0.03, 0.03)) for i in range(16)]
hand_bar = choco_box("handbar", (0, 0, -5))
# loose chocolate piece (for eating)
piece = box("piece", (0.06, 0.02, 0.045), (0, 0, -5), m=CHOC, bevel=0.004)

# ------------------------------------------------------------------ character
CH = empty("char", (0, 1.22, 0))
hips = empty("hips", (0, 0, 0.97), CH)
box("pelvis", (0.36, 0.22, 0.2), (0, 0, 0.0), parent=hips, m=JEANS, bevel=0.07, sub=2)
spine = empty("spine", (0, 0, 0.06), hips)
box("torso", (0.44, 0.25, 0.56), (0, 0, 0.28), parent=spine, m=HOOD, bevel=0.11, sub=2)
box("pocket", (0.3, 0.02, 0.13), (0, -0.125, 0.14), parent=spine, m=HOOD2, bevel=0.03, sub=1)
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.045, location=(0, 0.04, 0.56), rotation=(1.2, 0, 0)); link(bpy.context.object, spine, HOOD, sub=1)
for x in (-0.045, 0.045): cyl("string", 0.006, 0.16, (x, -0.128, 0.44), parent=spine, m=STRING)
neck = empty("neck", (0, 0, 0.535), spine)
cyl("neckm", 0.054, 0.12, (0, 0, 0.03), parent=neck, m=SKIN)
head = empty("head", (0, 0, 0.06), neck)
sphere("skull", 0.124, (0, 0, 0.135), (0.93, 1.0, 1.16), parent=head, m=SKIN, sub=1)
sphere("jaw", 0.1, (0, -0.02, 0.07), (0.95, 0.95, 0.75), parent=head, m=SKIN, sub=1)
# stubble shadow
STUB = mat("stubble", (0.42, 0.3, 0.24), rough=0.8)
sphere("stub", 0.101, (0, -0.022, 0.066), (0.95, 0.95, 0.72), parent=head, m=STUB, sub=1)
sphere("hairtop", 0.134, (0, 0.02, 0.2), (0.98, 1.04, 0.86), parent=head, m=HAIR, sub=1)
box("fringe", (0.19, 0.06, 0.05), (0.01, -0.085, 0.262), parent=head, m=HAIR, bevel=0.022, rot=(0.5, 0, 0.08), sub=1)
for x in (-1, 1):
    sphere("ear", 0.034, (x * 0.118, 0.0, 0.125), (0.35, 0.7, 1.0), parent=head, m=SKIN)
    sphere("sideburn", 0.03, (x * 0.112, -0.01, 0.17), (0.4, 0.9, 1.4), parent=head, m=HAIR)
eyes = []
for x in (-1, 1):
    e = empty("eye", (x * 0.041, -0.1, 0.138), head)
    sphere("eyew", 0.024, (0, 0, 0), parent=e, m=EYEW)
    ir = empty("iris", (0, 0, 0), e)
    sphere("irism", 0.0145, (0, -0.017, 0), (1, 0.5, 1), parent=ir, m=IRIS)
    sphere("pup", 0.0068, (0, -0.0235, 0), (1, 0.4, 1), parent=ir, m=PUPIL)
    lid = sphere("lid", 0.0255, (0, 0, 0), (1, 1, 1), parent=e, m=SKIN)   # upper lid closes by moving down
    lid.scale = (1, 1, 0.01)
    eyes.append((e, ir, lid))
brows = [box("brow", (0.05, 0.012, 0.011), (x * 0.043, -0.112, 0.176), parent=head, m=BROW, bevel=0.004) for x in (-1, 1)]
sphere("nose", 0.02, (0, -0.128, 0.108), (0.8, 1.2, 1.3), parent=head, m=SKIN, sub=1)
mouth = empty("mouth", (0, -0.112, 0.058), head)
mopen = sphere("mopen", 0.026, (0, 0, 0), (1.3, 0.35, 0.3), parent=mouth, m=MOUTH)
teeth = box("teeth", (0.04, 0.008, 0.008), (0, -0.004, 0.006), parent=mouth, m=TEETH, bevel=0.003)
lipu = cyl("lip", 0.0052, 0.062, (0, -0.002, 0.0), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
sd = lipu.modifiers.new("bend", "SIMPLE_DEFORM"); sd.deform_method = "BEND"; sd.deform_axis = "Y"; sd.angle = 0.6
lipd = cyl("lipd", 0.0048, 0.05, (0, -0.002, -0.01), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
sd2 = lipd.modifiers.new("bend", "SIMPLE_DEFORM"); sd2.deform_method = "BEND"; sd2.deform_axis = "Y"; sd2.angle = 0.6

def arm(side):
    s = empty("sh" + side, (side_x(side) * 0.235, 0, 0.47), spine)
    sphere("shm", 0.062, (0, 0, 0), parent=s, m=HOOD, sub=1)
    cyl("uarm", 0.054, 0.3, (0, 0, -0.15), parent=s, m=HOOD, sub=1)
    el = empty("el" + side, (0, 0, -0.3), s)
    sphere("elm", 0.05, (0, 0, 0), parent=el, m=HOOD)
    cyl("farm", 0.046, 0.25, (0, 0, -0.125), parent=el, m=HOOD, sub=1)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.043, minor_radius=0.011, location=(0, 0, -0.245)); link(bpy.context.object, el, HOOD2)
    wr = empty("wr" + side, (0, 0, -0.26), el)
    cyl("wrist", 0.034, 0.05, (0, 0, -0.01), parent=wr, m=SKIN)
    sphere("palm", 0.05, (0, 0, -0.06), (0.5, 0.95, 1.05), parent=wr, m=SKIN, sub=1)
    sphere("thumb", 0.018, (side_x(side) * -0.01, -0.042, -0.045), (0.9, 0.9, 1.8), parent=wr, m=SKIN, rot=(0.5, 0, 0))
    fing = []
    for k in range(4):
        f = cyl("finger", 0.0105, 0.07, (0, 0.03 - k * 0.02, -0.12), parent=wr, m=SKIN)
        fing.append(f)
    point = cyl("pointf", 0.011, 0.08, (0, -0.03, -0.135), parent=wr, m=SKIN)
    return s, el, wr, fing, point
def side_x(side): return -1 if side == "L" else 1
shL, elL, wrL, fingL, ptL = arm("L")
shR, elR, wrR, fingR, ptR = arm("R")
def leg(side):
    t = empty("th" + side, (side_x(side) * 0.095, 0, -0.03), hips)
    cyl("thigh", 0.085, 0.47, (0, 0, -0.235), parent=t, m=JEANS, sub=1)
    k = empty("kn" + side, (0, 0, -0.47), t)
    cyl("shin", 0.07, 0.45, (0, 0, -0.225), parent=k, m=JEANS, sub=1)
    f = empty("ft" + side, (0, 0, -0.45), k)
    box("shoe", (0.11, 0.27, 0.085), (0, -0.06, -0.02), parent=f, m=SHOE, bevel=0.03, sub=1)
    box("sole", (0.115, 0.275, 0.02), (0, -0.06, -0.06), parent=f, m=SOLE, bevel=0.008)
    return t, k
thL, knL = leg("L"); thR, knR = leg("R")

# ------------------------------------------------------------------ lights / world / camera
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.86, 0.9, 1.0, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
def area(name, loc, rot, energy, size, col=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = col
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
area("key", (-1.6, -1.8, 3.0), (0.75, -0.45, 0), 420, 2.5, (1, 0.96, 0.9))
area("fill", (2.0, -1.5, 2.2), (0.9, 0.6, 0), 160, 3.0, (0.92, 0.95, 1))
area("rim", (0.6, 2.6, 2.8), (-0.7, 0.2, 0), 220, 1.5, (1, 0.95, 0.85))
area("window", (-1.25, 3.4, 1.7), (-math.pi / 2, 0, 0), 300, 1.4, (0.85, 0.92, 1))
camd = bpy.data.cameras.new("cam"); camd.lens = 30; camd.sensor_fit = "VERTICAL"; camd.sensor_height = 36
camd.dof.use_dof = True; camd.dof.aperture_fstop = 2.2
cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam

# ------------------------------------------------------------------ animation
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t

POSE0 = dict(spine=(0.0, 0.0, 0.0), headr=(0.0, 0.0, 0.0), shL=(0.0, 0.14, 0.0), shR=(0.0, -0.14, 0.0), elL=-0.25, elR=-0.25,
             wrL=(0, 0, 0), wrR=(0, 0, 0), smile=0.5, mopen=0.0, brow=0.0, look=(0.0, 0.0), ptL=0.0, ptR=0.0, squint=0.0)
def P(**kw): p = dict(POSE0); p.update(kw); return p
def mix(a, b, u):
    o = {}
    for k, va in a.items():
        vb = b.get(k, va)
        o[k] = tuple(lerp(x, y, u) for x, y in zip(va, vb)) if isinstance(va, tuple) else lerp(va, vb, u)
    return o
def track(keys, t, dur=0.3):
    cur = keys[0][1]
    for tk, pk in keys[1:]:
        if t >= tk + dur: cur = pk
        elif t > tk: return mix(cur, pk, ease((t - tk) / dur))
        else: break
    return cur

idle = P()
arms_up = P(shL=(0.0, 2.55, 0.0), shR=(0.0, -2.55, 0.0), elL=-0.35, elR=-0.35, smile=1.0, mopen=0.8, brow=1.0, headr=(-0.12, 0, 0), squint=0.5)
point_board = P(shR=(-0.35, -1.45, 0.0), elR=-0.15, ptR=1.0, headr=(0.0, 0.0, 0.55), look=(0.6, 0.0), smile=0.8, brow=0.6, spine=(0, 0.05, 0.12))
point_board2 = P(shR=(-0.5, -1.2, 0.0), elR=-0.25, ptR=1.0, shL=(-0.3, 0.35, 0.0), elL=-1.2, headr=(0.0, 0.0, 0.15), look=(0.0, 0.0), smile=1.0, mopen=0.4, brow=0.8, spine=(0, 0.05, 0.05))
spread = P(shL=(-0.45, 1.25, 0.0), shR=(-0.45, -1.25, 0.0), elL=-0.5, elR=-0.5, smile=1.0, mopen=0.5, brow=0.7)
eat = P(shR=(-1.15, -0.32, 0.0), elR=-1.7, shL=(-0.4, 0.3, 0.0), elL=-1.3, smile=0.6, mopen=0.0, squint=1.0, headr=(0.08, 0, 0.05), brow=0.3)
laugh = P(shR=(-1.0, -0.3, 0.0), elR=-1.6, shL=(-0.2, 0.25, 0.0), elL=-0.8, smile=1.0, mopen=0.9, squint=1.0, headr=(-0.15, 0, 0.1), brow=0.5)
cta_p = P(shL=(-0.75, 0.75, 0.0), elL=-0.15, ptL=1.0, shR=(-0.3, -2.4, 0.0), elR=-0.5, smile=1.0, mopen=0.5, brow=0.8, headr=(0.05, 0, -0.1), look=(-0.4, 0.4))
KEYS = [(0.0, idle), (TL["wide"], arms_up), (TL["board"], point_board), (TL["buero"], spread), (TL["eat"], eat),
        (TL["eat"] + 1.4, laugh), (TL["witz"], point_board2), (TL["bfd"], point_board), (TL["cta"], cta_p)]

def apply_pose(p, t):
    spine.rotation_euler = Euler(p["spine"])
    head.rotation_euler = Euler((p["headr"][0] + 0.03 * math.sin(t * 2.1), p["headr"][1] + 0.02 * math.sin(t * 1.3), p["headr"][2] + 0.04 * math.sin(t * 0.9)))
    shL.rotation_euler = Euler(p["shL"]); shR.rotation_euler = Euler(p["shR"])
    elL.rotation_euler = Euler((p["elL"], 0, 0)); elR.rotation_euler = Euler((p["elR"], 0, 0))
    for fing, pt, v in ((fingL, ptL, p["ptL"]), (fingR, ptR, p["ptR"])):
        for f in fing: f.scale = (1, 1, max(0.01, 1 - v))
        pt.scale = (1, 1, max(0.01, v)); pt.location.z = -0.1 - 0.04 * v
    lipu.modifiers["bend"].angle = lerp(-0.5, 1.1, p["smile"]); lipd.modifiers["bend"].angle = lerp(-0.4, 0.9, p["smile"])
    mo = p["mopen"]
    if p.get("chew"): mo = 0.15 + 0.35 * abs(math.sin(t * 9))
    mopen.scale = (1.3, 0.35, 0.12 + 0.75 * mo); lipd.location.z = -0.008 - 0.018 * mo
    teeth.scale = (1, 1, 1 if mo > 0.3 else 0.01)
    for i, b in enumerate(brows):
        b.location.z = 0.176 + 0.012 * p["brow"]; b.rotation_euler = (0, (1 if i else -1) * -0.12 * p["brow"], 0)
    blink = 1.0 if (t % 3.3) < 0.09 else 0.0
    lidk = max(blink, 0.55 * p["squint"])
    for e, ir, lid in eyes:
        ir.location = (0.006 * p["look"][0], 0, 0.004 * p["look"][1])
        lid.scale = (1.02, 1.02, max(0.01, lidk)); lid.location.z = 0.022 * (1 - lidk) * 0.0 + 0.004
    # breathing
    hips.location.z = 0.97 + 0.006 * math.sin(t * 2.4)

def shot(t):
    """camera position, look-at target, focus point."""
    if t < TL["drawer"]:
        u = t / TL["drawer"]
        return (0.08 + 0.04 * u, -1.3 + 0.2 * u, 1.12), (0, -0.55, 1.02), (0, -0.55, 1.02)
    if t < TL["wide"]:
        u = (t - TL["drawer"]) / (TL["wide"] - TL["drawer"])
        return (0.3, -0.55 + 0.1 * u, 0.98), (0.6, 0.25, 0.66), (0.6, 0.2, 0.66)
    if t < TL["board"] or TL["buero"] <= t < TL["eat"]:
        u = (t % 3) / 3
        return (-0.05, -1.6 + 0.12 * u, 1.5), (0, 0.9, 1.2), (0, 1.2, 1.4)
    if TL["board"] <= t < TL["buero"] or TL["witz"] <= t < TL["cta"]:
        return (0.42, -1.35, 1.5), (0.45, 1.3, 1.42), (0.2, 1.3, 1.5)
    if TL["eat"] <= t < TL["witz"]:
        u = (t - TL["eat"]) / (TL["witz"] - TL["eat"])
        return (0.1, -0.72 + 0.12 * u, 1.68), (0.12, 1.2, 1.66), (0, 1.15, 1.65)
    u = (t - TL["cta"]) / 1.0
    return (-0.1, -1.5 + 0.15 * u, 1.45), (0, 0.9, 1.22), (0, 1.2, 1.45)

def look_at(obj, loc, target):
    obj.location = loc
    d = Vector(target) - Vector(loc)
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def place_box(b, pos, rot):
    b.location = pos; b.rotation_euler = rot

def frame_state(t):
    p = track(KEYS, t)
    p = dict(p); p["chew"] = TL["eat"] + 0.3 <= t < TL["eat"] + 1.4
    apply_pose(p, t)
    # pedestal only in hook
    hook = t < TL["drawer"]
    for o in [ped] + list(ped.children_recursive): o.hide_render = not hook
    stack.rotation_euler = (0, 0, 0.35 * math.sin(t * 0.9) - 0.15)
    stack.location.z = 0.9 + 0.012 * math.sin(t * 3)
    # drawer
    op = ease((t - TL["drawer"] - 0.15) / 0.45)
    drawer.location.y = 0.6 - 0.36 * op
    # flying bars: start in drawer, arc out at burst, land on desk
    for i, b in enumerate(fly):
        st = TL["burst"] + i * 0.05; u = clamp((t - st) / 0.75)
        d0 = Vector((0.6 + (i % 3 - 1) * 0.11, drawer.location.y - 0.05 + (i // 3 % 2) * 0.12, 0.66 + (i // 6) * 0.026))
        sx, sy = DESK_SPOTS[i]
        d1 = Vector((sx, sy, 0.783 + 0.012 + (0.026 if i % 5 == 0 else 0)))
        if t < TL["drawer"]: place_box(b, (0, 0, -5), (0, 0, 0)); continue
        if u <= 0: place_box(b, d0, (math.pi / 2, 0, 0.1 * (i % 3)))
        else:
            pos = d0.lerp(d1, ease(u)); pos.z += 0.9 * math.sin(math.pi * u) * (0.8 + 0.4 * (i % 3) / 2)
            spin = (1 - u) * (3 + i % 4)
            place_box(b, pos, (math.pi / 2 + spin, spin * 0.5, rnd.uniform(-0.3, 0.3) * (1 - u) + 0.3 * math.sin(i)))
    # bar in right hand while eating / CTA
    if TL["eat"] <= t < TL["witz"] or t >= TL["cta"]:
        hand_bar.parent = wrR; hand_bar.location = (0, -0.045, -0.1); hand_bar.rotation_euler = (math.pi / 2, 0, math.pi / 2 if t >= TL["cta"] else 0.0)
        hand_bar.scale = (1, 1, 1) if t >= TL["cta"] else (0.82, 1, 1)
    else:
        hand_bar.parent = None; hand_bar.location = (0, 0, -5)
    # clock: normal, then spins to lunchtime
    spin = ease((t - TL["clockspin"]) / 1.3)
    minutes = 9 * 60 + 5 + 3 * t + spin * (175 - 3 * t)
    mh.rotation_euler = (0, (minutes % 60) / 60 * 2 * math.pi, 0); hh.rotation_euler = (0, (minutes / 60 % 12) / 12 * 2 * math.pi, 0)
    loc, tgt, foc = shot(t)
    look_at(cam, loc, tgt)
    camd.dof.focus_distance = (Vector(foc) - Vector(loc)).length
    camd.dof.aperture_fstop = 1.8 if hook else 2.8

def anchors():
    bpy.context.view_layer.update()
    m = wb.matrix_world
    pts = []
    for c in WB_CORNERS:
        v = world_to_camera_view(sc, cam, m @ Vector(c)); pts.append((v.x, 1 - v.y, v.z))
    hv = world_to_camera_view(sc, cam, head.matrix_world @ Vector((0, 0, 0.14)))
    return dict(board=pts, head=(hv.x, 1 - hv.y))

# ------------------------------------------------------------------ render settings
r = sc.render; r.engine = "CYCLES"
sc.cycles.device = "CPU"; sc.cycles.samples = args.samples; sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.max_bounces = 5; sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 4; sc.cycles.use_adaptive_sampling = True
r.resolution_x = int(args.res * 9 / 16); r.resolution_y = args.res; r.resolution_percentage = 100
r.use_persistent_data = True; r.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Punchy"
except Exception: pass
sc.view_settings.exposure = -0.55
os.makedirs(args.out, exist_ok=True)

if os.environ.get("DEBUG"):
    frame_state(1.0); bpy.context.view_layer.update()
    for o in brows + [eyes[0][0], head, sc.objects["skull"], sc.objects["fringe"]]:
        print("DBG", o.name, tuple(round(v,3) for v in o.matrix_world.translation), tuple(round(v,3) for v in o.location), o.parent.name if o.parent else None, tuple(round(v,3) for v in o.dimensions))
    sys.exit(0)
if os.environ.get("HEADCAM"):
    def shot(t): return (0.0, 0.3, 1.72), (0.0, 1.2, 1.68), (0.0, 1.12, 1.7)
if args.test:
    for ts in [float(x) for x in args.test.split(",")]:
        frame_state(ts); r.filepath = os.path.join(args.out, f"test_{ts:05.2f}.png")
        bpy.ops.render.render(write_still=True); print("rendered", ts, flush=True)
else:
    a, b = [int(x) for x in args.frames.split("-")]
    anc_path = os.path.join(args.out, f"anchors_{a:04d}_{b:04d}.json"); anc = {}
    for f in range(a, b + 1):
        t = f / FPS
        frame_state(t); anc[f] = anchors()
        r.filepath = os.path.join(args.out, f"{f:04d}.png")
        if not os.path.exists(r.filepath):
            bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)
        json.dump(anc, open(anc_path, "w"))
