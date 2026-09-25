"""
build_methane_molecule.py
=========================
NCERT Class 10 Chemistry Chapter 4 "Carbon and its Compounds" standard 3D model.
Constructs dual collections:
  1. Methane_Full:
     - Classic CPK ball-and-stick model of methane (CH4) with regular tetrahedral geometry.
     - Central carbon atom (CPK dark charcoal) and 4 hydrogen atoms (crisp off-white).
     - 4 cylindrical covalent bond connector rods (C-H length = 109 pm).
     - Circular bond-angle indicator arc demonstrating the characteristic 109.5° tetrahedral angle.
     - Exhibition display plinth and engraved brass plaque.
  2. Methane_Orbital_Overlap (Detail / Section):
     - Displays the quantum mechanical sp³-1s covalent orbital overlap.
     - 4 directional sp³ hybrid orbital lobes radiating from carbon.
     - 4 spherical 1s orbital envelopes of hydrogen.
     - Glowing σ-bond overlap zones representing shared electron pairs.
     - Science plaque detailing carbon tetravalency, sp³ hybridization, and VSEPR stability.
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

ASSET_ID = "methane-molecule"

# Unified color tokens
COLOR_CARBON      = (0.16, 0.18, 0.20)   # CPK Charcoal/Black #262626
COLOR_HYDROGEN    = (0.94, 0.95, 0.97)   # CPK Off-White #f8fafc
COLOR_BOND        = (0.75, 0.78, 0.82)   # Metallic silver rod #94a3b8
COLOR_ANGLE_ARC   = (0.98, 0.70, 0.15)   # Amber/Gold #f59e0b
COLOR_SP3_LOBE    = (0.10, 0.65, 0.95)   # Translucent azure/cyan sp3 orbital
COLOR_1S_LOBE     = (0.95, 0.75, 0.20)   # Translucent amber 1s orbital
COLOR_OVERLAP     = (0.25, 0.95, 0.55)   # High-emission green-cyan sigma overlap
COLOR_PLINTH      = (0.12, 0.14, 0.16)   # Dark slate plinth
COLOR_GOLD        = (0.85, 0.70, 0.25)   # Polished brass


def link_strictly(obj, target_col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target_col.objects.link(obj)


def create_emissive_mat(name, color, strength=2.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Roughness"].default_value = 0.25
    node_bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Emission Strength"].default_value = strength
    mat.node_tree.links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    return mat


def create_orbital_mat(name, color, alpha=0.55):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Roughness"].default_value = 0.15
    node_bsdf.inputs["Transmission Weight"].default_value = 0.75
    node_bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
    node_bsdf.inputs["Emission Strength"].default_value = 1.0
    mat.node_tree.links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    return mat


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


def get_tetrahedral_positions(center, bond_len):
    s = bond_len / math.sqrt(3.0)
    return [
        center + Vector(( 1.0,  1.0,  1.0)) * s,
        center + Vector(( 1.0, -1.0, -1.0)) * s,
        center + Vector((-1.0,  1.0, -1.0)) * s,
        center + Vector((-1.0, -1.0,  1.0)) * s
    ]


# -----------------------------------------------------------------------------
# 1. BUILD METHANE FULL (CPK BALL-AND-STICK + ANGLE ARC)
# -----------------------------------------------------------------------------
def build_methane_full(collection):
    carbon_mat   = kit.add_material('ch4-full-c', COLOR_CARBON, metallic=0.15, roughness=0.30)
    hydrogen_mat = kit.add_material('ch4-full-h', COLOR_HYDROGEN, metallic=0.05, roughness=0.22)
    bond_mat     = kit.add_machined_metal_material('ch4-full-bond', COLOR_BOND, metallic=0.85, roughness=0.20)
    arc_mat      = create_emissive_mat('ch4-full-arc', COLOR_ANGLE_ARC, strength=4.0)
    plinth_mat   = kit.add_material('ch4-full-plinth', COLOR_PLINTH, metallic=0.15, roughness=0.70)
    stem_mat     = kit.add_machined_metal_material('ch4-full-stem', (0.42, 0.44, 0.48), metallic=0.88, roughness=0.18)
    gold_mat     = kit.add_machined_metal_material('ch4-full-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)

    # Base & Plinth
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Plinth', 'cube', plinth_mat,
        size=(0.280, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    plaque = kit.primitive_object(
        f'{ASSET_ID}_Plaque', 'cube', gold_mat,
        size=(0.110, 0.040, 0.002),
        location=(0.0, -0.080, 0.001)
    )
    link_strictly(plaque, collection)

    center = Vector((0.0, 0.0, 0.105))
    stem = kit.primitive_object(
        f'{ASSET_ID}_Stand_Post', 'cylinder', stem_mat,
        size=(0.008, 0.008, 0.085),
        location=(0.0, 0.0, 0.042)
    )
    link_strictly(stem, collection)

    # Central Carbon Atom
    carbon = kit.primitive_object(
        f'{ASSET_ID}_Carbon', 'uv_sphere', carbon_mat,
        size=(0.048, 0.048, 0.048),
        location=center
    )
    link_strictly(carbon, collection)

    # 4 Hydrogen Vertices
    bond_len = 0.062
    h_positions = get_tetrahedral_positions(center, bond_len)

    for idx, h_pos in enumerate(h_positions):
        h_atom = kit.primitive_object(
            f'{ASSET_ID}_Hydrogen_{idx}', 'uv_sphere', hydrogen_mat,
            size=(0.030, 0.030, 0.030),
            location=h_pos
        )
        link_strictly(h_atom, collection)

        # Bond Cylinder
        create_cylinder_segment(f'{ASSET_ID}_Bond_{idx}', center, h_pos, 0.004, bond_mat, collection)

    # Bond Angle Measurement Arc between H0 and H1
    # Arc between (1,1,1) and (1,-1,-1) vectors from center
    v0 = (h_positions[0] - center).normalized()
    v1 = (h_positions[1] - center).normalized()
    arc_radius = 0.032
    arc_points = 16
    for i in range(arc_points):
        t1 = i / arc_points
        t2 = (i + 1) / arc_points
        # Slerp between v0 and v1
        omega = math.acos(max(-1.0, min(1.0, v0.dot(v1))))
        p_a = (v0 * math.sin((1 - t1) * omega) + v1 * math.sin(t1 * omega)) / math.sin(omega) * arc_radius + center
        p_b = (v0 * math.sin((1 - t2) * omega) + v1 * math.sin(t2 * omega)) / math.sin(omega) * arc_radius + center
        create_cylinder_segment(f'{ASSET_ID}_AngleArc_{i}', p_a, p_b, 0.0009, arc_mat, collection)

    # Badge for 109.5°
    mid_arc = (v0 + v1).normalized() * (arc_radius + 0.008) + center
    badge = kit.primitive_object(
        f'{ASSET_ID}_AngleBadge', 'cube', arc_mat,
        size=(0.016, 0.008, 0.006),
        location=mid_arc
    )
    link_strictly(badge, collection)


# -----------------------------------------------------------------------------
# 2. BUILD METHANE ORBITAL OVERLAP / DETAIL
# -----------------------------------------------------------------------------
def build_methane_orbital_detail(collection):
    carbon_mat   = kit.add_material('ch4-sec-c', COLOR_CARBON, metallic=0.15, roughness=0.30)
    sp3_mat      = create_orbital_mat('ch4-sec-sp3', COLOR_SP3_LOBE, alpha=0.55)
    s1_mat       = create_orbital_mat('ch4-sec-1s', COLOR_1S_LOBE, alpha=0.55)
    overlap_mat  = create_emissive_mat('ch4-sec-overlap', COLOR_OVERLAP, strength=6.0)
    plinth_mat   = kit.add_material('ch4-sec-plinth', COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat     = kit.add_machined_metal_material('ch4-sec-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)
    txt_mat      = create_emissive_mat('ch4-sec-txt', (0.95, 0.95, 0.98), strength=6.0)

    # Base
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Sec_Plinth', 'cube', plinth_mat,
        size=(0.320, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    center = Vector((0.040, 0.0, 0.105))
    bond_len = 0.062
    h_positions = get_tetrahedral_positions(center, bond_len)

    # Central Carbon Nucleus / Core
    carbon = kit.primitive_object(
        f'{ASSET_ID}_Sec_Carbon', 'uv_sphere', carbon_mat,
        size=(0.032, 0.032, 0.032),
        location=center
    )
    link_strictly(carbon, collection)

    for idx, h_pos in enumerate(h_positions):
        direction = (h_pos - center).normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()

        # 1. Directional sp³ hybrid orbital lobe extending from Carbon
        sp3_pos = center + direction * (bond_len * 0.40)
        sp3_lobe = kit.primitive_object(
            f'{ASSET_ID}_Sec_Sp3_{idx}', 'uv_sphere', sp3_mat,
            size=(0.026, 0.026, 0.042),
            location=sp3_pos,
            rotation_euler=rot
        )
        link_strictly(sp3_lobe, collection)

        # 2. Hydrogen 1s spherical orbital
        h_orb = kit.primitive_object(
            f'{ASSET_ID}_Sec_1s_{idx}', 'uv_sphere', s1_mat,
            size=(0.032, 0.032, 0.032),
            location=h_pos
        )
        link_strictly(h_orb, collection)

        # 3. Glowing σ-bond overlap zone (shared electron pair)
        overlap_pos = center + direction * (bond_len * 0.60)
        overlap_mesh = kit.primitive_object(
            f'{ASSET_ID}_Sec_Overlap_{idx}', 'uv_sphere', overlap_mat,
            size=(0.018, 0.018, 0.022),
            location=overlap_pos,
            rotation_euler=rot
        )
        link_strictly(overlap_mesh, collection)

    # Educational Plaque on the left
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

    title_bar = kit.primitive_object(
        f'{ASSET_ID}_Plaque_TitleBar', 'cube', txt_mat,
        size=(0.085, 0.002, 0.005),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.062),
        rotation_euler=plq_rot
    )
    link_strictly(title_bar, collection)

    eq_bar = kit.primitive_object(
        f'{ASSET_ID}_Plaque_EqBar', 'cube', overlap_mat,
        size=(0.080, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.050),
        rotation_euler=plq_rot
    )
    link_strictly(eq_bar, collection)

    line_1 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line1', 'cube', sp3_mat,
        size=(0.072, 0.002, 0.003),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.038),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line2', 'cube', s1_mat,
        size=(0.065, 0.002, 0.003),
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
    cam_target = Vector((0.0, 0.0, 0.100))
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

    full_col = bpy.data.collections.new('Methane_Full')
    sec_col  = bpy.data.collections.new('Methane_Orbital_Overlap')
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_methane_full(full_col)
    build_methane_orbital_detail(sec_col)
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

    # Render Preview 1: Methane_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=12)
    kit.render_preview(out_dir / 'preview.png')

    # Render Preview 2: Methane_Orbital_Overlap
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
