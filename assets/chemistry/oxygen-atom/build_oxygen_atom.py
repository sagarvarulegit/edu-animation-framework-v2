"""
build_oxygen_atom.py
====================
NCERT Class 10 Chemistry Activity 1.1 / Chemical Bonding standard 3D model.
Constructs dual collections:
  1. Oxygen_Atom_Full:
     - 8 Protons (red emissive) and 8 Neutrons (slate grey) in a tight Fibonacci spherical cluster.
     - K Shell (n=1, r=0.044m) with 2 electrons.
     - L Shell (n=2, r=0.080m) with 6 valence electrons [2, 6 electronic configuration].
     - Laboratory museum exhibition plinth and support stem with engraved metadata plaque.
  2. Oxygen_Atom_Reduction (Detail / Ionization):
     - Displays electron acceptance (reduction): O [2, 6] + 2e⁻ -> O²⁻ [2, 8].
     - 6 existing valence electrons + 2 vacant orbital sites indicated with glowing indicators.
     - 2 incoming electrons arriving along ionization/reduction trajectories.
     - Pedagogical reduction plaque detailing anion formation and noble gas neon octet.
"""

import math
import shutil
import sys
from pathlib import Path

# Add shared python asset kit to path
KIT_PATH = Path(__file__).resolve().parent.parent.parent / "python"
if str(KIT_PATH) not in sys.path:
    sys.path.insert(0, str(KIT_PATH))

import bpy
import edu_asset_kit as kit
from mathutils import Vector

ASSET_ID = "oxygen-atom"

# Unified color tokens
COLOR_PROTON     = (0.95, 0.22, 0.22)   # Red #ef4444
COLOR_NEUTRON    = (0.45, 0.50, 0.60)   # Slate #64748b
COLOR_ELECTRON   = (0.15, 0.78, 1.0)    # Cyan #38bdf8
COLOR_VACANCY    = (1.0, 0.82, 0.15)    # Amber/Yellow #f59e0b vacancy highlight
COLOR_INCOMING   = (0.20, 0.90, 0.45)   # Green #22c55e incoming electron
COLOR_RING       = (0.30, 0.45, 0.65)   # Metallic steel-blue
COLOR_OCTET_RING = (0.20, 0.85, 0.60)   # Glowing green-cyan octet indicator
COLOR_STAND_BASE = (0.12, 0.14, 0.16)   # Dark lab plinth
COLOR_STAND_STEM = (0.40, 0.42, 0.45)   # Brushed chrome stem
COLOR_GOLD       = (0.85, 0.70, 0.25)   # Polished brass plate
COLOR_TRAJ       = (1.00, 0.48, 0.12)   # Trajectory guide path


def link_strictly(obj, target_col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target_col.objects.link(obj)


def create_emissive_mat(name, color, strength=2.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Roughness"].default_value = 0.20
    node_bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Emission Strength"].default_value = strength
    mat.node_tree.links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    return mat


def make_torus_ring(name, radius, tube_r=0.0008, mat=None, collection=None):
    sub = 16
    profile = []
    for j in range(sub + 1):
        ang = 2.0 * math.pi * j / sub
        profile.append((radius + tube_r * math.cos(ang), tube_r * math.sin(ang)))
    ring = kit.lathe_object(name, profile, segments=64, material=mat)
    if collection:
        link_strictly(ring, collection)
    return ring


def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    disp = p2 - p1
    length = disp.length
    if length < 1e-6:
        length = 1e-6
    center = (p1 + p2) * 0.5
    rot = disp.to_track_quat('Z', 'Y').to_euler()

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False,
        segments=24, radius1=radius, radius2=radius,
        depth=length
    )
    bm.to_mesh(mesh)
    bm.free()

    obj.location = center
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    return obj


# -----------------------------------------------------------------------------
# 1. BUILD OXYGEN ATOM FULL (GROUND STATE [2, 6])
# -----------------------------------------------------------------------------
def build_atom_full(collection):
    proton_mat   = create_emissive_mat('o-full-proton', COLOR_PROTON, strength=1.4)
    neutron_mat  = kit.add_material('o-full-neutron', COLOR_NEUTRON, metallic=0.3, roughness=0.45)
    electron_mat = create_emissive_mat('o-full-electron', COLOR_ELECTRON, strength=3.2)
    ring_mat     = kit.add_machined_metal_material('o-full-ring', COLOR_RING, metallic=0.75, roughness=0.20)
    plinth_mat   = kit.add_material('o-full-plinth', COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    stem_mat     = kit.add_machined_metal_material('o-full-stem', COLOR_STAND_STEM, metallic=0.88, roughness=0.18)
    gold_mat     = kit.add_machined_metal_material('o-full-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)

    # Exhibition Plinth & Stand
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Plinth', 'cube', plinth_mat,
        size=(0.300, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    stem = kit.primitive_object(
        f'{ASSET_ID}_Stand_Post', 'cylinder', stem_mat,
        size=(0.009, 0.009, 0.110),
        location=(0.0, 0.0, 0.055)
    )
    link_strictly(stem, collection)

    # Brass Plaque
    plaque = kit.primitive_object(
        f'{ASSET_ID}_Plaque', 'cube', gold_mat,
        size=(0.095, 0.040, 0.002),
        location=(0.0, -0.080, 0.001)
    )
    link_strictly(plaque, collection)

    # Nucleus: 8 Protons + 8 Neutrons (Fibonacci sphere packing)
    z_nucleus = 0.115
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0
    for i in range(16):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / 16.0)
        r = 0.014 * math.pow((i + 1) / 16.0, 1.0 / 3.0)
        nx = r * math.sin(phi) * math.cos(theta)
        ny = r * math.sin(phi) * math.sin(theta)
        nz = z_nucleus + r * math.cos(phi)
        mat = proton_mat if i < 8 else neutron_mat
        nuc = kit.primitive_object(
            f'{ASSET_ID}_Nuc_{i}', 'uv_sphere', mat,
            size=(0.0085, 0.0085, 0.0085),
            location=(nx, ny, nz)
        )
        link_strictly(nuc, collection)

    # Concentric Bohr Rings tilted slightly for pedagogical 3D depth
    tilt_rad = math.radians(20.0)
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    # Shell configurations: K=2, L=6
    shells = [
        {"name": "K", "radius": 0.044, "count": 2, "angles": [0.0, math.pi]},
        {"name": "L", "radius": 0.080, "count": 6, "angles": [
            0.0, math.pi / 3.0, 2.0 * math.pi / 3.0,
            math.pi, 4.0 * math.pi / 3.0, 5.0 * math.pi / 3.0
        ]}
    ]

    for shell in shells:
        r = shell["radius"]
        ring = make_torus_ring(f'{ASSET_ID}_Ring_{shell["name"]}', r, tube_r=0.00075, mat=ring_mat, collection=collection)
        ring.location = (0.0, 0.0, z_nucleus)
        ring.rotation_euler = (tilt_rad, 0.0, 0.0)

        for e_idx, ang in enumerate(shell["angles"]):
            ex_local = r * math.cos(ang)
            ey_local = r * math.sin(ang)
            ex = ex_local
            ey = ey_local * cos_t
            ez = z_nucleus + ey_local * sin_t
            elec = kit.primitive_object(
                f'{ASSET_ID}_Elec_{shell["name"]}_{e_idx}', 'uv_sphere', electron_mat,
                size=(0.0078, 0.0078, 0.0078),
                location=(ex, ey, ez)
            )
            link_strictly(elec, collection)


# -----------------------------------------------------------------------------
# 2. BUILD OXYGEN ATOM REDUCTION / DETAIL (O + 2e⁻ -> O²⁻)
# -----------------------------------------------------------------------------
def build_atom_detail(collection):
    proton_mat   = create_emissive_mat('o-sec-proton', COLOR_PROTON, strength=1.5)
    neutron_mat  = kit.add_material('o-sec-neutron', COLOR_NEUTRON, metallic=0.3, roughness=0.45)
    electron_mat = create_emissive_mat('o-sec-electron', COLOR_ELECTRON, strength=3.5)
    vacancy_mat  = create_emissive_mat('o-sec-vacancy', COLOR_VACANCY, strength=5.0)
    incoming_mat = create_emissive_mat('o-sec-incoming', COLOR_INCOMING, strength=6.0)
    ring_mat     = kit.add_machined_metal_material('o-sec-ring', COLOR_RING, metallic=0.75, roughness=0.20)
    octet_mat    = create_emissive_mat('o-sec-octet', COLOR_OCTET_RING, strength=2.2)
    traj_mat     = create_emissive_mat('o-sec-traj', COLOR_TRAJ, strength=8.0)
    plinth_mat   = kit.add_material('o-sec-plinth', COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    gold_mat     = kit.add_machined_metal_material('o-sec-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)

    # Base
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Sec_Plinth', 'cube', plinth_mat,
        size=(0.320, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    x_atom = 0.040
    y_atom = 0.000
    z_atom = 0.115

    # Nucleus
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0
    for i in range(16):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / 16.0)
        r = 0.014 * math.pow((i + 1) / 16.0, 1.0 / 3.0)
        nx = x_atom + r * math.sin(phi) * math.cos(theta)
        ny = y_atom + r * math.sin(phi) * math.sin(theta)
        nz = z_atom + r * math.cos(phi)
        mat = proton_mat if i < 8 else neutron_mat
        nuc = kit.primitive_object(
            f'{ASSET_ID}_Sec_Nuc_{i}', 'uv_sphere', mat,
            size=(0.0085, 0.0085, 0.0085),
            location=(nx, ny, nz)
        )
        link_strictly(nuc, collection)

    # K Shell (2 electrons)
    r_k = 0.044
    ring_k = make_torus_ring(f'{ASSET_ID}_Sec_Ring_K', r_k, tube_r=0.00075, mat=ring_mat, collection=collection)
    ring_k.location = (x_atom, y_atom, z_atom)

    for e_idx in range(2):
        ang = math.pi * e_idx
        ex = x_atom + r_k * math.cos(ang)
        ey = y_atom + r_k * math.sin(ang)
        elec = kit.primitive_object(
            f'{ASSET_ID}_Sec_Elec_K_{e_idx}', 'uv_sphere', electron_mat,
            size=(0.0078, 0.0078, 0.0078),
            location=(ex, ey, z_atom)
        )
        link_strictly(elec, collection)

    # L Shell (Valence Octet Formation)
    r_l = 0.082
    ring_l = make_torus_ring(f'{ASSET_ID}_Sec_Ring_L', r_l, tube_r=0.00090, mat=octet_mat, collection=collection)
    ring_l.location = (x_atom, y_atom, z_atom)

    # 6 Existing Electrons in L-shell (at angles 0, 45, 90, 135, 180, 225 deg)
    existing_angles = [
        0.0,
        math.pi / 4.0,
        math.pi / 2.0,
        3.0 * math.pi / 4.0,
        math.pi,
        5.0 * math.pi / 4.0
    ]
    for e_idx, ang in enumerate(existing_angles):
        ex = x_atom + r_l * math.cos(ang)
        ey = y_atom + r_l * math.sin(ang)
        elec = kit.primitive_object(
            f'{ASSET_ID}_Sec_Elec_L_{e_idx}', 'uv_sphere', electron_mat,
            size=(0.0078, 0.0078, 0.0078),
            location=(ex, ey, z_atom)
        )
        link_strictly(elec, collection)

    # 2 Vacant Octet Sites at 270 deg and 315 deg (-90 deg and -45 deg)
    vacant_angles = [3.0 * math.pi / 2.0, 7.0 * math.pi / 4.0]
    for v_idx, ang in enumerate(vacant_angles):
        vx = x_atom + r_l * math.cos(ang)
        vy = y_atom + r_l * math.sin(ang)
        vac_marker = make_torus_ring(f'{ASSET_ID}_Sec_Vac_{v_idx}', 0.009, tube_r=0.0005, mat=vacancy_mat, collection=collection)
        vac_marker.location = (vx, vy, z_atom)

    # 2 Incoming Electrons arriving along trajectory arcs
    v1_pos = (x_atom + r_l * math.cos(3.0 * math.pi / 2.0), y_atom + r_l * math.sin(3.0 * math.pi / 2.0), z_atom)
    inc1_pos = (x_atom + (r_l + 0.045) * math.cos(3.0 * math.pi / 2.0 - 0.2), y_atom + (r_l + 0.045) * math.sin(3.0 * math.pi / 2.0 - 0.2), z_atom + 0.020)
    create_cylinder_segment(f'{ASSET_ID}_Sec_Traj_1', inc1_pos, v1_pos, 0.0006, traj_mat, collection)
    inc_elec_1 = kit.primitive_object(
        f'{ASSET_ID}_Sec_Inc_1', 'uv_sphere', incoming_mat,
        size=(0.0085, 0.0085, 0.0085),
        location=inc1_pos
    )
    link_strictly(inc_elec_1, collection)

    v2_pos = (x_atom + r_l * math.cos(7.0 * math.pi / 4.0), y_atom + r_l * math.sin(7.0 * math.pi / 4.0), z_atom)
    inc2_pos = (x_atom + (r_l + 0.045) * math.cos(7.0 * math.pi / 4.0 + 0.2), y_atom + (r_l + 0.045) * math.sin(7.0 * math.pi / 4.0 + 0.2), z_atom + 0.020)
    create_cylinder_segment(f'{ASSET_ID}_Sec_Traj_2', inc2_pos, v2_pos, 0.0006, traj_mat, collection)
    inc_elec_2 = kit.primitive_object(
        f'{ASSET_ID}_Sec_Inc_2', 'uv_sphere', incoming_mat,
        size=(0.0085, 0.0085, 0.0085),
        location=inc2_pos
    )
    link_strictly(inc_elec_2, collection)

    # 3. Informational Science Plaque on the left
    plq_x = -0.075
    plq_y = 0.010
    plq_rot = (math.radians(12.0), 0.0, math.radians(35.0))
    plq_norm_x = 0.005 * math.sin(math.radians(35.0))
    plq_norm_y = -0.005 * math.cos(math.radians(35.0))

    plaque_base = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Base', 'cube', plinth_mat,
        size=(0.105, 0.010, 0.065),
        location=(plq_x, plq_y, 0.045),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Border', 'cube', gold_mat,
        size=(0.101, 0.002, 0.061),
        location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.045),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat(f'{ASSET_ID}_Sec_Txt', (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(
        f'{ASSET_ID}_Plaque_TitleBar', 'cube', txt_mat,
        size=(0.085, 0.002, 0.005),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.062),
        rotation_euler=plq_rot
    )
    link_strictly(title_bar, collection)

    eq_bar = kit.primitive_object(
        f'{ASSET_ID}_Plaque_EqBar', 'cube', octet_mat,
        size=(0.080, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.050),
        rotation_euler=plq_rot
    )
    link_strictly(eq_bar, collection)

    line_1 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line1', 'cube', vacancy_mat,
        size=(0.070, 0.002, 0.003),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.038),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line2', 'cube', incoming_mat,
        size=(0.062, 0.002, 0.003),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.028),
        rotation_euler=plq_rot
    )
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new('edu_camera')
    cam_data.lens = 42.0
    cam = bpy.data.objects.new('edu_camera', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    cam.location = (0.24, -0.32, 0.20)
    cam_target = Vector((0.0, 0.0, 0.110))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    # Studio Lights
    key_light_data = bpy.data.lights.new('Key_Light', type='AREA')
    key_light_data.energy = 45.0
    key_light_data.size = 0.40
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new('Key_Light', key_light_data)
    key_light.location = (0.26, -0.24, 0.30)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new('Fill_Light', type='AREA')
    fill_light_data.energy = 20.0
    fill_light_data.size = 0.45
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new('Fill_Light', fill_light_data)
    fill_light.location = (-0.26, -0.18, 0.24)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new('Rim_Light', type='POINT')
    rim_light_data.energy = 28.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new('Rim_Light', rim_light_data)
    rim_light.location = (0.0, 0.28, 0.26)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    full_col = bpy.data.collections.new('Oxygen_Atom_Full')
    sec_col  = bpy.data.collections.new('Oxygen_Atom_Reduction')
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_atom_full(full_col)
    build_atom_detail(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f'{ASSET_ID}.blend')

    # Export Full GLB only
    bpy.ops.object.select_all(action='DESELECT')
    for obj in full_col.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = full_col.objects[0]

    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / f'{ASSET_ID}.glb'),
        use_selection=True,
        export_format='GLB'
    )

    viewer_dest = Path('/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets') / f'{ASSET_ID}.glb'
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f'{ASSET_ID}.glb', viewer_dest)
        print(f'Synced GLB to: {viewer_dest}')

    # Render Preview 1: Oxygen_Atom_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=12)
    kit.render_preview(out_dir / 'preview.png')

    # Render Preview 2: Oxygen_Atom_Reduction
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.22, -0.28, 0.17)
    cam_target = Vector((0.0, 0.0, 0.095))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    kit.render_preview(out_dir / 'preview_section.png')

    print(f'=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===')


if __name__ == '__main__':
    main()
