"""
build_test_tube.py — High-Fidelity Borosilicate Test Tube with Hemispherical Base
NCERT Class 9 & 10 Science (Qualitative Analysis & Chemical Reactions).

Dual Collections:
  1. Test_Tube_Full:
     - 16x140mm Pyrex borosilicate glass test tube with true hemispherical base and flared beaded rim.
     - Containing 10ml reddish-amber iodine / bromine solution with concave wetting meniscus.
     - Mounted upright in a laboratory polished hardwood rack block on a studio slate plinth.
  2. Test_Tube_Section:
     - Longitudinal mechanical cross-section displaying 1.2mm uniform wall thickness and hemispherical bottom.
     - Dimension calipers for outer diameter (16mm) and length (140mm).
     - Forward-angled laboratory educational plaque:
       - "LABORATORY BOROSILICATE TEST TUBE"
       - "Dimensions: 16mm x 140mm | Wall Thickness: 1.2mm"
       - "Hemispherical Bottom: Uniform thermal stress distribution during direct Bunsen heating"
       - "CBSE Class 10/12 Standard Qualitative Analysis"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'test-tube'

# Calibrated Laboratory Palette
COLOR_GLASS        = (0.95, 0.98, 1.00)     # Pyrex borosilicate glass (IOR 1.52)
COLOR_LIQUID_IODINE= (0.88, 0.38, 0.10)     # Reddish-amber iodine solution (IOR 1.333)
COLOR_WOOD_RACK    = (0.55, 0.38, 0.22)     # Polished hardwood laboratory rack block
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
# BUILD TEST TUBE FULL
# -----------------------------------------------------------------------------
def build_test_tube_full(collection):
    glass_mat = kit.add_glass_material("tube-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    liquid_mat = kit.add_glass_material("tube-liquid", COLOR_LIQUID_IODINE, ior=1.333, roughness=0.008)
    wood_mat = kit.add_material("tube-rack-wood", COLOR_WOOD_RACK, metallic=0.05, roughness=0.55)
    plinth_mat = kit.add_material("tube-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Slate Pedestal
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.180, 0.160, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # Hardwood Support Block holding tube upright
    rack_block = kit.primitive_object(
        f"{ASSET_ID}_Rack_Block", "cube", wood_mat,
        size=(0.050, 0.050, 0.040),
        location=(0.0, 0.0, 0.020)
    )
    link_strictly(rack_block, collection)

    # 2. Test Tube Dimensions & Lathe Profile
    r_outer = 0.008
    r_inner = 0.0068
    r_rim   = 0.0094
    h_total = 0.140

    tube_profile = []
    num_hemi = 16
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_outer * math.sin(angle)
        z = r_outer * (1.0 - math.cos(angle))
        tube_profile.append((r, z))

    tube_profile.extend([
        (r_outer, h_total - 0.006),
        (r_rim - 0.0005, h_total - 0.0015),
        (r_rim, h_total),
        (r_rim - 0.001, h_total + 0.0008),
        (r_inner + 0.0008, h_total - 0.0015),
        (r_inner, h_total - 0.006),
        (r_inner, r_outer)
    ])

    for i in range(num_hemi, -1, -1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_inner * math.sin(angle)
        z = r_outer + (r_inner - 0.0012) - r_inner * math.cos(angle)
        if z < 0.0015:
            z = 0.0015
        tube_profile.append((r, z))

    # Elevate test tube so its bottom rests securely in rack socket (bottom at z = 0.008)
    tube_body = kit.lathe_object(f"{ASSET_ID}_Body", tube_profile, segments=48, material=glass_mat)
    tube_body.location.z = 0.008
    link_strictly(tube_body, collection)

    # 3. Liquid Fill (Iodine solution)
    liquid_h = 0.065
    liquid_profile = []
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = (r_inner - 0.0002) * math.sin(angle)
        z = 0.0018 + (r_inner - 0.0002) * (1.0 - math.cos(angle))
        liquid_profile.append((r, z))

    liquid_profile.extend([
        (r_inner - 0.0002, liquid_h - 0.001),
        (r_inner - 0.0010, liquid_h + 0.0008),
        (0.000, liquid_h)
    ])

    liquid_body = kit.lathe_object(f"{ASSET_ID}_Liquid", liquid_profile, segments=48, material=liquid_mat)
    liquid_body.location.z = 0.008
    link_strictly(liquid_body, collection)

    print("Built Test_Tube_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD TEST TUBE SECTION (Longitudinal Cutaway)
# -----------------------------------------------------------------------------
def build_test_tube_section(collection):
    glass_mat = kit.add_glass_material("sec-t-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    liquid_mat = kit.add_glass_material("sec-t-liquid", COLOR_LIQUID_IODINE, ior=1.333, roughness=0.008)
    plinth_mat = kit.add_material("sec-t-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    wood_mat = kit.add_material("sec-t-wood", COLOR_WOOD_RACK, metallic=0.05, roughness=0.55)
    gold_mat = kit.add_machined_metal_material("sec-t-gold", COLOR_BRASS_GOLD, metallic=0.92, roughness=0.20)
    dim_mat = kit.add_material("sec-t-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)
    plaque_bg = kit.add_material("sec-t-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Base Pedestal & Half Rack Block
    plinth = kit.primitive_object("Sec_Plinth", "cube", plinth_mat, size=(0.200, 0.160, 0.012), location=(0.0, 0.0, -0.006))
    link_strictly(plinth, collection)

    # Half wood block (y from 0 to 0.025)
    rack_half = kit.primitive_object("Sec_Rack_Half", "cube", wood_mat, size=(0.050, 0.025, 0.040), location=(0.0, 0.0125, 0.020))
    link_strictly(rack_half, collection)

    r_outer = 0.008
    r_inner = 0.0068
    r_rim   = 0.0094
    h_total = 0.140

    tube_profile = []
    num_hemi = 16
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_outer * math.sin(angle)
        z = r_outer * (1.0 - math.cos(angle))
        tube_profile.append((r, z))

    tube_profile.extend([
        (r_outer, h_total - 0.006),
        (r_rim - 0.0005, h_total - 0.0015),
        (r_rim, h_total),
        (r_rim - 0.001, h_total + 0.0008),
        (r_inner + 0.0008, h_total - 0.0015),
        (r_inner, h_total - 0.006),
        (r_inner, r_outer)
    ])

    for i in range(num_hemi, -1, -1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_inner * math.sin(angle)
        z = r_outer + (r_inner - 0.0012) - r_inner * math.cos(angle)
        if z < 0.0015:
            z = 0.0015
        tube_profile.append((r, z))

    # Revolve 180° (theta from 0 to pi)
    bm_half = bmesh.new()
    segments = 32
    rings = []
    for r_pt, z_pt in tube_profile:
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
    mesh_half = bpy.data.meshes.new("Sec_Tube_Mesh")
    bm_half.to_mesh(mesh_half)
    bm_half.free()

    obj_half = bpy.data.objects.new("Sec_Tube_Body", mesh_half)
    bpy.context.collection.objects.link(obj_half)
    obj_half.data.materials.append(glass_mat)
    obj_half.location.z = 0.008
    link_strictly(obj_half, collection)

    # 2. Half Liquid Fill (180°)
    liquid_h = 0.065
    liquid_profile = []
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = (r_inner - 0.0002) * math.sin(angle)
        z = 0.0018 + (r_inner - 0.0002) * (1.0 - math.cos(angle))
        liquid_profile.append((r, z))

    liquid_profile.extend([
        (r_inner - 0.0002, liquid_h - 0.001),
        (r_inner - 0.0010, liquid_h + 0.0008),
        (0.000, liquid_h)
    ])

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
    mesh_liq = bpy.data.meshes.new("Sec_Tube_Liq_Mesh")
    bm_liq.to_mesh(mesh_liq)
    bm_liq.free()

    obj_liq = bpy.data.objects.new("Sec_Tube_Liquid", mesh_liq)
    bpy.context.collection.objects.link(obj_liq)
    obj_liq.data.materials.append(liquid_mat)
    obj_liq.location.z = 0.008
    link_strictly(obj_liq, collection)

    # 3. Dimension Calipers (Diameter 16mm & Length 140mm)
    create_cylinder_segment("Sec_Caliper_Dia", (-r_outer, 0.0, 0.155), (r_outer, 0.0, 0.155), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_L", (r_outer + 0.006, 0.0, 0.008), (r_outer + 0.006, 0.0, 0.008 + h_total), 0.0006, dim_mat, collection)

    # 4. Forward Angled Laboratory Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.180, 0.006, 0.054),
        location=(0.0, -0.052, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.186, 0.004, 0.060),
        location=(0.0, -0.053, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.150, 0.002, 0.008),
        location=(0.0, -0.049, 0.040),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    bar_sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.140, 0.002, 0.006),
        location=(0.0, -0.051, 0.025),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_sub1, collection)

    bar_sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", create_emissive_mat("sec-t-iod-glow", COLOR_LIQUID_IODINE, strength=10.0),
        size=(0.145, 0.002, 0.005),
        location=(0.0, -0.053, 0.012),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_sub2, collection)

    for sx in [-0.065, 0.065]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Leg_{sx}", "cylinder", gold_mat,
            size=(0.004, 0.004, 0.028),
            location=(sx, -0.049, 0.010)
        )
        link_strictly(stanchion, collection)

    print("Built Test_Tube_Section successfully.")

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

    cam_obj.location = Vector((-0.02, -0.32, 0.22))
    direction = Vector((0.0, 0.0, 0.075)) - cam_obj.location
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

    make_light("Key_Left", "AREA", (-0.14, -0.22, 0.28), 5.0, 0.3)
    make_light("Key_Right", "AREA", (0.14, -0.20, 0.26), 4.5, 0.3)
    make_light("Fill_Center", "AREA", (0.0, -0.15, 0.18), 2.5, 0.35)
    make_light("Top_Rim", "AREA", (0.0, 0.15, 0.30), 4.0, 0.35)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Test_Tube_Full")
    sec_col  = bpy.data.collections.new("Test_Tube_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_test_tube_full(full_col)
    build_test_tube_section(sec_col)
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

    # Render Preview 1: Test_Tube_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Test_Tube_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
