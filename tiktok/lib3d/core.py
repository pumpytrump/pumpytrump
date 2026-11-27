"""Shared Blender toolkit for the coded 3D product videos (Cycles, CPU).
Usage in a scene:  import core as K; K.init(args); K.build_character(...); ...; K.run(frame_state, anchors)
"""
import bpy, bmesh, math, json, os, sys, random, argparse
from mathutils import Vector, Euler, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view

FPS = 24
sc = None

def parse_args(default_frames="0-393"):
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=default_frames); ap.add_argument("--res", type=int, default=1280)
    ap.add_argument("--samples", type=int, default=12); ap.add_argument("--out", default="")
    ap.add_argument("--test", default="")
    return ap.parse_args(sys.argv[1:])

def init():
    global sc
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    _materials()
    return sc

# ------------------------------------------------------------------ primitives
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

def set_col(m, c): m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*c, 1)
def set_emit(m, s, c=None):
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Emission Strength"].default_value = s
    if c: b.inputs["Emission Color"].default_value = (*c, 1)

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

def torus(name, R, r, loc, parent=None, m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=12)
    o = bpy.context.object; o.name = name; o.location = loc; o.rotation_euler = rot
    return link(o, parent, m)

def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o)
    o.location = loc; o.parent = parent; o.empty_display_size = 0.05
    return o

def plane(name, w, h, loc, rot, m, parent=None):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.object; o.name = name; o.data.transform(Matrix.Diagonal((w, h, 1.0, 1.0)))
    o.location = loc; o.rotation_euler = rot
    return link(o, parent, m, smooth=False)

def tex_mat(name, path, rough=0.3, coat=0.5, metal=0.0, alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); t.extension = "EXTEND"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if alpha: nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = coat; b.inputs["Metallic"].default_value = metal
    return m

def wood_mat(name, c0, c1, scale=2.5, dist=6, rough=0.35):
    m = mat(name, c1, rough=rough, coat=0.3); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = dist
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*c0, 1); cr.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    return m

def brick_mat(name, c1, c2, mortar, scale=18, msize=0.012, rough=0.15, coat=0.6):
    m = mat(name, c1, rough=rough, coat=coat); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = scale; br.inputs["Mortar Size"].default_value = msize
    br.inputs["Color1"].default_value = (*c1, 1); br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1); nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    return m

def checker_mat(name, c1, c2, scale=6, rough=0.2, coat=0.5):
    m = mat(name, c1, rough=rough, coat=coat); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    ch = nt.nodes.new("ShaderNodeTexChecker"); ch.inputs["Scale"].default_value = scale
    ch.inputs["Color1"].default_value = (*c1, 1); ch.inputs["Color2"].default_value = (*c2, 1)
    nt.links.new(ch.outputs["Color"], b.inputs["Base Color"])
    return m

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

def _materials():
    g = globals()
    g.update(SKIN=mat("skin", (0.78, 0.55, 0.42), rough=0.45, sss=0.25), LIP=mat("lip", (0.55, 0.25, 0.22), rough=0.4, sss=0.2),
             MOUTH=mat("mouth", (0.18, 0.04, 0.04), rough=0.6), TEETH=mat("teeth", (0.95, 0.93, 0.88), rough=0.3),
             HAIR=mat("hair", (0.09, 0.055, 0.035), rough=0.55, sheen=0.3), BROW=mat("brow", (0.08, 0.05, 0.03), rough=0.7),
             EYEW=mat("eyew", (0.95, 0.95, 0.95), rough=0.15, coat=1.0), IRIS=mat("iris", (0.22, 0.12, 0.05), rough=0.1, coat=1.0),
             PUPIL=mat("pupil", (0.01, 0.01, 0.01), rough=0.05, coat=1.0), STUB=mat("stubble", (0.42, 0.3, 0.24), rough=0.8),
             TEE=mat("tee", (0.93, 0.92, 0.88), rough=0.85, sheen=0.2), SHIRT=mat("shirt", (0.52, 0.62, 0.48), rough=0.8, sheen=0.2),
             SHIRT2=mat("shirt2", (0.42, 0.52, 0.38), rough=0.8), BRASS=mat("brass", (0.9, 0.7, 0.35), rough=0.25, metal=1.0),
             CHROME=mat("chrome", (0.9, 0.9, 0.92), rough=0.12, metal=1.0), BLACK=mat("black", (0.02, 0.02, 0.025), rough=0.35, coat=0.5),
             WHITE=mat("white", (0.92, 0.92, 0.9), rough=0.4), GREEN=mat("leaf", (0.12, 0.38, 0.12), rough=0.5, sss=0.1),
             POT=mat("pot", (0.85, 0.5, 0.35), rough=0.7), GLASS=thin_glass("glass"),
             ICE=mat("ice", (0.92, 0.97, 1.0), rough=0.12, trans=1.0, ior=1.31), SHADES=mat("shades", (0.02, 0.02, 0.03), rough=0.05, coat=1.0))

# ------------------------------------------------------------------ product meshes from photo cut-outs
def revolve(name, path, height, r_from=0, r_to=None, depth=0.95, m=None, step=4, N=48):
    """Body of revolution from the alpha silhouette of a front photo; UVs = front projection (label shows on front)."""
    from PIL import Image
    im = Image.open(path).convert("RGBA"); Wp, Hp = im.size; px = im.load()
    if r_to is None: r_to = Hp
    s = height / Hp; cx = Wp / 2
    rows = []
    for r in list(range(r_from, r_to, step)) + [r_to - 1]:
        xs = [x for x in range(Wp) if px[x, r][3] > 140]
        if len(xs) < 2: continue
        rows.append((r, xs[0], xs[-1]))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); rings = []
    for r, l, rr in rows:
        rad = (rr - l) / 2; c = (rr + l) / 2; ring = []
        for k in range(N):
            a = 2 * math.pi * k / N
            ring.append(bm.verts.new(((c - cx + rad * math.cos(a)) * s, -rad * math.sin(a) * s * depth, (Hp - r) * s)))
        rings.append(ring)
    def uv(f, vz=None):
        for lp in f.loops: lp[uvl].uv = ((lp.vert.co.x / s + cx) / Wp, (lp.vert.co.z if vz is None else vz) / s / Hp)
    for a0, a1 in zip(rings, rings[1:]):
        for k in range(N): uv(bm.faces.new((a0[k], a0[(k + 1) % N], a1[(k + 1) % N], a1[k])))
    i1 = min(3, len(rings) - 1)
    uv(bm.faces.new(rings[0]), rings[i1][0].co.z); uv(bm.faces.new(list(reversed(rings[-1]))), rings[-1 - i1][0].co.z)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    me.materials.append(m or tex_mat(name + "_lbl", path))
    for p in me.polygons: p.use_smooth = True
    md = o.modifiers.new("sub", "SUBSURF"); md.levels = 1; md.render_levels = 1
    zmin = (Hp - r_to) * s
    for v in me.vertices: v.co.z -= zmin           # origin at the bottom of the part
    return o

def extrude(name, path, height, thick, side_col=(0.05, 0.05, 0.06), r_from=0, r_to=None, step=3, round_k=0.35):
    """Flat-ish product (clipper, square bottle): silhouette extruded with rounded sides; photo on front + mirrored on back."""
    from PIL import Image
    im = Image.open(path).convert("RGBA"); Wp, Hp = im.size; px = im.load()
    if r_to is None: r_to = Hp
    s = height / Hp; cx = Wp / 2
    rows = []
    for r in list(range(r_from, r_to, step)) + [r_to - 1]:
        xs = [x for x in range(Wp) if px[x, r][3] > 140]
        if len(xs) < 2: continue
        rows.append((r, xs[0], xs[-1]))
    # cross-section: rounded rectangle (superellipse) between l..r with depth thick
    K = 20
    prof = []
    for k in range(K):
        a = 2 * math.pi * k / K; ca, sa = math.cos(a), math.sin(a)
        e = 2.0 / (2 + 6 * (1 - round_k))
        prof.append((math.copysign(abs(ca) ** e, ca), math.copysign(abs(sa) ** e, sa)))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); rings = []
    for r, l, rr in rows:
        hw = (rr - l) / 2; c = (rr + l) / 2
        rings.append([bm.verts.new(((c - cx + hw * px_) * s, -py * thick / 2, (Hp - r) * s)) for px_, py in prof])
    def uv(f):
        for lp in f.loops:
            x = (lp.vert.co.x / s + cx) / Wp
            if lp.vert.co.y > 0: x = 1 - x                 # back face: mirrored copy of front photo
            lp[uvl].uv = (x, lp.vert.co.z / s / Hp)
    for a0, a1 in zip(rings, rings[1:]):
        for k in range(K): uv(bm.faces.new((a0[k], a0[(k + 1) % K], a1[(k + 1) % K], a1[k])))
    uv(bm.faces.new(rings[0])); uv(bm.faces.new(list(reversed(rings[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    me.materials.append(tex_mat(name + "_lbl", path, rough=0.35, coat=0.6))
    for p in me.polygons: p.use_smooth = True
    md = o.modifiers.new("sub", "SUBSURF"); md.levels = 1; md.render_levels = 1
    zmin = (Hp - r_to) * s
    for v in me.vertices: v.co.z -= zmin
    return o

# ------------------------------------------------------------------ character
def side_x(side): return -1 if side == "L" else 1
UA, FA = 0.29, 0.25

def build_character(loc=(0, 1.38, 0), female=False, hair="short", beard="stubble", tee=(0.93, 0.92, 0.88), shirt=(0.52, 0.62, 0.48),
                    shirt2=None, skin=(0.78, 0.55, 0.42), hair_col=(0.09, 0.055, 0.035), iris=(0.22, 0.12, 0.05), apron=None, open_shirt=True):
    g = globals()
    set_col(SKIN, skin); set_col(HAIR, hair_col); set_col(TEE, tee); set_col(SHIRT, shirt); set_col(IRIS, iris)
    set_col(SHIRT2, shirt2 or tuple(c * 0.82 for c in shirt)); set_col(BROW, tuple(c * 0.9 for c in hair_col))
    if female: set_col(LIP, (0.68, 0.22, 0.26))
    CH = empty("char", loc)
    hips = empty("hips", (0, 0, 0.97), CH)
    box("pelvis", (0.36, 0.22, 0.2), (0, 0, 0.0), parent=hips, m=SHIRT2, bevel=0.07, sub=1)
    spine = empty("spine", (0, 0, 0.06), hips)
    tw = 0.38 if female else 0.42
    box("torso", (tw, 0.24, 0.55), (0, 0, 0.27), parent=spine, m=TEE, bevel=0.11, sub=2)
    if open_shirt:
        for x in (-1, 1):
            box("panel", (0.1, 0.022, 0.52), (x * (tw / 2 - 0.045), -0.115, 0.27), parent=spine, m=SHIRT, bevel=0.02, sub=1, rot=(0, 0, x * 0.18))
            box("collar", (0.09, 0.03, 0.08), (x * 0.075, -0.1, 0.53), parent=spine, m=SHIRT, bevel=0.02, rot=(0.3, 0, x * 0.5))
    if apron:
        AP = mat("apron", apron, rough=0.85, sheen=0.3)
        box("apron", (0.34, 0.02, 0.46), (0, -0.125, 0.16), parent=spine, m=AP, bevel=0.01, sub=1)
        for x in (-1, 1): box("strap", (0.025, 0.02, 0.2), (x * 0.1, -0.12, 0.47), parent=spine, m=AP, rot=(0, x * -0.25, 0))
    neck = empty("neck", (0, 0, 0.535), spine)
    cyl("neckm", 0.05 if female else 0.054, 0.12, (0, 0, 0.03), parent=neck, m=SKIN)
    head = empty("head", (0, 0, 0.06), neck)
    sphere("skull", 0.124, (0, 0, 0.135), (0.93, 1.0, 1.16), parent=head, m=SKIN, sub=1)
    sphere("jaw", 0.1, (0, -0.02, 0.07), (0.88, 0.92, 0.72) if female else (0.95, 0.95, 0.75), parent=head, m=SKIN, sub=1)
    hair_objs, beard_objs = [], []
    if beard in ("stubble", "full") and not female:
        beard_objs.append(sphere("stub", 0.101, (0, -0.022, 0.066), (0.95, 0.95, 0.72), parent=head, m=STUB, sub=1))
    if beard == "full" and not female:
        BEARD = mat("beard", hair_col, rough=0.7, sheen=0.4); g["BEARD"] = BEARD
        beard_objs.append(sphere("beard", 0.108, (0, -0.03, 0.045), (1.0, 1.0, 0.95), parent=head, m=BEARD, sub=1))
        beard_objs.append(sphere("beard2", 0.07, (0, -0.075, 0.0), (1.1, 0.9, 1.0), parent=head, m=BEARD, sub=1))
        beard_objs.append(box("mous", (0.075, 0.03, 0.022), (0, -0.118, 0.078), parent=head, m=BEARD, bevel=0.01, sub=1))
    hair_objs.append(sphere("hairtop", 0.134, (0, 0.02, 0.2), (0.98, 1.04, 0.86), parent=head, m=HAIR, sub=1))
    if hair == "messy":
        rng = random.Random(5)
        for i in range(26):
            a = rng.uniform(0, 2 * math.pi); el = rng.uniform(0.15, 1.3)
            p = Vector((0.125 * math.cos(a) * math.cos(el), 0.02 + 0.13 * math.sin(a) * math.cos(el), 0.2 + 0.1 * math.sin(el)))
            hair_objs.append(sphere("tuft", rng.uniform(0.035, 0.055), p, (1, 1, 1.5), parent=head, m=HAIR, sub=1, seg=16,
                                    rot=(rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 0)))
    elif female or hair == "long":
        hair_objs.append(box("fringe", (0.2, 0.05, 0.05), (0.03, -0.09, 0.255), parent=head, m=HAIR, bevel=0.022, rot=(0.7, 0.25, -0.25), sub=1))
    else:
        hair_objs.append(box("fringe", (0.19, 0.06, 0.05), (0.01, -0.085, 0.262), parent=head, m=HAIR, bevel=0.022, rot=(0.5, 0, 0.08), sub=1))
    if female or hair == "long":
        hair_objs.append(box("hairback", (0.27, 0.1, 0.38), (0, 0.06, 0.04), parent=head, m=HAIR, bevel=0.05, sub=2))
        for x in (-1, 1):
            hair_objs.append(box("lock", (0.05, 0.08, 0.3), (x * 0.122, -0.01, 0.06), parent=head, m=HAIR, bevel=0.022, sub=2, rot=(0, x * -0.06, 0)))
    for x in (-1, 1):
        sphere("ear", 0.034, (x * 0.118, 0.0, 0.125), (0.35, 0.7, 1.0), parent=head, m=SKIN)
        if not female: hair_objs.append(sphere("sideburn", 0.03, (x * 0.112, -0.01, 0.17), (0.4, 0.9, 1.4), parent=head, m=HAIR))
    eyes = []
    for x in (-1, 1):
        e = empty("eye", (x * 0.041, -0.1, 0.138), head)
        sphere("eyew", 0.024, (0, 0, 0), parent=e, m=EYEW)
        ir = empty("iris", (0, 0, 0), e)
        sphere("irism", 0.0145, (0, -0.017, 0), (1, 0.5, 1), parent=ir, m=IRIS)
        sphere("pup", 0.0068, (0, -0.0235, 0), (1, 0.4, 1), parent=ir, m=PUPIL)
        lid = sphere("lid", 0.0255, (0, 0, 0.004), (1.02, 1.02, 0.01), parent=e, m=SKIN)
        if female: box("lash", (0.05, 0.012, 0.004), (0, -0.016, 0.022), parent=e, m=BLACK, rot=(0.3, 0, 0))
        eyes.append((e, ir, lid))
    bw = (0.045, 0.008, 0.008) if female else (0.05, 0.012, 0.011)
    brows = [box("brow", bw, (x * 0.043, -0.112, 0.176), parent=head, m=BROW, bevel=0.003) for x in (-1, 1)]
    sphere("nose", 0.02, (0, -0.128, 0.108), (0.7, 1.1, 1.2) if female else (0.8, 1.2, 1.3), parent=head, m=SKIN, sub=1)
    mouth = empty("mouth", (0, -0.112, 0.058), head)
    MOPEN = sphere("mopen", 0.026, (0, 0, 0), (1.3, 0.35, 0.3), parent=mouth, m=MOUTH)
    teeth = box("teeth", (0.04, 0.008, 0.008), (0, -0.004, 0.006), parent=mouth, m=TEETH, bevel=0.003)
    lipu = cyl("lip", 0.0062 if female else 0.0052, 0.062, (0, -0.002, 0.0), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
    sd = lipu.modifiers.new("bend", "SIMPLE_DEFORM"); sd.deform_method = "BEND"; sd.deform_axis = "Y"; sd.angle = 0.6
    lipd = cyl("lipd", 0.0058 if female else 0.0048, 0.05, (0, -0.002, -0.01), parent=mouth, m=LIP, rot=(0, math.pi / 2, 0))
    sd2 = lipd.modifiers.new("bend", "SIMPLE_DEFORM"); sd2.deform_method = "BEND"; sd2.deform_axis = "Y"; sd2.angle = 0.6
    def arm(side):
        s = empty("sh" + side, (side_x(side) * (tw / 2 + 0.015), 0, 0.47), spine); s.rotation_mode = "QUATERNION"
        sphere("shm", 0.062, (0, 0, 0), parent=s, m=SHIRT, sub=1)
        cyl("uarm", 0.054, UA, (0, 0, -UA / 2), parent=s, m=SHIRT, sub=1)
        el = empty("el" + side, (0, 0, -UA), s); el.rotation_mode = "QUATERNION"
        sphere("elm", 0.05, (0, 0, 0), parent=el, m=SHIRT)
        cyl("farm", 0.045, 0.16, (0, 0, -0.08), parent=el, m=SHIRT, sub=1)
        cyl("cuff", 0.05, 0.03, (0, 0, -0.15), parent=el, m=SHIRT2)
        cyl("forearm", 0.035 if female else 0.037, 0.11, (0, 0, -0.2), parent=el, m=SKIN, sub=1)
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
    L = arm("L"); R = arm("R")
    g.update(CH=CH, hips=hips, spine=spine, neck=neck, head=head, eyes=eyes, brows=brows, mouth=mouth, MOPEN=MOPEN, teeth=teeth,
             lipu=lipu, lipd=lipd, hair_objs=hair_objs, beard_objs=beard_objs, ARM=dict(L=L, R=R))
    return CH

# ------------------------------------------------------------------ lights / camera
def world(col=(0.95, 0.92, 0.88), strength=0.3):
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*col, 1); w.node_tree.nodes["Background"].inputs[1].default_value = strength
    return w

def area(name, loc, rot, energy, size, col=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = col
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o

def point(name, loc, energy, col=(1, 1, 1), r=0.05):
    d = bpy.data.lights.new(name, "POINT"); d.energy = energy; d.color = col; d.shadow_soft_size = r
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; return o

def camera(lens=32):
    global cam, camd
    camd = bpy.data.cameras.new("cam"); camd.lens = lens; camd.sensor_fit = "VERTICAL"; camd.sensor_height = 36
    camd.dof.use_dof = True
    cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam
    return cam

def look_at(obj, loc, target):
    obj.location = loc; d = Vector(target) - Vector(loc); obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def set_shot(loc, tgt, foc, fst):
    look_at(cam, loc, tgt); camd.dof.focus_distance = (Vector(foc) - Vector(loc)).length; camd.dof.aperture_fstop = fst

# ------------------------------------------------------------------ animation helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def vlerp(a, b, t): return Vector(a).lerp(Vector(b), t)
def upd(): bpy.context.view_layer.update()
def win(t, a, b): return a <= t < b

def ik_arm(sh, el, wr, target, pole, hand_rot=None):
    upd()
    S = sh.matrix_world.translation.copy(); Tg = Vector(target)
    d = Tg - S; dist = min(max(d.length, 0.05), UA + FA - 0.002); dn = d.normalized()
    a = (UA * UA + dist * dist - FA * FA) / (2 * dist); h = math.sqrt(max(UA * UA - a * a, 0))
    pv = Vector(pole) - S; pv = (pv - dn * pv.dot(dn)); pv = pv.normalized() if pv.length > 1e-6 else Vector((0, 0, -1))
    E = S + dn * a + pv * h; Tg = S + dn * dist
    prot = sh.parent.matrix_world.to_quaternion()
    sh.rotation_quaternion = (prot.inverted() @ (E - S)).to_track_quat("-Z", "Y"); upd()
    el.rotation_quaternion = (sh.matrix_world.to_quaternion().inverted() @ (Tg - E)).to_track_quat("-Z", "Y"); upd()
    wr.rotation_quaternion = (el.matrix_world.to_quaternion().inverted() @ hand_rot.to_quaternion()) if hand_rot is not None else Quaternion()
    upd()

def hand_frame(fdir, palm_to_obj, side):
    z = -Vector(fdir).normalized()
    n = Vector(palm_to_obj); n = (n - (-z) * n.dot(-z)).normalized()
    x = (-n) if side == "R" else n
    y = z.cross(x).normalized(); x = y.cross(z).normalized()
    return Matrix((x, y, z)).transposed()

def grip(fingers, thumb, amount, side):
    for f, f2 in fingers:
        f.rotation_euler = (0, side_x(side) * -1.2 * amount, 0); f2.rotation_euler = (0, side_x(side) * -1.1 * amount, 0)
    thumb.rotation_euler = (0.6 * amount, side_x(side) * -0.6 * amount, 0)

def hold(obj, side, center, fdir=(0, -1, 0.25), approach=None, obj_rot=(0, 0, 0), pole=None, g=1.0, palm_off=0.045):
    """Place obj at `center` and make hand `side` grip it from the `approach` direction (palm -> object = -approach)."""
    center = Vector(center)
    if approach is None: approach = Vector((side_x(side), 0.0, 0.0))
    n = -Vector(approach).normalized()
    R = hand_frame(fdir, n, side)
    fd = -(R @ Vector((0, 0, 1)))
    wrist = center - n * palm_off - fd * 0.055
    sh, el, wr, th, fing = ARM[side]
    if pole is None: pole = sh.matrix_world.translation + Vector((side_x(side) * 0.4, 0.25, -0.5))
    ik_arm(sh, el, wr, wrist, pole, R)
    grip(fing, th, g, side)
    if obj is not None: obj.location = center; obj.rotation_euler = obj_rot

def free_arm(side, target, pole_off=(0.4, 0.25, -0.5), fdir=None, point=False, g=0.3, palm=None):
    sh, el, wr, th, fing = ARM[side]
    upd()
    pole = sh.matrix_world.translation + Vector((side_x(side) * pole_off[0], pole_off[1], pole_off[2]))
    R = None
    if fdir is not None: R = hand_frame(fdir, Vector(palm) if palm else Vector((-side_x(side), 0, 0)), side)
    ik_arm(sh, el, wr, target, pole, R)
    if point:
        for i, (f, f2) in enumerate(fing):
            a = 0.0 if i == 0 else 1.0
            f.rotation_euler = (0, side_x(side) * -1.5 * a, 0); f2.rotation_euler = (0, side_x(side) * -1.4 * a, 0)
        th.rotation_euler = (0.5, side_x(side) * -0.5, 0)
    else: grip(fing, th, g, side)

def thumbs_up(side, target):
    free_arm(side, target, fdir=(0, -0.3, 1), g=1.0)
    sh, el, wr, th, fing = ARM[side]
    th.rotation_euler = (-0.6, side_x(side) * 0.3, 0)

def face(smile=0.6, mopen=0.0, brow=0.0, look=(0, 0), squint=0.0, t=0.0, blink=True):
    lipu.modifiers["bend"].angle = lerp(-0.5, 1.1, smile); lipd.modifiers["bend"].angle = lerp(-0.4, 0.9, smile)
    MOPEN.scale = (1.3, 0.35, 0.12 + 0.75 * mopen); lipd.location.z = -0.008 - 0.018 * mopen
    teeth.scale = (1, 1, 1 if mopen > 0.3 else 0.01)
    for i, b in enumerate(brows):
        b.location.z = 0.176 + 0.012 * brow; b.rotation_euler = (0, (1 if i else -1) * -0.12 * brow, 0)
    bl = 1.0 if (blink and (t % 3.3) < 0.09) else 0.0; lidk = max(bl, 0.55 * squint) if squint <= 1.0 else min(1.0, 0.55 + 0.45 * (squint - 1.0) * 2)
    for e, ir, lid in eyes:
        ir.location = (0.006 * look[0], 0, 0.004 * look[1]); lid.scale = (1.02, 1.02, max(0.01, min(lidk, 1.0)))

def talk(t, words, amp=0.55):
    """mouth open amount from word timings"""
    for w, s, e in words:
        if s <= t < e: return amp * (0.45 + 0.55 * abs(math.sin((t - s) * 21)))
    return 0.0

def idle(t):
    hips.location = (0, 0, 0.97 + 0.006 * math.sin(t * 2.4))
    spine.rotation_euler = (0.04 * math.sin(t * 0.8), 0.02 * math.sin(t * 1.1), 0)
    head.rotation_euler = (0.03 * math.sin(t * 2.1), 0, 0.05 * math.sin(t * 0.9))

def world_of(o, off=(0, 0, 0)):
    upd(); return o.matrix_world @ Vector(off)

# ------------------------------------------------------------------ render
def setup_render(args, exposure=-0.35):
    r = sc.render; r.engine = "CYCLES"
    sc.cycles.device = "CPU"; sc.cycles.samples = args.samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 12; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 4; sc.cycles.transmission_bounces = 12
    sc.cycles.transparent_max_bounces = 8; sc.cycles.use_adaptive_sampling = True
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
    r.resolution_x = int(args.res * 9 / 16); r.resolution_y = args.res; r.resolution_percentage = 100
    r.use_persistent_data = True; r.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"
    try: sc.view_settings.look = "AgX - Punchy"
    except Exception: pass
    sc.view_settings.exposure = exposure

def run(args, here, frame_state, anchor_objs):
    out = args.out or os.path.join(here, "out", "frames"); os.makedirs(out, exist_ok=True)
    r = sc.render
    def anchors():
        upd(); res = {}
        for k, v in anchor_objs().items():
            q = world_to_camera_view(sc, cam, v); res[k] = (q.x, 1 - q.y, q.z)
        return res
    if args.test:
        for ts in [float(x) for x in args.test.split(",")]:
            frame_state(ts); r.filepath = os.path.join(out, f"test_{ts:05.2f}.png")
            bpy.ops.render.render(write_still=True); print("rendered", ts, flush=True)
        return
    a, b = [int(x) for x in args.frames.split("-")]
    anc_path = os.path.join(out, f"anchors_{a:04d}_{b:04d}.json"); anc = {}
    for f in range(a, b + 1):
        frame_state(f / FPS); anc[f] = anchors()
        r.filepath = os.path.join(out, f"{f:04d}.png")
        if not os.path.exists(r.filepath): bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True); json.dump(anc, open(anc_path, "w"))
