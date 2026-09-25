"""
build_prism.py — High-Fidelity Optical Crown Glass Prism & White Light Dispersion
NCERT Class 10 Science Chapter 11 (The Human Eye and the Colourful World), Section 11.2 (Dispersion of White Light by a Glass Prism).

Dual Collections:
  1. Glass_Prism_Full:
     - Equilateral 60° crown glass optical dispersion prism (side 65mm, height 75mm, n = 1.52) with polished optical transmitting faces and frosted ground-glass base.
     - Precision turned brass spectrometer turntable with 360° vernier degree graduation collar and knurled clamping screw.
     - Studio slate carrier plinth with chamfered edge.
  2. Glass_Prism_Section:
     - Dispersion Demonstration (Sir Isaac Newton's 1665 experiment):
       * Incident collimated narrow pencil beam of white light (strength 14.0) striking face AB.
       * Differential refraction and angular dispersion inside the glass prism (Cauchy's dispersion relation n(λ) = A + B/λ²).
       * Emergent spectral rainbow fan spreading into 7 canonical ROYGBIV rays:
         Red (700nm), Orange (620nm), Yellow (580nm), Green (530nm), Blue (470nm), Indigo (430nm), Violet (400nm).
       * White observation screen receiving the projected rainbow spectrum.
       * Forward-angled laboratory educational plaque:
         - "DISPERSION OF WHITE LIGHT THROUGH GLASS PRISM"
         - "Wavelength dependence: v = c / n(λ)"
         - "n(violet) > n(red) => Violet deviates most, Red deviates least"
         - "Spectrum: V-I-B-G-Y-O-R"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'glass-prism'

# Calibrated Laboratory Palette
COLOR_GLASS_BODY   = (0.95, 0.98, 1.00)     # Crown glass (n = 1.52, transmission = 1.0)
COLOR_GROUND_BASE  = (0.85, 0.90, 0.95)     # Frosted ground glass base
COLOR_BRASS        = (0.88, 0.72, 0.28)     # Turned brass spectrometer table & hardware
COLOR_PLINTH       = (0.07, 0.08, 0.10)     # Studio slate base pedestal
COLOR_WHITE_BEAM   = (1.00, 1.00, 1.00)     # Collimated incident white light pencil (strength 16.0)
COLOR_WHITE_SCREEN = (0.94, 0.94, 0.94)     # Matte white observation screen

# The 7 Canonical Spectral Rainbow Colors (VIBGYOR / ROYGBIV)
SPECTRAL_RAYS = [
    ("Red",    (1.00, 0.12, 0.10), 0.012),   # Least deviation
    ("Orange", (1.00, 0.50, 0.05), 0.009),
    ("Yellow", (1.00, 0.90, 0.10), 0.006),
    ("Green",  (0.12, 0.92, 0.35), 0.003),
    ("Blue",   (0.15, 0.65, 1.00), 0.000),
    ("Indigo", (0.30, 0.25, 0.90), -0.003),
    ("Violet", (0.60, 0.15, 0.90), -0.006)   # Greatest deviation
]

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

def create_equilateral_prism_mesh(name, side, height, glass_mat, base_mat):
    # Equilateral triangle in XY plane, extruded along Z
    h_tri = side * math.sqrt(3.0) / 2.0
    # Centroid at origin: vertices at:
    # A (top apex): (0.0, +2/3 * h_tri)
    # B (bottom left): (-side/2, -1/3 * h_tri)
    # C (bottom right): (+side/2, -1/3 * h_tri)
    y_apex = (2.0 / 3.0) * h_tri
    y_base = (-1.0 / 3.0) * h_tri
    x_half = side / 2.0

    bm = bmesh.new()
    # Bottom vertices (z = 0)
    v0 = bm.verts.new((-x_half, y_base, 0.0))
    v1 = bm.verts.new((x_half, y_base, 0.0))
    v2 = bm.verts.new((0.0, y_apex, 0.0))
    # Top vertices (z = height)
    v3 = bm.verts.new((-x_half, y_base, height))
    v4 = bm.verts.new((x_half, y_base, height))
    v5 = bm.verts.new((0.0, y_apex, height))

    # Faces:
    # Face 0: Bottom base (v0, v1, v2) -> ground glass
    f_bottom = bm.faces.new([v2, v1, v0])
    # Face 1: Top base (v3, v4, v5) -> polished
    f_top = bm.faces.new([v3, v4, v5])
    # Face 2: Back flat base face BC (v0, v1, v4, v3)
    f_back = bm.faces.new([v0, v1, v4, v3])
    # Face 3: Left optical face AB (v0, v3, v5, v2)
    f_left = bm.faces.new([v2, v5, v3, v0])
    # Face 4: Right optical face AC (v1, v2, v5, v4)
    f_right = bm.faces.new([v1, v4, v5, v2])

    f_bottom.material_index = 1
    f_top.material_index = 0
    f_back.material_index = 0
    f_left.material_index = 0
    f_right.material_index = 0

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = False

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(glass_mat)
    obj.data.materials.append(base_mat)
    return obj

# -----------------------------------------------------------------------------
# BUILD GLASS PRISM FULL
# -----------------------------------------------------------------------------
def build_glass_prism_full(collection):
    glass_mat = kit.add_glass_material("prism-glass-clear", COLOR_GLASS_BODY, ior=1.52, roughness=0.008)
    ground_mat = kit.add_glass_material("prism-glass-frosted", COLOR_GROUND_BASE, ior=1.52, roughness=0.65)
    brass = kit.add_machined_metal_material("prism-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    plinth_mat = kit.add_material("prism-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    scale_mat = kit.add_material("prism-dial-scale", (0.92, 0.92, 0.90), metallic=0.0, roughness=0.4)

    # 1. Studio Slate Pedestal
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.280, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Turned Brass Spectrometer Turntable
    # Base collar
    base_ring = kit.primitive_object(
        f"{ASSET_ID}_Table_Base", "cylinder", brass,
        size=(0.110, 0.110, 0.014),
        location=(0.0, 0.0, 0.007)
    )
    link_strictly(base_ring, collection)

    # Rotating graduated table disc
    table_disc = kit.primitive_object(
        f"{ASSET_ID}_Table_Disc", "cylinder", brass,
        size=(0.096, 0.096, 0.008),
        location=(0.0, 0.0, 0.018)
    )
    link_strictly(table_disc, collection)

    # Vernier scale inlay disc
    scale_disc = kit.primitive_object(
        f"{ASSET_ID}_Scale_Disc", "cylinder", scale_mat,
        size=(0.092, 0.092, 0.001),
        location=(0.0, 0.0, 0.0225)
    )
    link_strictly(scale_disc, collection)

    # Knurled brass locking thumb-screw on side
    screw = kit.primitive_object(
        f"{ASSET_ID}_Lock_Screw", "cylinder", brass,
        size=(0.012, 0.012, 0.014),
        location=(-0.058, 0.0, 0.014),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(screw, collection)

    # 3. Equilateral Glass Prism (side 65mm, height 75mm)
    # Centered on the turntable at z = 0.023
    prism = create_equilateral_prism_mesh(
        f"{ASSET_ID}_Body", side=0.065, height=0.075,
        glass_mat=glass_mat, base_mat=ground_mat
    )
    prism.location = Vector((0.0, 0.0, 0.023))
    link_strictly(prism, collection)

    print("Built Glass_Prism_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD GLASS PRISM SECTION (Dispersion & Rainbow Spectrum)
# -----------------------------------------------------------------------------
def build_glass_prism_section(collection):
    glass_mat = kit.add_glass_material("sec-glass-clear", COLOR_GLASS_BODY, ior=1.52, roughness=0.008)
    ground_mat = kit.add_glass_material("sec-glass-frosted", COLOR_GROUND_BASE, ior=1.52, roughness=0.65)
    brass = kit.add_machined_metal_material("sec-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    plinth_mat = kit.add_material("sec-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    screen_mat = kit.add_material("sec-white-screen", COLOR_WHITE_SCREEN, metallic=0.0, roughness=0.92)
    gold_mat = kit.add_machined_metal_material("sec-gold", (0.95, 0.75, 0.20), metallic=0.92, roughness=0.20)
    plaque_bg = kit.add_material("sec-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    beam_white = create_emissive_mat("sec-beam-white", COLOR_WHITE_BEAM, strength=16.0)

    # 1. Base Pedestal & Turntable
    plinth = kit.primitive_object("Sec_Plinth", "cube", plinth_mat, size=(0.320, 0.240, 0.012), location=(0.0, 0.0, -0.006))
    link_strictly(plinth, collection)

    table_disc = kit.primitive_object("Sec_Table_Disc", "cylinder", brass, size=(0.096, 0.096, 0.012), location=(0.0, 0.0, 0.006))
    link_strictly(table_disc, collection)

    # 2. Equilateral Prism (side 65mm, height 75mm)
    prism = create_equilateral_prism_mesh(
        "Sec_Prism_Body", side=0.065, height=0.075,
        glass_mat=glass_mat, base_mat=ground_mat
    )
    prism.location = Vector((0.0, 0.0, 0.012))
    link_strictly(prism, collection)

    # Prism geometry reference:
    # Side AB (left refracting face): runs from (-0.0325, -0.0188) to (0.0, +0.0375) at mid-height Z = 0.050
    # Center of left face AB is at roughly (-0.016, 0.009, 0.050)
    # Side AC (right refracting face): runs from (0.0, +0.0375) to (+0.0325, -0.0188)

    # 3. Incident White Light Pencil Beam (from Left x = -0.110, y = -0.020, z = 0.050)
    p_inc_start = Vector((-0.110, -0.020, 0.050))
    p_entry     = Vector((-0.018, 0.008, 0.050))
    create_cylinder_segment("Sec_Beam_White_Inc", p_inc_start, p_entry, 0.0022, beam_white, collection)

    # Collimator tube housing incident beam
    collimator = kit.primitive_object(
        "Sec_Collimator_Tube", "cylinder", brass,
        size=(0.014, 0.014, 0.045),
        location=(-0.088, -0.015, 0.050),
        rotation_euler=(0.0, math.pi/2, math.radians(-16))
    )
    link_strictly(collimator, collection)

    # 4. Dispersion into 7 Spectral Rainbow Rays (VIBGYOR)
    # The rays travel inside the prism from p_entry to the right face AC, then emerge toward the screen
    p_screen_x = 0.115
    for ray_name, col_rgb, spread_offset in SPECTRAL_RAYS:
        ray_mat = create_emissive_mat(f"sec-ray-{ray_name.lower()}", col_rgb, strength=14.0)

        # Internal path to right face AC:
        # Red deviates least (hits higher/further right), Violet deviates most (hits lower)
        p_exit = Vector((0.016 + spread_offset * 0.3, 0.010 - spread_offset * 0.4, 0.050))
        create_cylinder_segment(f"Sec_Ray_Int_{ray_name}", p_entry, p_exit, 0.0012, ray_mat, collection)

        # Emergent path to observation screen at x = +0.115:
        p_screen = Vector((p_screen_x, -0.020 + spread_offset * 2.8, 0.050))
        create_cylinder_segment(f"Sec_Ray_Out_{ray_name}", p_exit, p_screen, 0.0014, ray_mat, collection)

    # 5. Observation White Screen (at x = +0.118, y = -0.020)
    screen_board = kit.primitive_object(
        "Sec_Obs_Screen", "cube", screen_mat,
        size=(0.004, 0.075, 0.070),
        location=(p_screen_x + 0.003, -0.020, 0.050),
        rotation_euler=(0.0, 0.0, math.radians(15))
    )
    link_strictly(screen_board, collection)

    screen_post = kit.primitive_object(
        "Sec_Screen_Post", "cylinder", brass,
        size=(0.008, 0.008, 0.050),
        location=(p_screen_x + 0.003, -0.020, 0.020)
    )
    link_strictly(screen_post, collection)

    # 6. Forward Angled Laboratory Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.260, 0.006, 0.062),
        location=(0.0, -0.078, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.266, 0.004, 0.068),
        location=(0.0, -0.079, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.230, 0.002, 0.009),
        location=(0.0, -0.075, 0.044),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    # Red bar (least deviated)
    bar_red = kit.primitive_object(
        "Sec_Plaque_Bar_Red", "cube", kit.add_material("sec-plaque-red", (1.0, 0.2, 0.15), metallic=0.0, roughness=0.3),
        size=(0.210, 0.002, 0.006),
        location=(0.0, -0.077, 0.029),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_red, collection)

    # Violet bar (most deviated)
    bar_violet = kit.primitive_object(
        "Sec_Plaque_Bar_Violet", "cube", kit.add_material("sec-plaque-viol", (0.6, 0.15, 0.95), metallic=0.0, roughness=0.3),
        size=(0.220, 0.002, 0.006),
        location=(0.0, -0.079, 0.015),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_violet, collection)

    for sx in [-0.09, 0.09]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Leg_{sx}", "cylinder", brass,
            size=(0.005, 0.005, 0.030),
            location=(sx, -0.075, 0.012)
        )
        link_strictly(stanchion, collection)

    print("Built Glass_Prism_Section successfully.")

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

    # 3/4 perspective view showing incident beam, prism, rainbow dispersion, and screen
    cam_obj.location = Vector((-0.02, -0.32, 0.24))
    direction = Vector((0.0, -0.01, 0.04)) - cam_obj.location
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

    make_light("Key_Left", "AREA", (-0.16, -0.22, 0.28), 5.5, 0.3)
    make_light("Key_Right", "AREA", (0.16, -0.20, 0.26), 5.0, 0.3)
    make_light("Fill_Center", "AREA", (0.0, -0.16, 0.20), 3.0, 0.35)
    make_light("Top_Rim", "AREA", (0.0, 0.16, 0.30), 4.5, 0.35)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Glass_Prism_Full")
    sec_col  = bpy.data.collections.new("Glass_Prism_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_glass_prism_full(full_col)
    build_glass_prism_section(sec_col)
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

    # Render Preview 1: Glass_Prism_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Glass_Prism_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
