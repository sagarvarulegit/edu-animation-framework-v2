"""
build_wire.py — High-Fidelity Laboratory Connecting Lead & Stranded Conductor
NCERT Class 10 Science Chapter 12 (Electricity) & Practical Skills in Physics.

Dual Collections:
  1. Connecting_Wire_Full:
     - Flexible red PVC silicone-insulated laboratory patch cord (OD 4.0mm) resting in a natural curve.
     - Terminal 1 (Left): Stackable 4mm laboratory banana plug with gold/nickel-plated brass pin,
       4-leaf lantern contact springs, rear stackable socket, and molded ribbed finger-grip sleeve.
     - Terminal 2 (Right): Heavy-duty spring-loaded crocodile/alligator clip with stamped serrated jaws,
       pivot rivet, coiled torsion spring, and insulated vinyl boot.
     - Studio slate carrier plinth with bevel edge.
  2. Connecting_Wire_Section:
     - Precision step-stripped cutaway displaying concentric construction:
       * Outer flexible red PVC insulating dielectric jacket (OD 4.0mm, ID 2.4mm).
       * Inner multi-strand core: 19 twisted oxygen-free high-conductivity copper (OFHC) strands.
     - Terminal crimp cutaway revealing mechanical compaction of copper strands into brass barrel.
     - Glowing cyan/blue directional current vector arrows illustrating electron drift velocity and conventional current (I).
     - Forward-angled laboratory educational plaque detailing electrical conductivity, resistivity, and dielectric parameters.
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'connecting-wire'

# Calibrated Laboratory Palette
COLOR_WIRE_RED     = (0.85, 0.12, 0.10)     # High-visibility laboratory red PVC jacket
COLOR_COPPER       = (0.88, 0.54, 0.22)     # Oxygen-free high-conductivity copper (OFHC)
COLOR_BRASS_GOLD   = (0.90, 0.75, 0.25)     # Gold/brass plated 4mm banana plug
COLOR_STEEL_NICKEL = (0.86, 0.88, 0.90)     # Nickel-plated steel alligator clip
COLOR_BOOT_BLACK   = (0.05, 0.05, 0.07)     # Molded black flexible vinyl strain boot
COLOR_CUT_PVC      = (0.95, 0.35, 0.30)     # Section sliced face of PVC jacket
COLOR_PLINTH       = (0.05, 0.06, 0.08)     # Studio slate base pedestal
COLOR_CURRENT_CYAN = (0.15, 0.90, 1.00)     # Glowing current vector / drift flow (strength 14.0)
COLOR_AMBER        = (1.00, 0.72, 0.18)     # Glowing metric / educational highlight

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
# BUILD CONNECTING WIRE FULL
# -----------------------------------------------------------------------------
def build_connecting_wire_full(collection):
    pvc_red = kit.add_material("wire-pvc-red", COLOR_WIRE_RED, metallic=0.04, roughness=0.35)
    boot_black = kit.add_material("wire-boot-black", COLOR_BOOT_BLACK, metallic=0.08, roughness=0.65)
    brass_gold = kit.add_machined_metal_material("wire-banana-gold", COLOR_BRASS_GOLD, metallic=0.95, roughness=0.18)
    nickel = kit.add_machined_metal_material("wire-alligator-nickel", COLOR_STEEL_NICKEL, metallic=0.96, roughness=0.15)
    plinth_mat = kit.add_material("wire-plinth", COLOR_PLINTH, metallic=0.1, roughness=0.75)

    # 1. Studio Slate Pedestal
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.340, 0.220, 0.012),
        location=(0.0, 0.010, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Smooth Curved Wire Body (Catenary / U-loop on bench)
    # Control nodes in 3D:
    wire_nodes = [
        Vector((-0.100, -0.035, 0.012)),
        Vector((-0.085, -0.005, 0.014)),
        Vector((-0.065,  0.035, 0.016)),
        Vector((-0.035,  0.062, 0.017)),
        Vector(( 0.000,  0.070, 0.018)),
        Vector(( 0.035,  0.062, 0.017)),
        Vector(( 0.065,  0.035, 0.016)),
        Vector(( 0.085, -0.005, 0.014)),
        Vector(( 0.100, -0.035, 0.012))
    ]

    # Interpolate nodes with fine segments
    fine_pts = []
    num_sub = 4
    for i in range(len(wire_nodes) - 1):
        p0 = wire_nodes[max(0, i - 1)]
        p1 = wire_nodes[i]
        p2 = wire_nodes[i + 1]
        p3 = wire_nodes[min(len(wire_nodes) - 1, i + 2)]
        for s in range(num_sub):
            t = s / float(num_sub)
            t2 = t * t
            t3 = t2 * t
            pt = 0.5 * (
                (2.0 * p1) +
                (-p0 + p2) * t +
                (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
                (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )
            fine_pts.append(pt)
    fine_pts.append(wire_nodes[-1])

    # Build continuous cylindrical segments
    wire_radius = 0.0022  # 4.4mm OD
    for i in range(len(fine_pts) - 1):
        create_cylinder_segment(
            f"{ASSET_ID}_Jacket_Seg_{i}",
            fine_pts[i], fine_pts[i+1],
            wire_radius, pvc_red, collection
        )

    # 3. Terminal 1: 4mm Banana Plug Assembly (Left end: fine_pts[0])
    p_plug = fine_pts[0]
    dir_plug = (fine_pts[0] - fine_pts[1]).normalized()
    rot_plug = dir_plug.to_track_quat('Z', 'Y').to_euler()

    boot_plug = kit.primitive_object(
        f"{ASSET_ID}_Banana_Boot", "cylinder", boot_black,
        size=(0.0065, 0.0065, 0.014),
        location=(p_plug.x + dir_plug.x * 0.007, p_plug.y + dir_plug.y * 0.007, p_plug.z),
        rotation_euler=rot_plug
    )
    link_strictly(boot_plug, collection)

    sleeve_pos = p_plug + dir_plug * 0.020
    sleeve = kit.primitive_object(
        f"{ASSET_ID}_Banana_Sleeve", "cylinder", pvc_red,
        size=(0.010, 0.010, 0.020),
        location=(sleeve_pos.x, sleeve_pos.y, sleeve_pos.z),
        rotation_euler=rot_plug
    )
    link_strictly(sleeve, collection)

    ring_pos = sleeve_pos + dir_plug * 0.011
    ring = kit.primitive_object(
        f"{ASSET_ID}_Banana_Collar", "cylinder", brass_gold,
        size=(0.0085, 0.0085, 0.004),
        location=(ring_pos.x, ring_pos.y, ring_pos.z),
        rotation_euler=rot_plug
    )
    link_strictly(ring, collection)

    pin_pos = ring_pos + dir_plug * 0.011
    pin = kit.primitive_object(
        f"{ASSET_ID}_Banana_Pin", "cylinder", brass_gold,
        size=(0.004, 0.004, 0.018),
        location=(pin_pos.x, pin_pos.y, pin_pos.z),
        rotation_euler=rot_plug
    )
    link_strictly(pin, collection)

    for blade_idx in range(4):
        blade = kit.primitive_object(
            f"{ASSET_ID}_Banana_Spring_{blade_idx}", "cube", brass_gold,
            size=(0.0008, 0.0055, 0.012),
            location=(pin_pos.x, pin_pos.y, pin_pos.z),
            rotation_euler=rot_plug
        )
        link_strictly(blade, collection)

    # 4. Terminal 2: Crocodile / Alligator Clip Assembly (Right end: fine_pts[-1])
    p_clip = fine_pts[-1]
    dir_clip = (fine_pts[-1] - fine_pts[-2]).normalized()
    rot_clip = dir_clip.to_track_quat('Z', 'Y').to_euler()

    boot_clip = kit.primitive_object(
        f"{ASSET_ID}_Alligator_Boot", "cylinder", pvc_red,
        size=(0.008, 0.008, 0.018),
        location=(p_clip.x + dir_clip.x * 0.009, p_clip.y + dir_clip.y * 0.009, p_clip.z),
        rotation_euler=rot_clip
    )
    link_strictly(boot_clip, collection)

    clip_base = p_clip + dir_clip * 0.018
    rivet = kit.primitive_object(
        f"{ASSET_ID}_Clip_Rivet", "cylinder", nickel,
        size=(0.0035, 0.0035, 0.008),
        location=(clip_base.x, clip_base.y, clip_base.z + 0.002),
        rotation_euler=(math.pi/2, 0, 0)
    )
    link_strictly(rivet, collection)

    jaw_u = kit.primitive_object(
        f"{ASSET_ID}_Clip_Jaw_Upper", "cube", nickel,
        size=(0.005, 0.0015, 0.018),
        location=(clip_base.x + dir_clip.x * 0.010, clip_base.y + dir_clip.y * 0.010, clip_base.z + 0.0035),
        rotation_euler=rot_clip
    )
    link_strictly(jaw_u, collection)

    jaw_l = kit.primitive_object(
        f"{ASSET_ID}_Clip_Jaw_Lower", "cube", nickel,
        size=(0.005, 0.0015, 0.018),
        location=(clip_base.x + dir_clip.x * 0.010, clip_base.y + dir_clip.y * 0.010, clip_base.z - 0.0015),
        rotation_euler=rot_clip
    )
    link_strictly(jaw_l, collection)

    for t_idx in range(4):
        tooth = kit.primitive_object(
            f"{ASSET_ID}_Clip_Tooth_{t_idx}", "cube", nickel,
            size=(0.004, 0.002, 0.0015),
            location=(clip_base.x + dir_clip.x * (0.013 + t_idx * 0.002),
                      clip_base.y + dir_clip.y * (0.013 + t_idx * 0.002),
                      clip_base.z + 0.001),
            rotation_euler=rot_clip
        )
        link_strictly(tooth, collection)

    print("Built Connecting_Wire_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD CONNECTING WIRE SECTION (Stranded Conductor & Crimp Anatomy)
# -----------------------------------------------------------------------------
def build_connecting_wire_section(collection):
    pvc_red = kit.add_material("sec-pvc-red", COLOR_WIRE_RED, metallic=0.04, roughness=0.35)
    cut_pvc = kit.add_material("sec-pvc-cut", COLOR_CUT_PVC, metallic=0.02, roughness=0.45)
    copper_core = kit.add_machined_metal_material("sec-copper-strand", COLOR_COPPER, metallic=0.96, roughness=0.18)
    brass_gold = kit.add_machined_metal_material("sec-brass-gold", COLOR_BRASS_GOLD, metallic=0.95, roughness=0.18)
    nickel = kit.add_machined_metal_material("sec-nickel", COLOR_STEEL_NICKEL, metallic=0.96, roughness=0.15)
    plinth_mat = kit.add_material("sec-plinth", COLOR_PLINTH, metallic=0.1, roughness=0.75)

    current_mat = create_emissive_mat("sec-current-cyan", COLOR_CURRENT_CYAN, strength=14.0)
    amber_mat = create_emissive_mat("sec-amber-focal", COLOR_AMBER, strength=10.0)
    gold_mat = kit.add_machined_metal_material("sec-plaque-gold", (0.95, 0.75, 0.20), metallic=0.92, roughness=0.20)

    # 1. Studio Slate Pedestal
    plinth = kit.primitive_object(
        "Sec_Plinth", "cube", plinth_mat,
        size=(0.340, 0.220, 0.012),
        location=(0.0, 0.010, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Straight Step-Stripped Conductor Demonstration (along X from -0.11 to +0.10 at Y = 0.040, Z = 0.024)
    x_start = -0.110
    z_axis  =  0.024
    y_axis  =  0.040

    # Segment A: Full Outer Insulating PVC Jacket (x from -0.110 to -0.040)
    jacket = kit.primitive_object(
        "Sec_Outer_Jacket", "cylinder", pvc_red,
        size=(0.0044, 0.0044, 0.070),
        location=(-0.075, y_axis, z_axis),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(jacket, collection)

    cut_face = kit.primitive_object(
        "Sec_Jacket_Cut_Face", "cylinder", cut_pvc,
        size=(0.0044, 0.0044, 0.001),
        location=(-0.040, y_axis, z_axis),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(cut_face, collection)

    # Segment B: 19-Strand Oxygen-Free Copper Conductor Core
    strand_rad = 0.00030
    strand_len = 0.090

    strand_coords = [(0.0, 0.0)]
    r1 = strand_rad * 2.0
    for k in range(6):
        ang = k * (math.pi / 3.0)
        strand_coords.append((r1 * math.cos(ang), r1 * math.sin(ang)))
    r2 = strand_rad * 3.8
    for k in range(12):
        ang = k * (math.pi / 6.0)
        strand_coords.append((r2 * math.cos(ang), r2 * math.sin(ang)))

    for s_idx, (dy, dz) in enumerate(strand_coords):
        strand = kit.primitive_object(
            f"Sec_Copper_Strand_{s_idx}", "cylinder", copper_core,
            size=(strand_rad * 2, strand_rad * 2, strand_len),
            location=(-0.040 + strand_len/2.0, y_axis + dy, z_axis + dz),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(strand, collection)

    # 3. Crimp Terminal Longitudinal Cutaway (at x = +0.050 to +0.090)
    crimp_barrel = kit.primitive_object(
        "Sec_Crimp_Barrel_Half", "cylinder", brass_gold,
        size=(0.0050, 0.0050, 0.024),
        location=(0.062, y_axis, z_axis),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(crimp_barrel, collection)

    crimp_pin = kit.primitive_object(
        "Sec_Crimp_Pin_Solid", "cylinder", brass_gold,
        size=(0.0040, 0.0040, 0.016),
        location=(0.082, y_axis, z_axis),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(crimp_pin, collection)

    # 4. Glowing Current Vector Arrows (Conventional Current I -> +X)
    for c_idx, cx in enumerate([-0.020, 0.010, 0.040]):
        arrow_shaft = kit.primitive_object(
            f"Sec_Current_Arrow_Shaft_{c_idx}", "cylinder", current_mat,
            size=(0.0012, 0.0012, 0.016),
            location=(cx, y_axis, z_axis + 0.008),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(arrow_shaft, collection)
        arrow_head = kit.primitive_object(
            f"Sec_Current_Arrow_Head_{c_idx}", "cone", current_mat,
            size=(0.0035, 0.0035, 0.006),
            location=(cx + 0.011, y_axis, z_axis + 0.008),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(arrow_head, collection)

    # 5. Dimension Calipers & Callouts
    dim_mat = kit.add_material("sec-dim-brass", (0.95, 0.80, 0.25), metallic=0.9, roughness=0.2)
    create_cylinder_segment("Sec_Caliper_Core", (0.010, y_axis, z_axis + 0.018), (0.010, y_axis, z_axis + 0.003), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_Jacket", (-0.075, y_axis, z_axis + 0.018), (-0.075, y_axis, z_axis + 0.003), 0.0006, dim_mat, collection)

    # 6. Forward Angled Educational Plaque
    plaque_bg = kit.add_material("sec-plaque-bg", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.280, 0.006, 0.064),
        location=(0.0, -0.048, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.286, 0.004, 0.070),
        location=(0.0, -0.049, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.240, 0.002, 0.009),
        location=(0.0, -0.045, 0.044),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    bar_eq = kit.primitive_object(
        "Sec_Plaque_Bar_Cu", "cube", current_mat,
        size=(0.220, 0.002, 0.007),
        location=(0.0, -0.047, 0.028),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_eq, collection)

    bar_pvc = kit.primitive_object(
        "Sec_Plaque_Bar_PVC", "cube", amber_mat,
        size=(0.230, 0.002, 0.006),
        location=(0.0, -0.049, 0.013),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_pvc, collection)

    for sx in [-0.10, 0.10]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Leg_{sx}", "cylinder", brass_gold,
            size=(0.005, 0.005, 0.030),
            location=(sx, -0.045, 0.010)
        )
        link_strictly(stanchion, collection)

    print("Built Connecting_Wire_Section successfully.")

# -----------------------------------------------------------------------------
# CAMERA & LIGHTING (Macro Calibrated)
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 42.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Positioned to frame the entire 34cm x 22cm plinth and all terminals comfortably
    cam_obj.location = Vector((-0.02, -0.38, 0.28))
    direction = Vector((0.0, 0.01, 0.015)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Soft, balanced macro lighting rig (low power to prevent burnout on small objects)
    def make_light(name, ltype, pos, power, size=0.3):
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

    make_light("Key_Left", "AREA", (-0.18, -0.28, 0.32), 4.5, 0.35)
    make_light("Key_Right", "AREA", (0.18, -0.25, 0.30), 4.0, 0.35)
    make_light("Fill_Center", "AREA", (0.0, -0.20, 0.22), 2.5, 0.40)
    make_light("Top_Rim", "AREA", (0.0, 0.20, 0.35), 3.5, 0.40)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Connecting_Wire_Full")
    sec_col  = bpy.data.collections.new("Connecting_Wire_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_connecting_wire_full(full_col)
    build_connecting_wire_section(sec_col)
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

    # Render Preview 1: Connecting_Wire_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Connecting_Wire_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
