"""
build_flask.py — High-Fidelity Borosilicate Erlenmeyer Conical Flask (250ml)
NCERT Class 9 & 10 Science (Experimental Chemistry & Chemical Reactions).

Dual Collections:
  1. Conical_Flask_Full:
     - 250ml Pyrex Erlenmeyer conical flask with wide flat base (84mm), tapered conical body,
       cylindrical neck with reinforced beaded rim (34mm), 3D white enamel graduation markings
       (50, 100, 150, 200 ml), and 100ml golden-amber ferric chloride / dilute acid solution with concave meniscus.
     - Studio slate carrier plinth with bevel edge and rubber pads.
  2. Conical_Flask_Section:
     - Longitudinal mechanical cross-section displaying 1.5mm wall thickness, bottom heel fillet,
       and interior fluid meniscus wetting angle.
     - Dimension calipers for base diameter (84mm), neck diameter (34mm), and body height (140mm).
     - Forward-angled laboratory educational plaque:
       - "ERLENMEYER CONICAL FLASK (250 mL)"
       - "Conical Geometry: Prevents splashing during vigorous manual swirling"
       - "Optimal for Acid-Base Titrations & Gas Evolution Reactions"
       - "Borosilicate 3.3 Glass: High chemical and thermal durability"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'conical-flask'

# Calibrated Laboratory Palette
COLOR_GLASS        = (0.95, 0.98, 1.00)     # Pyrex borosilicate glass (IOR 1.52)
COLOR_LIQUID_AMBER = (0.96, 0.80, 0.22)     # Golden-amber acid / FeCl3 solution (IOR 1.333)
COLOR_ENAMEL_WHITE = (0.95, 0.95, 0.95)     # Ceramic enamel permanent graduation markings
COLOR_CUT_GLASS    = (0.45, 0.75, 0.90)     # Sliced section face of borosilicate glass
COLOR_PLINTH       = (0.07, 0.08, 0.10)     # Studio slate base pedestal
COLOR_BRASS_GOLD   = (0.90, 0.75, 0.22)     # Gold trim and plaque frame
COLOR_CYAN_DIM     = (0.20, 0.85, 1.00)     # Dimension highlight

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=10.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    v1 = Vector(p1)
    v2 = Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-6:
        return None
    mid = (v1 + v2) / 2.0
    rot = diff.to_track_quat('Z', 'Y').to_euler()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=mid,
        rotation=rot
    )
    cyl = bpy.context.active_object
    cyl.name = name
    if cyl.data.materials:
        cyl.data.materials[0] = mat
    else:
        cyl.data.materials.append(mat)
    link_strictly(cyl, collection)
    return cyl

# -----------------------------------------------------------------------------
# BUILD CONICAL FLASK FULL
# -----------------------------------------------------------------------------
def build_conical_flask_full(collection):
    glass_mat = kit.add_glass_material("flask-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    liquid_mat = kit.add_glass_material("flask-liquid", COLOR_LIQUID_AMBER, ior=1.333, roughness=0.008)
    enamel_mat = kit.add_material("flask-enamel", COLOR_ENAMEL_WHITE, metallic=0.0, roughness=0.35)
    plinth_mat = kit.add_material("flask-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Slate Pedestal
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.220, 0.200, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    r_base_outer = 0.042
    r_base_inner = 0.0405
    r_neck_outer = 0.017
    r_neck_inner = 0.0155
    r_rim_outer  = 0.0195
    h_body       = 0.095
    h_total      = 0.140

    flask_profile = [
        (0.000, 0.000),
        (r_base_outer - 0.006, 0.000),
        (r_base_outer - 0.001, 0.002),
        (r_base_outer, 0.008),
        (r_neck_outer, h_body),
        (r_neck_outer, h_total - 0.008),
        (r_rim_outer - 0.001, h_total - 0.002),
        (r_rim_outer, h_total),
        (r_rim_outer - 0.0015, h_total + 0.001),
        (r_neck_inner + 0.001, h_total - 0.002),
        (r_neck_inner, h_total - 0.008),
        (r_neck_inner, h_body),
        (r_base_inner, 0.008),
        (r_base_inner - 0.004, 0.0025),
        (0.000, 0.0025)
    ]

    flask_body = kit.lathe_object(f"{ASSET_ID}_Body", flask_profile, segments=64, material=glass_mat)
    link_strictly(flask_body, collection)

    # 2. Meniscus Liquid Fill (100ml level)
    liquid_h = 0.042
    r_liq_top = r_base_inner - (r_base_inner - r_neck_inner) * (liquid_h / h_body)

    liquid_profile = [
        (0.000, 0.003),
        (r_base_inner - 0.003, 0.003),
        (r_base_inner - 0.0003, 0.008),
        (r_liq_top - 0.0003, liquid_h - 0.001),
        (r_liq_top - 0.0015, liquid_h + 0.001),
        (0.000, liquid_h)
    ]
    liquid_body = kit.lathe_object(f"{ASSET_ID}_Liquid", liquid_profile, segments=64, material=liquid_mat)
    link_strictly(liquid_body, collection)

    # 3. Graduation Marks on Front Wall
    for i, ml in enumerate([50, 100, 150, 200]):
        z_mark = 0.024 + (i * 0.018)
        r_at_z = r_base_outer - (r_base_outer - r_neck_outer) * (z_mark / h_body)
        is_major = (ml % 100 == 0)
        arc_angle = 0.32 if is_major else 0.18

        bm_mark = bmesh.new()
        seg_mark = 12
        r1 = r_at_z + 0.0001
        r2 = r_at_z + 0.0004
        z_low = z_mark - 0.0004
        z_high = z_mark + 0.0004

        verts_in_low, verts_in_high = [], []
        verts_out_low, verts_out_high = [], []

        for s in range(seg_mark + 1):
            theta = -arc_angle / 2 + (arc_angle * s / seg_mark)
            st = math.sin(theta)
            ct = math.cos(theta)
            verts_in_low.append(bm_mark.verts.new((r1 * st, -r1 * ct, z_low)))
            verts_in_high.append(bm_mark.verts.new((r1 * st, -r1 * ct, z_high)))
            verts_out_low.append(bm_mark.verts.new((r2 * st, -r2 * ct, z_low)))
            verts_out_high.append(bm_mark.verts.new((r2 * st, -r2 * ct, z_high)))

        for s in range(seg_mark):
            bm_mark.faces.new([verts_out_low[s], verts_out_low[s + 1], verts_out_high[s + 1], verts_out_high[s]])
            bm_mark.faces.new([verts_in_low[s + 1], verts_in_low[s], verts_in_high[s], verts_in_high[s + 1]])
            bm_mark.faces.new([verts_in_high[s], verts_out_high[s], verts_out_high[s + 1], verts_in_high[s + 1]])
            bm_mark.faces.new([verts_in_low[s + 1], verts_out_low[s + 1], verts_out_low[s], verts_in_low[s]])

        bm_mark.faces.new([verts_in_low[0], verts_in_high[0], verts_out_high[0], verts_out_low[0]])
        bm_mark.faces.new([verts_in_low[-1], verts_out_low[-1], verts_out_high[-1], verts_in_high[-1]])
        bmesh.ops.recalc_face_normals(bm_mark, faces=bm_mark.faces)

        mesh_mark = bpy.data.meshes.new(f"{ASSET_ID}_Tick_{ml}")
        bm_mark.to_mesh(mesh_mark)
        bm_mark.free()
        mark_obj = bpy.data.objects.new(f"{ASSET_ID}_Tick_{ml}", mesh_mark)
        bpy.context.collection.objects.link(mark_obj)
        mark_obj.data.materials.append(enamel_mat)
        link_strictly(mark_obj, collection)

    print("Built Conical_Flask_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD CONICAL FLASK SECTION (Longitudinal Cutaway)
# -----------------------------------------------------------------------------
def build_conical_flask_section(collection):
    glass_mat = kit.add_glass_material("sec-f-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    liquid_mat = kit.add_glass_material("sec-f-liquid", COLOR_LIQUID_AMBER, ior=1.333, roughness=0.008)
    plinth_mat = kit.add_material("sec-f-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat = kit.add_machined_metal_material("sec-f-gold", COLOR_BRASS_GOLD, metallic=0.92, roughness=0.20)
    dim_mat = kit.add_material("sec-f-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)
    plaque_bg = kit.add_material("sec-f-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Base Pedestal
    plinth = kit.primitive_object("Sec_Plinth", "cube", plinth_mat, size=(0.240, 0.200, 0.012), location=(0.0, 0.0, -0.006))
    link_strictly(plinth, collection)

    r_base_outer = 0.042
    r_base_inner = 0.0405
    r_neck_outer = 0.017
    r_neck_inner = 0.0155
    r_rim_outer  = 0.0195
    h_body       = 0.095
    h_total      = 0.140

    flask_profile = [
        (0.000, 0.000),
        (r_base_outer - 0.006, 0.000),
        (r_base_outer - 0.001, 0.002),
        (r_base_outer, 0.008),
        (r_neck_outer, h_body),
        (r_neck_outer, h_total - 0.008),
        (r_rim_outer - 0.001, h_total - 0.002),
        (r_rim_outer, h_total),
        (r_rim_outer - 0.0015, h_total + 0.001),
        (r_neck_inner + 0.001, h_total - 0.002),
        (r_neck_inner, h_total - 0.008),
        (r_neck_inner, h_body),
        (r_base_inner, 0.008),
        (r_base_inner - 0.004, 0.0025),
        (0.000, 0.0025)
    ]

    bm_half = bmesh.new()
    segments = 36
    rings = []
    for r_pt, z_pt in flask_profile:
        ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm_half.verts.new((x, y, z_pt)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for s in range(segments):
            bm_half.faces.new([rings[i][s], rings[i+1][s], rings[i+1][s+1], rings[i][s+1]])

    bm_half.faces.new([rings[i][0] for i in range(len(rings))])
    bm_half.faces.new([rings[i][segments] for i in range(len(rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_half, faces=bm_half.faces)
    mesh_half = bpy.data.meshes.new("Sec_Flask_Mesh")
    bm_half.to_mesh(mesh_half)
    bm_half.free()

    obj_half = bpy.data.objects.new("Sec_Flask_Body", mesh_half)
    bpy.context.collection.objects.link(obj_half)
    obj_half.data.materials.append(glass_mat)
    link_strictly(obj_half, collection)

    # 2. Half Liquid Fill (180°)
    liquid_h = 0.042
    r_liq_top = r_base_inner - (r_base_inner - r_neck_inner) * (liquid_h / h_body)

    liquid_profile = [
        (0.000, 0.003),
        (r_base_inner - 0.003, 0.003),
        (r_base_inner - 0.0003, 0.008),
        (r_liq_top - 0.0003, liquid_h - 0.001),
        (r_liq_top - 0.0015, liquid_h + 0.001),
        (0.000, liquid_h)
    ]
    bm_liq = bmesh.new()
    liq_rings = []
    for r_pt, z_pt in liquid_profile:
        ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm_liq.verts.new((x, y, z_pt)))
        liq_rings.append(ring)

    for i in range(len(liq_rings) - 1):
        for s in range(segments):
            bm_liq.faces.new([liq_rings[i][s], liq_rings[i+1][s], liq_rings[i+1][s+1], liq_rings[i][s+1]])

    bm_liq.faces.new([liq_rings[i][0] for i in range(len(liq_rings))])
    bm_liq.faces.new([liq_rings[i][segments] for i in range(len(liq_rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_liq, faces=bm_liq.faces)
    mesh_liq = bpy.data.meshes.new("Sec_Liquid_Mesh")
    bm_liq.to_mesh(mesh_liq)
    bm_liq.free()

    obj_liq = bpy.data.objects.new("Sec_Liquid_Body", mesh_liq)
    bpy.context.collection.objects.link(obj_liq)
    obj_liq.data.materials.append(liquid_mat)
    link_strictly(obj_liq, collection)

    # 3. Dimension Calipers (Base diameter 84mm & Total height 140mm)
    create_cylinder_segment("Sec_Caliper_Base", (-r_base_outer, 0.0, 0.004), (r_base_outer, 0.0, 0.004), 0.0008, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_H", (r_base_outer + 0.010, 0.0, 0.0), (r_base_outer + 0.010, 0.0, h_total), 0.0008, dim_mat, collection)

    # 4. Forward Angled Laboratory Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.210, 0.006, 0.058),
        location=(0.0, -0.068, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.216, 0.004, 0.064),
        location=(0.0, -0.069, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.180, 0.002, 0.008),
        location=(0.0, -0.065, 0.043),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    bar_sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.160, 0.002, 0.006),
        location=(0.0, -0.067, 0.027),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_sub1, collection)

    bar_sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", create_emissive_mat("sec-f-fe-glow", COLOR_LIQUID_AMBER, strength=10.0),
        size=(0.170, 0.002, 0.005),
        location=(0.0, -0.069, 0.013),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_sub2, collection)

    for sx in [-0.075, 0.075]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Leg_{sx}", "cylinder", gold_mat,
            size=(0.004, 0.004, 0.030),
            location=(sx, -0.065, 0.012)
        )
        link_strictly(stanchion, collection)

    print("Built Conical_Flask_Section successfully.")

# -----------------------------------------------------------------------------
# CAMERA & LIGHTING
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 45.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_obj.location = Vector((-0.02, -0.34, 0.24))
    direction = Vector((0.0, 0.0, 0.065)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    def make_light(name, ltype, pos, power, size=0.25):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = power
        if ltype == 'AREA':
            ldata.size = size
            ldata.shape = 'RECTANGLE'
            ldata.size_y = size * 0.7
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = pos
        bpy.context.scene.collection.objects.link(lobj)
        return lobj

    make_light("Key_Left", "AREA", (-0.16, -0.24, 0.30), 5.5, 0.3)
    make_light("Key_Right", "AREA", (0.16, -0.22, 0.28), 5.0, 0.3)
    make_light("Fill_Center", "AREA", (0.0, -0.16, 0.20), 2.8, 0.35)
    make_light("Top_Rim", "AREA", (0.0, 0.16, 0.32), 4.5, 0.35)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Conical_Flask_Full")
    sec_col  = bpy.data.collections.new("Conical_Flask_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_conical_flask_full(full_col)
    build_conical_flask_section(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False
    kit.export_glb(out_dir / f"{ASSET_ID}.glb")

    viewer_dest = Path("/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets") / f"{ASSET_ID}.glb"
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f"{ASSET_ID}.glb", viewer_dest)
        print(f"Synced GLB to: {viewer_dest}")

    # Render Preview 1: Conical_Flask_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Conical_Flask_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
