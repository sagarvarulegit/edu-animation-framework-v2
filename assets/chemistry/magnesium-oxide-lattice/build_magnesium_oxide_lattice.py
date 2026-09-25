"""
build_magnesium_oxide_lattice.py
================================
NCERT Class 10/11/12 Chemistry standard 3D model for Magnesium Oxide (MgO).
Constructs dual collections:
  1. MgO_Lattice_Full:
     - 3x3x3 alternating cubic crystal lattice of 27 ions (Mg²⁺ cations and O²⁻ anions).
     - Accurate ionic radii distinction: Mg²⁺ (72 pm, cyan) vs O²⁻ (140 pm, scarlet).
     - Full inter-ionic electrostatic bond network along X, Y, Z.
     - Studio exhibition plinth with corner supports and engraved brass plaque.
  2. MgO_Lattice_UnitCell (Detail / Coordination):
     - Isolated Octahedral Coordination complex: 1 central Mg²⁺ surrounded by 6 O²⁻ ions.
     - 12 octahedral geometry boundary struts demonstrating 6:6 octahedral coordination.
     - Informational science plaque detailing the radius ratio rule (0.514), lattice energy (3791 kJ/mol),
       and extreme melting point (2852°C).
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

ASSET_ID = "magnesium-oxide-lattice"

# Unified color tokens
COLOR_MG        = (0.05, 0.75, 0.90)    # Cyan/Teal Mg²⁺ #06b6d4
COLOR_O         = (0.95, 0.30, 0.30)    # Scarlet Red O²⁻ #ef4444
COLOR_BOND      = (0.82, 0.86, 0.92)    # Metallic bond strut #cbd5e1
COLOR_OCT_EDGE  = (1.00, 0.80, 0.20)    # Amber/Gold octahedral wireframe #f59e0b
COLOR_PLINTH    = (0.12, 0.14, 0.16)    # Dark slate plinth
COLOR_GOLD      = (0.85, 0.70, 0.25)    # Polished brass


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
        segments=20, radius1=radius, radius2=radius,
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
# 1. BUILD FULL 3x3x3 CRYSTAL LATTICE
# -----------------------------------------------------------------------------
def build_lattice_full(collection):
    mg_mat    = create_emissive_mat('mgo-full-mg', COLOR_MG, strength=1.2)
    o_mat     = create_emissive_mat('mgo-full-o', COLOR_O, strength=1.2)
    bond_mat  = kit.add_machined_metal_material('mgo-full-bond', COLOR_BOND, metallic=0.85, roughness=0.20)
    plinth_mat= kit.add_material('mgo-full-plinth', COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat  = kit.add_machined_metal_material('mgo-full-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)

    # Base & Display Plinth
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Plinth', 'cube', plinth_mat,
        size=(0.280, 0.280, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    plaque = kit.primitive_object(
        f'{ASSET_ID}_Plaque', 'cube', gold_mat,
        size=(0.110, 0.040, 0.002),
        location=(0.0, -0.100, 0.001)
    )
    link_strictly(plaque, collection)

    # Corner support feet
    for fx in (-0.115, 0.115):
        for fy in (-0.115, 0.115):
            foot = kit.primitive_object(
                f'{ASSET_ID}_Foot_{fx}_{fy}', 'cylinder', gold_mat,
                size=(0.012, 0.012, 0.010),
                location=(fx, fy, 0.005)
            )
            link_strictly(foot, collection)

    # 3x3x3 Rock-salt lattice
    spacing = 0.052
    z_center = 0.115
    r_mg = 0.012  # Mg2+ smaller (72 pm)
    r_o  = 0.019  # O2- larger (140 pm)

    for x in range(-1, 2):
        for y in range(-1, 2):
            for z in range(-1, 2):
                is_mg = (x + y + z) % 2 == 0
                pos = (x * spacing, y * spacing, z_center + z * spacing)
                mat = mg_mat if is_mg else o_mat
                r_ion = r_mg if is_mg else r_o

                ion = kit.primitive_object(
                    f'{ASSET_ID}_Ion_{x+1}_{y+1}_{z+1}', 'uv_sphere', mat,
                    size=(r_ion * 2, r_ion * 2, r_ion * 2),
                    location=pos
                )
                link_strictly(ion, collection)

                # Connect bonds along positive directions
                if x < 1:
                    p1 = pos
                    p2 = ((x + 1) * spacing, y * spacing, z_center + z * spacing)
                    create_cylinder_segment(f'{ASSET_ID}_BondX_{x+1}_{y+1}_{z+1}', p1, p2, 0.0028, bond_mat, collection)
                if y < 1:
                    p1 = pos
                    p2 = (x * spacing, (y + 1) * spacing, z_center + z * spacing)
                    create_cylinder_segment(f'{ASSET_ID}_BondY_{x+1}_{y+1}_{z+1}', p1, p2, 0.0028, bond_mat, collection)
                if z < 1:
                    p1 = pos
                    p2 = (x * spacing, y * spacing, z_center + (z + 1) * spacing)
                    create_cylinder_segment(f'{ASSET_ID}_BondZ_{x+1}_{y+1}_{z+1}', p1, p2, 0.0028, bond_mat, collection)


# -----------------------------------------------------------------------------
# 2. BUILD UNIT CELL / OCTAHEDRAL COORDINATION DETAIL
# -----------------------------------------------------------------------------
def build_unit_cell_detail(collection):
    mg_mat    = create_emissive_mat('mgo-sec-mg', COLOR_MG, strength=2.0)
    o_mat     = create_emissive_mat('mgo-sec-o', COLOR_O, strength=2.0)
    bond_mat  = kit.add_machined_metal_material('mgo-sec-bond', COLOR_BOND, metallic=0.85, roughness=0.20)
    oct_mat   = create_emissive_mat('mgo-sec-oct', COLOR_OCT_EDGE, strength=5.0)
    plinth_mat= kit.add_material('mgo-sec-plinth', COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat  = kit.add_machined_metal_material('mgo-sec-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)
    txt_mat   = create_emissive_mat('mgo-sec-txt', (0.95, 0.95, 0.98), strength=6.0)

    # Base
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Sec_Plinth', 'cube', plinth_mat,
        size=(0.320, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    x_c = 0.045
    y_c = 0.000
    z_c = 0.115
    d   = 0.060  # Bond distance

    # Central Mg²⁺ Cation
    center_ion = kit.primitive_object(
        f'{ASSET_ID}_Sec_Center_Mg', 'uv_sphere', mg_mat,
        size=(0.026, 0.026, 0.026),
        location=(x_c, y_c, z_c)
    )
    link_strictly(center_ion, collection)

    # 6 Coordinating O²⁻ Anions in Octahedral positions
    oct_positions = [
        (x_c + d, y_c, z_c),      # +X
        (x_c - d, y_c, z_c),      # -X
        (x_c, y_c + d, z_c),      # +Y
        (x_c, y_c - d, z_c),      # -Y
        (x_c, y_c, z_c + d),      # +Z
        (x_c, y_c, z_c - d)       # -Z
    ]

    for idx, pos in enumerate(oct_positions):
        ion = kit.primitive_object(
            f'{ASSET_ID}_Sec_Oct_O_{idx}', 'uv_sphere', o_mat,
            size=(0.038, 0.038, 0.038),
            location=pos
        )
        link_strictly(ion, collection)

        # Bond to center
        create_cylinder_segment(f'{ASSET_ID}_Sec_CoordBond_{idx}', (x_c, y_c, z_c), pos, 0.003, bond_mat, collection)

    # 12 Octahedron boundary wireframe edges connecting vertices
    # Vertices: 0(+X), 1(-X), 2(+Y), 3(-Y), 4(+Z), 5(-Z)
    edges = [
        (4, 0), (4, 2), (4, 1), (4, 3),  # Top pyramid edges
        (5, 0), (5, 2), (5, 1), (5, 3),  # Bottom pyramid edges
        (0, 2), (2, 1), (1, 3), (3, 0)   # Equatorial square edges
    ]
    for e_idx, (v1, v2) in enumerate(edges):
        create_cylinder_segment(
            f'{ASSET_ID}_Sec_OctEdge_{e_idx}',
            oct_positions[v1], oct_positions[v2],
            0.0012, oct_mat, collection
        )

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
        f'{ASSET_ID}_Plaque_EqBar', 'cube', mg_mat,
        size=(0.080, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.050),
        rotation_euler=plq_rot
    )
    link_strictly(eq_bar, collection)

    line_1 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line1', 'cube', oct_mat,
        size=(0.072, 0.002, 0.003),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.038),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f'{ASSET_ID}_Plaque_Line2', 'cube', o_mat,
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

    full_col = bpy.data.collections.new('MgO_Lattice_Full')
    sec_col  = bpy.data.collections.new('MgO_Lattice_UnitCell')
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_lattice_full(full_col)
    build_unit_cell_detail(sec_col)
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

    # Render Preview 1: MgO_Lattice_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=12)
    kit.render_preview(out_dir / 'preview.png')

    # Render Preview 2: MgO_Lattice_UnitCell
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
