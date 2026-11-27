"""Blender scene: More ZERUP Peach Iced Tea – sunny kitchen, character pours syrup into water, drinks, CTA.
python3 scene.py --test 0.5,1.5,3.0,4.6,6.5,8.4,9.6,12.0,15.0 --samples 8 --res 640 --out out/test
python3 scene.py --frames 0-391 --res 1280 --samples 12 --out out/frames
"""
import bpy, bmesh, math, json, os, sys, random, argparse
from mathutils import Vector, Euler, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
FPS = 24
W_ = json.load(open(os.path.join(A, "words.json")))
T = [w[1] for w in W_]
TL = dict(medium=1.1, pour=1.9, color=2.5, ice=3.86, zero=5.66, drink=7.74, shades=9.3, sorten=11.2, cta=14.08, end=16.3)

ap = argparse.ArgumentParser()
ap.add_argument("--frames", default="0-391"); ap.add_argument("--res", type=int, default=1280)
ap.add_argument("--samples", type=int, default=12); ap.add_argument("--out", default=os.path.join(HERE, "out", "frames"))
ap.add_argument("--test", default="")
args = ap.parse_args(sys.argv[1:])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ helpers
def mat(name, col, rough=0.5, sss=0.0, metal=0.0, emit=None, es=0.0, coat=0.0, sheen=0.0, trans=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["IOR"].default_value = ior
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss; b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.02
    if coat: b.inputs["Coat Weight"].default_value = coat
    if sheen: b.inputs["Sheen Weight"].default_value = sheen
    if trans: b.inputs["Transmission Weight"].default_value = trans
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = es
    return m

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
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object; o.name = name
    o.data.transform(Matrix.Diagonal((dims[0], dims[1], dims[2], 1.0))); o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=bool(bevel), bevel=bevel, sub=sub)

def sphere(name, r, loc, scale=(1, 1, 1), parent=None, m=None, rot=(0, 0, 0), sub=0, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = name; o.location = loc; o.rotation_euler = rot; o.scale = scale
    return link(o, parent, m, sub=sub)

def cyl(name, r, depth, loc, parent=None, m=None, rot=(0, 0, 0), verts=32, bevel=0.0, sub=0, cap=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, end_fill_type="NGON" if cap else "NOTHING")
    o = bpy.context.object; o.name = name; o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=True, bevel=bevel, sub=sub)

def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o)
    o.location = loc; o.parent = parent; o.empty_display_size = 0.05
    return o

def plane(name, w, h, loc, rot, m, parent=None):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.object; o.name = name; o.data.transform(Matrix.Diagonal((w, h, 1.0, 1.0)))
    o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=False)

def node_mat_tex(name, path, rough=0.3, coat=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); t.extension = "EXTEND"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = coat
    return m

# ------------------------------------------------------------------ materials
SKIN = mat("skin", (0.78, 0.55, 0.42), rough=0.45, sss=0.25)
LIP = mat("lip", (0.55, 0.25, 0.22), rough=0.4, sss=0.2)
MOUTH = mat("mouth", (0.18, 0.04, 0.04), rough=0.6)
TEETH = mat("teeth", (0.95, 0.93, 0.88), rough=0.3)
HAIR = mat("hair", (0.09, 0.055, 0.035), rough=0.55, sheen=0.3)
BROW = mat("brow", (0.08, 0.05, 0.03), rough=0.7)
EYEW = mat("eyew", (0.95, 0.95, 0.95), rough=0.15, coat=1.0)
IRIS = mat("iris", (0.22, 0.12, 0.05), rough=0.1, coat=1.0)
PUPIL = mat("pupil", (0.01, 0.01, 0.01), rough=0.05, coat=1.0)
STUB = mat("stubble", (0.42, 0.3, 0.24), rough=0.8)
TEE = mat("tee", (0.93, 0.92, 0.88), rough=0.85, sheen=0.2)        # white t-shirt
SHIRT = mat("shirt", (0.52, 0.62, 0.48), rough=0.8, sheen=0.2)     # open sage overshirt
SHIRT2 = mat("shirt2", (0.42, 0.52, 0.38), rough=0.8)
WALL = mat("wall", (0.93, 0.9, 0.85), rough=0.9)
CAB = mat("cab", (0.62, 0.7, 0.6), rough=0.45, coat=0.2)           # sage cabinets
CABW = mat("cabw", (0.95, 0.94, 0.9), rough=0.4)
WOOD = mat("wood", (0.55, 0.38, 0.22), rough=0.35, coat=0.3)
BRASS = mat("brass", (0.9, 0.7, 0.35), rough=0.25, metal=1.0)
FLOOR = mat("floor", (0.75, 0.72, 0.68), rough=0.5)
SKY = mat("sky", (0.9, 0.95, 1.0), emit=(1.0, 0.97, 0.9), es=6.0)
GREEN = mat("leaf", (0.12, 0.38, 0.12), rough=0.5, sss=0.1)
POT = mat("pot", (0.85, 0.5, 0.35), rough=0.7)
PEACH = mat("peach", (0.95, 0.45, 0.2), rough=0.45, sss=0.2)
PEACHIN = mat("peachin", (1.0, 0.68, 0.2), rough=0.3, sss=0.3)
def thin_glass(name, tint=(0.97, 0.99, 1.0)):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (*tint, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.03
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.5
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs["Fac"], mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m
GLASS = thin_glass("glass")
ICE = mat("ice", (0.92, 0.97, 1.0), rough=0.12, trans=1.0, ior=1.31)
LIQ = mat("liquid", (0.95, 0.98, 1.0), rough=0.0, trans=1.0, ior=1.33)
STREAM = mat("stream", (0.8, 0.25, 0.1), rough=0.1, trans=0.6, ior=1.33)
STRAW_R = mat("strawr", (0.9, 0.1, 0.12), rough=0.3); STRAW_W = mat("straww", (0.97, 0.97, 0.97), rough=0.3)
SHADES = mat("shades", (0.02, 0.02, 0.03), rough=0.05, coat=1.0)
TILE = mat("tile", (0.95, 0.95, 0.93), rough=0.15, coat=0.6)
BOT_LIQ = mat("botliq", (0.35, 0.12, 0.05), rough=0.1)
LABEL = node_mat_tex("label", os.path.join(A, "bottle.png"))
# subway tiles: brick texture
nt = TILE.node_tree; b = nt.nodes["Principled BSDF"]
br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 18; br.inputs["Mortar Size"].default_value = 0.012
br.inputs["Color1"].default_value = (0.95, 0.95, 0.93, 1); br.inputs["Color2"].default_value = (0.9, 0.9, 0.88, 1)
br.inputs["Mortar"].default_value = (0.75, 0.74, 0.72, 1); nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
# wood grain counter
nt = WOOD.node_tree; b = nt.nodes["Principled BSDF"]
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 2.5; wv.inputs["Distortion"].default_value = 6
cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.42, 0.27, 0.14, 1); cr.color_ramp.elements[1].color = (0.62, 0.44, 0.27, 1)
nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
# stripes on straw
nt = STRAW_R.node_tree; b = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord"); wv2 = nt.nodes.new("ShaderNodeTexWave"); wv2.wave_type = "BANDS"; wv2.bands_direction = "Z"
wv2.inputs["Scale"].default_value = 9; nt.links.new(tc.outputs["Object"], wv2.inputs["Vector"])
mx = nt.nodes.new("ShaderNodeValToRGB"); mx.color_ramp.interpolation = "CONSTANT"
mx.color_ramp.elements[0].color = (0.9, 0.08, 0.1, 1); mx.color_ramp.elements[1].position = 0.5; mx.color_ramp.elements[1].color = (0.97, 0.97, 0.97, 1)
nt.links.new(wv2.outputs["Fac"], mx.inputs["Fac"]); nt.links.new(mx.outputs["Color"], b.inputs["Base Color"])

# ------------------------------------------------------------------ kitchen
plane("floor", 12, 12, (0, 1.5, 0), (0, 0, 0), FLOOR)
plane("wall", 12, 5, (0, 2.6, 2.5), (math.pi / 2, 0, 0), WALL)
plane("wallL", 8, 5, (-2.4, 0.5, 2.5), (math.pi / 2, 0, math.pi / 2), WALL)
plane("backsplash", 4.2, 0.62, (0.4, 2.585, 1.25), (math.pi / 2, 0, 0), TILE)
# back counter + upper cabinets
box("bcab", (4.2, 0.6, 0.88), (0.4, 2.3, 0.44), m=CAB, bevel=0.01)
box("btop", (4.24, 0.64, 0.04), (0.4, 2.28, 0.9), m=WOOD, bevel=0.004)
for i in range(6):
    x = -1.3 + i * 0.68
    box("ucab", (0.66, 0.36, 0.7), (x, 2.42, 1.95), m=CAB, bevel=0.008)
    box("uhnd", (0.012, 0.015, 0.12), (x + 0.28, 2.235, 1.68), m=BRASS)
# window (bright, sun comes through it)
for (w, h, x, z) in ((1.1, 0.05, -1.0, 2.25), (1.1, 0.05, -1.0, 1.0), (0.05, 1.3, -1.55, 1.62), (0.05, 1.3, -0.45, 1.62), (0.04, 1.3, -1.0, 1.62)):
    box("wf", (w, 0.06, h), (x, 2.57, z), m=CABW)
plane("pane", 1.08, 1.22, (-1.0, 2.598, 1.62), (math.pi / 2, 0, 0), SKY)
# kettle + plant + jars on back counter
cyl("kettle", 0.09, 0.2, (0.9, 2.3, 1.02), m=CABW, bevel=0.02)
cyl("plantpot", 0.09, 0.16, (-0.2, 2.3, 1.0), m=POT)
for i in range(9):
    a = i * 2.3; sphere("leaf", 0.07, (-0.2 + 0.05 * math.cos(a), 2.3 + 0.05 * math.sin(a), 1.12 + 0.03 * i), (1, 0.4, 1.5), m=GREEN, rot=(0.5 * math.sin(a), 0.5 * math.cos(a), a), seg=12)
for i, x in enumerate((1.4, 1.55, 1.7)): cyl("jar", 0.055, 0.16 + 0.03 * i, (x, 2.3, 1.0 + 0.015 * i), m=GLASS)
# island
box("island", (2.4, 0.66, 0.88), (0, 0.75, 0.44), m=CABW, bevel=0.01)
for x in (-0.9, -0.3, 0.3, 0.9):
    box("door", (0.56, 0.01, 0.74), (x, 0.415, 0.46), m=CABW, bevel=0.004); box("dh", (0.14, 0.015, 0.012), (x, 0.405, 0.78), m=BRASS)
box("itop", (2.5, 0.74, 0.045), (0, 0.75, 0.9), m=WOOD, bevel=0.005)
TOP = 0.9225
# fruit bowl with peaches
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(-0.75, 0.8, TOP + 0.09)); bowl = bpy.context.object
bowl.scale = (1, 1, 0.55); link(bowl, m=CABW)
for i in range(4):
    a = i * 1.6; sphere("peach", 0.042, (-0.75 + 0.07 * math.cos(a), 0.8 + 0.06 * math.sin(a), TOP + 0.13 + 0.02 * (i % 2)), m=PEACH, sub=1, seg=24)
# cutting board with a peach half
box("board", (0.3, 0.2, 0.018), (0.62, 0.68, TOP + 0.009), m=WOOD, bevel=0.006, rot=(0, 0, 0.2))
sphere("peachhalf", 0.042, (0.58, 0.67, TOP + 0.03), (1, 1, 0.6), m=PEACHIN, seg=24)
# ice bowl
cyl("icebowl", 0.08, 0.06, (0.95, 0.75, TOP + 0.03), m=CABW, bevel=0.01)
for i in range(5): box("icec", (0.022, 0.022, 0.022), (0.93 + 0.02 * (i % 3), 0.73 + 0.02 * (i // 3), TOP + 0.07), m=ICE, bevel=0.005, rot=(i, i * 0.5, 0))

# ------------------------------------------------------------------ product bottle (revolved from real photo silhouette)
def build_bottle(name, height=0.14, depth=0.68):
    from PIL import Image
    im = Image.open(os.path.join(A, "bottle.png")).convert("RGBA"); Wp, Hp = im.size; px = im.load()
    s = height / Hp; cx = Wp / 2
    rows = []
    for r in range(0, Hp, 6):
        xs = [x for x in range(Wp) if px[x, r][3] > 140]
        if len(xs) < 2: continue
        rows.append((r, xs[0], xs[-1]))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); N = 48; rings = []
    for r, l, rr in rows:
        rad = (rr - l) / 2; c = (rr + l) / 2; ring = []
        for k in range(N):
            a = 2 * math.pi * k / N
            x = (c - cx + rad * math.cos(a)) * s; y = -rad * math.sin(a) * s * depth; z = (Hp - r) * s
            ring.append(bm.verts.new((x, y, z)))
        rings.append((r, l, rr, ring))
    for (r0, l0, rr0, a0), (r1, l1, rr1, a1) in zip(rings, rings[1:]):
        for k in range(N):
            f = bm.faces.new((a0[k], a0[(k + 1) % N], a1[(k + 1) % N], a1[k]))
            for lp in f.loops:
                v = lp.vert; lp[uvl].uv = ((v.co.x / s + cx) / Wp, v.co.z / s / Hp)
    for (_, _, _, ring), flip in ((rings[0], False), (rings[-1], True)):
        f = bm.faces.new(list(reversed(ring)) if flip else ring)
        for lp in f.loops: lp[uvl].uv = ((lp.vert.co.x / s + cx) / Wp, lp.vert.co.z / s / Hp)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(LABEL)
    for p in me.polygons: p.use_smooth = True
    md = o.modifiers.new("sub", "SUBSURF"); md.levels = 1; md.render_levels = 1
    root = empty(name + "_root", (0, 0, 0)); o.parent = root; o.location = (0, 0, -height / 2)   # root at bottle centre
    return root, o
bottle, bottle_mesh = build_bottle("zerup")
BOTTLE_H = 0.14
# hero pedestal: a round wooden stand with peaches + ice around (hook shot)
hero = empty("hero", (0.0, 0.62, TOP))
cyl("stand", 0.12, 0.03, (0, 0, 0.015), parent=hero, m=WOOD, bevel=0.006, verts=48)
for i, (x, y) in enumerate(((-0.16, 0.02), (0.17, -0.03), (-0.12, -0.1), (0.13, 0.08))):
    if i < 2: sphere("hpeach", 0.04, (x, y, 0.04), parent=hero, m=PEACH, sub=1, seg=24)
    else: box("hice", (0.024, 0.024, 0.024), (x, y, 0.014), parent=hero, m=ICE, bevel=0.006, rot=(0.3 * i, 0.2, i))

# ------------------------------------------------------------------ glass, liquid, ice, straw, shades
def make_glass():
    root = empty("glass_root", (0, 0, 0))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=48, radius1=0.04, radius2=0.047, depth=0.13)
    top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context="FACES")
    me = bpy.data.meshes.new("glass"); bm.to_mesh(me); bm.free()
    g = bpy.data.objects.new("glass", me); sc.collection.objects.link(g); g.parent = root; g.location = (0, 0, 0.065)
    me.materials.append(GLASS)
    for p in me.polygons: p.use_smooth = True
    pass
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=48, radius1=0.0355, radius2=0.041, depth=0.094)
    me2 = bpy.data.meshes.new("liquid"); bm.to_mesh(me2); bm.free()
    liq = bpy.data.objects.new("liquid", me2); sc.collection.objects.link(liq); liq.parent = root; liq.location = (0, 0, 0.06)
    me2.materials.append(LIQ)
    for p_ in me2.polygons: p_.use_smooth = True
    return root, liq
glass, liquid = make_glass()
ices = [box(f"ice{i}", (0.026, 0.026, 0.026), (0, 0, -5), m=ICE, bevel=0.006) for i in range(3)]
pslice = sphere("pslice", 0.035, (0, 0, -5), (1, 0.35, 0.6), m=PEACHIN, seg=24)
straw = empty("straw", (0, 0, -5))
cyl("strawm", 0.0045, 0.21, (0, 0, 0.105), parent=straw, m=STRAW_R, verts=16)
shades = empty("shades", (0, 0, -5))
for x in (-0.018, 0.018):
    cyl("lens", 0.015, 0.004, (x, 0, 0), parent=shades, m=SHADES, rot=(math.pi / 2, 0, 0))
box("bridge", (0.012, 0.004, 0.003), (0, 0, 0.004), parent=shades, m=SHADES)
for x in (-1, 1): box("arm", (0.003, 0.04, 0.003), (x * 0.034, 0.02, 0.004), parent=shades, m=SHADES)
stream = cyl("stream", 0.0035, 1.0, (0, 0, -5), m=STREAM, verts=12)
drops = [sphere(f"drop{i}", 0.006, (0, 0, -5), m=STREAM, seg=12) for i in range(6)]

# ------------------------------------------------------------------ character (upper body; legs hidden by island)
def side_x(side): return -1 if side == "L" else 1
CH = empty("char", (0, 1.38, 0))
hips = empty("hips", (0, 0, 0.97), CH)
box("pelvis", (0.36, 0.22, 0.2), (0, 0, 0.0), parent=hips, m=SHIRT2, bevel=0.07, sub=1)
spine = empty("spine", (0, 0, 0.06), hips)
box("torso", (0.42, 0.24, 0.55), (0, 0, 0.27), parent=spine, m=TEE, bevel=0.11, sub=2)
for x in (-1, 1):   # open overshirt panels
    box("panel", (0.1, 0.022, 0.52), (x * 0.165, -0.115, 0.27), parent=spine, m=SHIRT, bevel=0.02, sub=1, rot=(0, 0, x * 0.18))
    box("collar", (0.09, 0.03, 0.08), (x * 0.075, -0.1, 0.53), parent=spine, m=SHIRT, bevel=0.02, rot=(0.3, 0, x * 0.5))
neck = empty("neck", (0, 0, 0.535), spine)
cyl("neckm", 0.054, 0.12, (0, 0, 0.03), parent=neck, m=SKIN)
head = empty("head", (0, 0, 0.06), neck)
sphere("skull", 0.124, (0, 0, 0.135), (0.93, 1.0, 1.16), parent=head, m=SKIN, sub=1)
sphere("jaw", 0.1, (0, -0.02, 0.07), (0.95, 0.95, 0.75), parent=head, m=SKIN, sub=1)
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
    lid = sphere("lid", 0.0255, (0, 0, 0.004), (1.02, 1.02, 0.01), parent=e, m=SKIN)
    eyes.append((e, ir, lid))
brows = [box("brow", (0.05, 0.012, 0.011), (x * 0.043, -0.112, 0.176), parent=head, m=BROW, bevel=0.004) for x in (-1, 1)]
sphere("nose", 0.02, (0, -0.128, 0.108), (0.8, 1.2, 1.3), parent=head, m=SKIN, sub=1)
mouth = empty("mouth", (0, -0.112, 0.058), head)
MOPEN = sphere("mopen", 0.026, (0, 0, 0), (1.3, 0.35, 0.3), parent=mouth, m=MOUTH)
teeth = box("teeth", (0.04, 0.008, 0.008), (0, -0.004, 0.006), parent=mouth, m=TEETH, bevel=0.003)
lipu = cyl("lip", 0.0052, 0.062, (0, -0.002, 0.0), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
sd = lipu.modifiers.new("bend", "SIMPLE_DEFORM"); sd.deform_method = "BEND"; sd.deform_axis = "Y"; sd.angle = 0.6
lipd = cyl("lipd", 0.0048, 0.05, (0, -0.002, -0.01), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
sd2 = lipd.modifiers.new("bend", "SIMPLE_DEFORM"); sd2.deform_method = "BEND"; sd2.deform_axis = "Y"; sd2.angle = 0.6

UA, FA = 0.29, 0.25
def arm(side):
    s = empty("sh" + side, (side_x(side) * 0.225, 0, 0.47), spine); s.rotation_mode = "QUATERNION"
    sphere("shm", 0.062, (0, 0, 0), parent=s, m=SHIRT, sub=1)
    cyl("uarm", 0.054, UA, (0, 0, -UA / 2), parent=s, m=SHIRT, sub=1)
    el = empty("el" + side, (0, 0, -UA), s); el.rotation_mode = "QUATERNION"
    sphere("elm", 0.05, (0, 0, 0), parent=el, m=SHIRT)
    cyl("farm", 0.045, 0.16, (0, 0, -0.08), parent=el, m=SHIRT, sub=1)          # rolled-up sleeve
    cyl("cuff", 0.05, 0.03, (0, 0, -0.15), parent=el, m=SHIRT2)
    cyl("forearm", 0.037, 0.11, (0, 0, -0.2), parent=el, m=SKIN, sub=1)
    wr = empty("wr" + side, (0, 0, -FA), el); wr.rotation_mode = "QUATERNION"
    sphere("palm", 0.045, (0, 0, -0.055), (0.55, 0.95, 1.05), parent=wr, m=SKIN, sub=1)
    th = empty("thumb", (side_x(side) * -0.012, -0.038, -0.035), wr)
    cyl("thumbm", 0.011, 0.055, (0, 0, -0.027), parent=th, m=SKIN)
    fingers = []
    for k in range(4):
        f = empty("fing", (side_x(side) * -0.004, 0.028 - k * 0.019, -0.095), wr)
        cyl("f1", 0.0095, 0.045, (0, 0, -0.022), parent=f, m=SKIN)
        f2 = empty("fj", (0, 0, -0.045), f)
        cyl("f2", 0.0088, 0.035, (0, 0, -0.017), parent=f2, m=SKIN)
        fingers.append((f, f2))
    return s, el, wr, th, fingers
shL, elL, wrL, thL, fingL = arm("L")
shR, elR, wrR, thR, fingR = arm("R")

# ------------------------------------------------------------------ lights / world / camera
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.92, 0.88, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.3
def area(name, loc, rot, energy, size, col=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = col
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.5; sun.color = (1, 0.9, 0.75); sun.angle = 0.05
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(-55), math.radians(-28), 0)
area("key", (-1.4, -1.4, 2.6), (0.8, -0.5, 0), 260, 2.5, (1, 0.96, 0.92))
area("fill", (1.8, -1.2, 2.0), (0.9, 0.6, 0), 120, 3.0, (0.94, 0.96, 1))
area("window", (-1.0, 3.2, 1.6), (-math.pi / 2, 0, 0), 250, 1.2, (1, 0.95, 0.85))
camd = bpy.data.cameras.new("cam"); camd.lens = 32; camd.sensor_fit = "VERTICAL"; camd.sensor_height = 36
camd.dof.use_dof = True
cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam

# ------------------------------------------------------------------ animation helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def vlerp(a, b, t): return Vector(a).lerp(Vector(b), t)
def upd(): bpy.context.view_layer.update()

def ik_arm(sh, el, wr, target, pole, hand_rot=None):
    """Analytic 2-bone IK: point the arm at `target` (wrist, world), elbow bends toward `pole`.
    hand_rot: optional world rotation matrix (3x3) for the wrist."""
    upd()
    S = sh.matrix_world.translation.copy(); Tg = Vector(target)
    d = Tg - S; dist = min(max(d.length, 0.05), UA + FA - 0.002); dn = d.normalized()
    a = (UA * UA + dist * dist - FA * FA) / (2 * dist); h = math.sqrt(max(UA * UA - a * a, 0))
    pv = Vector(pole) - S; pv = (pv - dn * pv.dot(dn)); pv = pv.normalized() if pv.length > 1e-6 else Vector((0, 0, -1))
    E = S + dn * a + pv * h; Tg = S + dn * dist
    prot = sh.parent.matrix_world.to_quaternion()
    v1 = prot.inverted() @ (E - S)
    sh.rotation_quaternion = v1.to_track_quat("-Z", "Y"); upd()
    v2 = sh.matrix_world.to_quaternion().inverted() @ (Tg - E)
    el.rotation_quaternion = v2.to_track_quat("-Z", "Y"); upd()
    if hand_rot is not None:
        wr.rotation_quaternion = el.matrix_world.to_quaternion().inverted() @ hand_rot.to_quaternion()
    else:
        wr.rotation_quaternion = Quaternion()
    upd()

def hand_frame(fdir, palm_to_obj, side):
    """World rotation for a hand: fingers along fdir (local -Z), palm facing palm_to_obj."""
    z = -Vector(fdir).normalized()
    n = Vector(palm_to_obj); n = (n - (-z) * n.dot(-z)).normalized()
    x = (-n) if side == "R" else n           # right palm faces local -X, left palm faces +X
    y = z.cross(x).normalized(); x = y.cross(z).normalized()
    return Matrix((x, y, z)).transposed()

def grip(fingers, thumb, amount, side):
    for f, f2 in fingers:
        f.rotation_euler = (0, side_x(side) * -1.2 * amount, 0); f2.rotation_euler = (0, side_x(side) * -1.1 * amount, 0)
    thumb.rotation_euler = (0.6 * amount, side_x(side) * -0.6 * amount, 0)

def hold(obj, side, center, fdir=(0, -1, 0.25), approach=None, obj_rot=(0, 0, 0), pole=None, g=1.0, palm_off=0.045):
    """Place obj at `center` (world) and make hand `side` grip it from `approach` direction."""
    center = Vector(center)
    if approach is None: approach = Vector((side_x(side), 0.0, 0.0))
    n = -Vector(approach).normalized()                       # palm -> object
    R = hand_frame(fdir, n, side)
    fd = -(R @ Vector((0, 0, 1)))                              # finger direction (world)
    wrist = center - n * palm_off - fd * 0.055
    sh, el, wr, th, fing = (shL, elL, wrL, thL, fingL) if side == "L" else (shR, elR, wrR, thR, fingR)
    if pole is None: pole = sh.matrix_world.translation + Vector((side_x(side) * 0.4, 0.25, -0.5))
    ik_arm(sh, el, wr, wrist, pole, R)
    grip(fing, th, g, side)
    obj.location = center; obj.rotation_euler = obj_rot

def free_arm(side, target, pole_off=(0.4, 0.25, -0.5), fdir=None, point=False, g=0.3):
    sh, el, wr, th, fing = (shL, elL, wrL, thL, fingL) if side == "L" else (shR, elR, wrR, thR, fingR)
    upd()
    pole = sh.matrix_world.translation + Vector((side_x(side) * pole_off[0], pole_off[1], pole_off[2]))
    R = None
    if fdir is not None: R = hand_frame(fdir, Vector((-side_x(side), 0, 0)), side)
    ik_arm(sh, el, wr, target, pole, R)
    if point:
        for i, (f, f2) in enumerate(fing):
            a = 0.0 if i == 0 else 1.0
            f.rotation_euler = (0, side_x(side) * -1.5 * a, 0); f2.rotation_euler = (0, side_x(side) * -1.4 * a, 0)
        th.rotation_euler = (0.5, side_x(side) * -0.5, 0)
    else: grip(fing, th, g, side)

def face(smile=0.6, mopen=0.0, brow=0.0, look=(0, 0), squint=0.0, t=0.0, chew=False):
    lipu.modifiers["bend"].angle = lerp(-0.5, 1.1, smile); lipd.modifiers["bend"].angle = lerp(-0.4, 0.9, smile)
    MOPEN.scale = (1.3, 0.35, 0.12 + 0.75 * mopen); lipd.location.z = -0.008 - 0.018 * mopen
    teeth.scale = (1, 1, 1 if mopen > 0.3 else 0.01)
    for i, b in enumerate(brows):
        b.location.z = 0.176 + 0.012 * brow; b.rotation_euler = (0, (1 if i else -1) * -0.12 * brow, 0)
    blink = 1.0 if (t % 3.3) < 0.09 else 0.0; lidk = max(blink, 0.55 * squint)
    for e, ir, lid in eyes:
        ir.location = (0.006 * look[0], 0, 0.004 * look[1]); lid.scale = (1.02, 1.02, max(0.01, lidk))

# ------------------------------------------------------------------ choreography
GLASS_SPOT = Vector((0.05, 0.66, TOP))          # where the glass stands while pouring
def mouth_world():
    upd(); return mouth.matrix_world.translation.copy()

def frame_state(t):
    # body sway / breathing
    hips.location.z = 0.97 + 0.006 * math.sin(t * 2.4)
    spine.rotation_euler = (0.04 * math.sin(t * 0.8), 0.02 * math.sin(t * 1.1), 0)
    head.rotation_euler = (0.03 * math.sin(t * 2.1), 0, 0.05 * math.sin(t * 0.9))
    for o in (straw, shades, stream, pslice, *ices, *drops): o.location = (0, 0, -5)
    hero_on = t < TL["medium"]
    for o in [hero] + list(hero.children_recursive): o.hide_render = not hero_on
    # liquid colour: water -> peach iced tea
    mixk = ease((t - TL["pour"] - 0.25) / 1.6)
    col = vlerp((0.95, 0.98, 1.0), (0.92, 0.42, 0.12), mixk)
    LIQ.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*col, 1)
    LIQ.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 1.0 - 0.25 * mixk
    glass_items = t >= TL["ice"] + 0.1
    look = (0, 0); smile, mopen, brow, squint = 0.6, 0.0, 0.0, 0.0
    if hero_on:
        # bottle spins on the wooden stand; character idles in background holding the glass
        bottle.location = hero.location + Vector((0, 0, 0.03 + BOTTLE_H / 2)); bottle.rotation_euler = (0, 0, 0.6 * math.sin(t * 1.4) - 0.2)
        hold(glass, "L", CH.location + Vector((-0.2, -0.32, 1.12)), approach=(-1, 0, 0))
        free_arm("R", CH.location + Vector((0.28, -0.1, 0.95)))
        smile, squint = 0.2, 0.3
    elif t < TL["pour"]:
        # medium: bored face, plain water in left hand, right hand brings the bottle and squeezes
        u = ease((t - TL["medium"]) / 0.5)
        gl = CH.location + Vector((-0.1, -0.36, 1.2))
        hold(glass, "L", gl, approach=(-1, 0, 0))
        bpos = vlerp(CH.location + Vector((0.28, -0.36, 1.2)), gl + Vector((0.02, 0, 0.2)), u)
        brot = (0, lerp(0, -2.6, u), 0)
        hold(bottle, "R", bpos, approach=(1, 0, 0), fdir=(0, -1, 0.4), obj_rot=brot)
        smile, brow, look = 0.25 if t < TL["medium"] + 0.3 else 0.9, -0.3 if t < TL["medium"] + 0.3 else 0.8, (-0.6, -0.6)
        if u > 0.9:
            stream.location = gl + Vector((0.0, 0, 0.13)); stream.scale = (1, 1, 0.12); stream.rotation_euler = (0, 0, 0)
    elif t < TL["zero"]:
        # close-up pour on the island: glass on counter, bottle squeezing above it
        glass.location = GLASS_SPOT; glass.rotation_euler = (0, 0, 0)
        free_arm("L", CH.location + Vector((-0.26, -0.3, 1.0)), g=0.4)
        squeeze = t < TL["ice"] - 0.1
        bpos = GLASS_SPOT + Vector((0.025, 0.0, 0.29 if squeeze else 0.35)); brot = (0, -2.75 if squeeze else -0.4, 0)
        if t > TL["ice"] - 0.1:
            u = ease((t - TL["ice"] + 0.1) / 0.5); bpos = vlerp(GLASS_SPOT + Vector((0.025, 0, 0.29)), CH.location + Vector((0.32, -0.3, 1.08)), u)
            brot = (0, lerp(-2.75, 0, u), 0)
        hold(bottle, "R", bpos, approach=(1, 0, 0), fdir=(0, -1, 0.3), obj_rot=brot)
        if squeeze:
            bottle_mesh.scale = (1 - 0.06 * abs(math.sin(t * 7)), 1, 1)
            top = bpos + Vector((0.0, 0, -0.08)); bot = GLASS_SPOT + Vector((0, 0, 0.09))
            stream.location = (top + bot) / 2; stream.scale = (1, 1, (top - bot).length); stream.rotation_euler = (0, 0, 0)
            for i, d in enumerate(drops):
                ph = (t * 2.2 + i / 6) % 1; d.location = GLASS_SPOT + Vector((0.012 * math.sin(i * 2.1 + t * 5), 0.012 * math.cos(i * 1.7), 0.09 - 0.07 * ph))
        else: bottle_mesh.scale = (1, 1, 1)
        smile, mopen, brow, look = 0.9, 0.35, 0.8, (0.2, -0.8)
        # ice + peach slice + straw drop in on "Eistee"
        for i, c in enumerate(ices):
            st = TL["ice"] + 0.15 + i * 0.18; u = clamp((t - st) / 0.35)
            if t < st: continue
            endz = TOP + 0.06 + 0.025 * i; z = lerp(TOP + 0.45, endz, u * u) + (0.012 * math.sin((t - st - 0.35) * 25) * math.exp(-(t - st - 0.35) * 6) if u >= 1 else 0)
            c.location = GLASS_SPOT + Vector((0.012 * (i - 1), 0.01 * (i % 2), 0)); c.location.z = z; c.rotation_euler = (i + t * (1 - u), i * 0.7, i * 1.3)
        st = TL["ice"] + 0.7; u = clamp((t - st) / 0.35)
        if t >= st:
            pslice.location = GLASS_SPOT + Vector((0.0, -0.022, lerp(0.5, 0.1, u * u))); pslice.rotation_euler = (0.3, 0.2, 0.4)
        st = TL["ice"] + 1.1; u = clamp((t - st) / 0.3)
        if t >= st:
            straw.location = GLASS_SPOT + Vector((0.015, 0.0, lerp(0.45, 0.02, ease(u)))); straw.rotation_euler = (0.0, 0.25, 0)
    else:
        # glass on the counter or in hand, with straw/ice/slice
        if TL["drink"] <= t < TL["sorten"]:
            # drinking through the straw, then holding the glass up proudly with sunglasses on it
            mw = mouth_world()
            if t < TL["shades"] - 0.2:
                gpos = mw + Vector((-0.01, -0.07, -0.21)); brow, squint, smile, mopen = 0.3, 1.0, 0.4, 0.05
            else:
                u = ease((t - TL["shades"] + 0.2) / 0.4)
                gpos = vlerp(mw + Vector((-0.01, -0.07, -0.21)), CH.location + Vector((-0.24, -0.34, 1.5)), u)
                smile, mopen, brow, squint, look = 1.0, 0.7, 0.9, 0.6, (-0.8, 0.2)
            hold(glass, "L", gpos, approach=(-1, 0, 0), fdir=(0.2, -1, 0.3))
            free_arm("R", CH.location + Vector((0.24, -0.34, 1.0)), g=0.5)
            bottle.location = CH.location + Vector((0.45, -0.68, TOP - 0.97 + 0.97 + BOTTLE_H / 2 - 0.0)) ; bottle.location.z = TOP + BOTTLE_H / 2; bottle.rotation_euler = (0, 0, -0.3)
            if t >= TL["shades"]:
                k = back((t - TL["shades"]) / 0.3)
                shades.location = glass.location + Vector((0, -0.05, 0.1)); shades.scale = (k, k, k); shades.rotation_euler = (0, 0.12, 0)
        else:
            glass.location = GLASS_SPOT + Vector((-0.25, 0.02, 0)); glass.rotation_euler = (0, 0, 0)
            if t < TL["drink"]:
                # 0 Zucker / 0 kcal: bottle held up next to face, other hand taps the label
                bpos = CH.location + Vector((0.24, -0.34, 1.6 + 0.02 * math.sin(t * 5)))
                hold(bottle, "R", bpos, approach=(1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, 0.0))
                free_arm("L", CH.location + Vector((-0.24, -0.34, 1.0)), g=0.4)
                smile, mopen, brow, look = 1.0, 0.4, 0.9, (0.7, 0.0)
            elif t < TL["cta"]:
                # "Keine Lust auf Pfirsich?" shrug with bottle, then present it
                u = ease((t - TL["sorten"]) / 0.4)
                bpos = CH.location + Vector((0.26, -0.34, 1.38 + 0.03 * math.sin(t * 3)))
                hold(bottle, "R", bpos, approach=(1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, 0.0))
                free_arm("L", CH.location + Vector((-0.36, -0.28, 1.38)), g=0.1)
                smile, mopen, brow, look = 0.7, 0.3, 1.0 if t < T[28] else 0.6, (0.0, 0.0)
                if t < T[28]: head.rotation_euler = (0.0, 0.15, 0.1)
            else:
                # CTA: bottle raised, point down-left
                bpos = CH.location + Vector((0.27, -0.34, 1.62 + 0.03 * math.sin(t * 6)))
                hold(bottle, "R", bpos, approach=(1, 0, 0), fdir=(0, -1, 0.3), obj_rot=(0, 0, 0.0))
                free_arm("L", CH.location + Vector((-0.42, -0.4, 1.08)), point=True)
                smile, mopen, brow, look = 1.0, 0.5, 0.8, (-0.5, -0.6)
        # glass contents follow the glass
        for i, c in enumerate(ices):
            c.location = glass.location + Vector((0.012 * (i - 1), 0.01 * (i % 2), 0.06 + 0.025 * i)); c.rotation_euler = (i, i * 0.7, i * 1.3)
        pslice.location = glass.location + Vector((0.0, -0.022, 0.1)); pslice.rotation_euler = (0.3, 0.2, 0.4)
        straw.location = glass.location + Vector((0.015, 0.0, 0.02)); straw.rotation_euler = (0.0, 0.25, 0)
        if TL["drink"] <= t < TL["shades"] - 0.2:
            straw.rotation_euler = (0.25, 0.0, 0)
    face(smile, mopen, brow, look, squint, t)
    if not hero_on:
        for o in [hero] + list(hero.children_recursive): o.hide_render = True
    # camera
    loc, tgt, foc, fst = shot(t)
    look_at(cam, loc, tgt); camd.dof.focus_distance = (Vector(foc) - Vector(loc)).length; camd.dof.aperture_fstop = fst

def shot(t):
    C = CH.location
    if t < TL["medium"]:   # hero orbit around the bottle on the stand
        a = -0.5 + 0.55 * t / TL["medium"]; c = hero.location + Vector((0, 0, 0.1))
        cam_p = c + Vector((0.34 * math.sin(a), -0.34 * math.cos(a), 0.03))
        return cam_p, c + Vector((0, 0, -0.01)), c + (cam_p - c).normalized() * 0.025, 5.6
    if t < TL["pour"]:
        return C + Vector((0.05, -1.5, 1.5)), C + Vector((0.0, 0, 1.38)), C + Vector((0, -0.3, 1.4)), 2.8
    if t < TL["zero"]:     # close on the glass on the island
        u = (t - TL["pour"]) / (TL["zero"] - TL["pour"])
        g = GLASS_SPOT + Vector((0, 0, 0.12))
        return g + Vector((0.1 - 0.12 * u, -0.48 + 0.06 * u, 0.12)), g + Vector((0, 0, 0.03)), g, 2.2
    if t < TL["drink"]:
        return C + Vector((0.1, -1.25, 1.6)), C + Vector((0.08, 0, 1.5)), C + Vector((0.1, -0.3, 1.6)), 2.4
    if t < TL["sorten"]:
        u = (t - TL["drink"]) / (TL["sorten"] - TL["drink"])
        return C + Vector((-0.12, -1.25 + 0.1 * u, 1.62)), C + Vector((-0.12, 0, 1.52)), C + Vector((-0.1, -0.3, 1.6)), 2.4
    if t < TL["cta"]:
        return C + Vector((0.05, -1.5, 1.52)), C + Vector((0.03, 0, 1.38)), C + Vector((0.1, -0.3, 1.45)), 2.8
    u = (t - TL["cta"]) / 2.2
    return C + Vector((0.0, -1.6 + 0.12 * u, 1.5)), C + Vector((0.0, 0, 1.35)), C + Vector((0, -0.3, 1.45)), 2.8

def look_at(obj, loc, target):
    obj.location = loc; d = Vector(target) - Vector(loc); obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def anchors():
    upd()
    def p(v):
        q = world_to_camera_view(sc, cam, v); return (q.x, 1 - q.y, q.z)
    return dict(bottle=p(bottle.matrix_world.translation), glass=p(glass.matrix_world.translation + Vector((0, 0, 0.07))),
                head=p(head.matrix_world @ Vector((0, 0, 0.14))))

# ------------------------------------------------------------------ render settings
r = sc.render; r.engine = "CYCLES"
sc.cycles.device = "CPU"; sc.cycles.samples = args.samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 16; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 4; sc.cycles.transmission_bounces = 16
sc.cycles.transparent_max_bounces = 8; sc.cycles.use_adaptive_sampling = True; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
r.resolution_x = int(args.res * 9 / 16); r.resolution_y = args.res; r.resolution_percentage = 100
r.use_persistent_data = True; r.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Punchy"
except Exception: pass
sc.view_settings.exposure = -0.35
os.makedirs(args.out, exist_ok=True)
if os.environ.get("NOLIQ"): liquid.hide_render = True
if os.environ.get("NOGLASS"): sc.objects["glass"].hide_render = True

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
        if not os.path.exists(r.filepath): bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True); json.dump(anc, open(anc_path, "w"))
