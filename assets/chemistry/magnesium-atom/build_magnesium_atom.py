"""
build_magnesium_atom.py — NCERT Class 9 & 10 High-Fidelity Magnesium Bohr Atom (Mg, Z=12)
Dual collections:
  - Magnesium_Atom_Full: Neutral ground-state Mg atom [2, 8, 2] with 12p/12n nucleus, K/L/M orbital guide rings, paired electrons, and studio stand
  - Magnesium_Atom_Ionization: Ionization detail showing valence electron transfer (Mg -> Mg2+ + 2e-), octet core, calipers, and technical plaque
"""

import sys
import math
import shutil
from pathlib import Path
from mathutils import Vector, Euler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy
import bmesh

ASSET_ID = 'magnesium-atom'

COLOR_PROTON        = (0.95, 0.22, 0.22)
COLOR_NEUTRON       = (0.45, 0.50, 0.60)
COLOR_ELECTRON      = (0.22, 0.74, 0.97)     # Cyan #38bdf8
COLOR_RING          = (0.35, 0.48, 0.65)
COLOR_STAND_BASE    = (0.12, 0.13, 0.16)
COLOR_CHROME        = (0.85, 0.88, 0.92)
COLOR_GOLD          = (0.90, 0.75, 0.22)
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)
COLOR_ION_CORE      = (0.85, 0.60, 0.95)
COLOR_TRAJECTORY    = (0.30, 0.85, 1.00)


def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_emissive_mat(name, color, strength=8.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Emission Color'].default_value = (*color[:3], 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength
    return mat


def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    diff = p2 - p1
    length = diff.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = diff.to_track_quat('Z', 'Y').to_euler()

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(f'{name}_Mesh')
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = mid
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj


def make_torus_ring(name, radius, tube_r=0.0008, segments=64, mat=None, collection=None):
    sub = 12
    profile = []
    for j in range(sub + 1):
        ang = 2.0 * math.pi * j / sub
        profile.append((radius + tube_r * math.cos(ang), tube_r * math.sin(ang)))
    obj = kit.lathe_object(name, profile, segments=segments, material=mat)
    if collection:
        link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# BUILD MAGNESIUM ATOM FULL (Ground State [2, 8, 2])
# -----------------------------------------------------------------------------
def build_atom_full(collection):
    proton_mat   = create_emissive_mat('mg-full-proton', COLOR_PROTON, strength=1.5)
    neutron_mat  = kit.add_material('mg-full-neutron', COLOR_NEUTRON, metallic=0.3, roughness=0.4)
    electron_mat = create_emissive_mat('mg-full-electron', COLOR_ELECTRON, strength=3.5)
    ring_mat     = kit.add_machined_metal_material('mg-full-ring', COLOR_RING, metallic=0.7, roughness=0.25)
    plinth_mat   = kit.add_material('mg-full-plinth', COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    chrome_mat   = kit.add_machined_metal_material('mg-full-chrome', COLOR_CHROME, metallic=0.96, roughness=0.18)

    # 1. Studio Plinth & Atom Stand Post
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Plinth', 'cube', plinth_mat,
        size=(0.280, 0.200, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    z_atom = 0.145
    post = kit.primitive_object(
        f'{ASSET_ID}_Stand_Post', 'cylinder', chrome_mat,
        size=(0.008, 0.008, z_atom),
        location=(0.0, 0.0, z_atom / 2.0)
    )
    link_strictly(post, collection)

    # 2. Packed 12p + 12n Nucleus
    golden_ratio = (1 + math.sqrt(5)) / 2.0
    for i in range(24):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / 24.0)
        r = 0.018 * math.pow((i + 1) / 24.0, 1.0 / 3.0)
        nx = r * math.sin(phi) * math.cos(theta)
        ny = r * math.sin(phi) * math.sin(theta)
        nz = z_atom + r * math.cos(phi)
        mat = proton_mat if i < 12 else neutron_mat
        nuc = kit.primitive_object(f'{ASSET_ID}_Nuc_{i}', 'uv_sphere', mat,
                                   size=(0.009, 0.009, 0.009),
                                   location=(nx, ny, nz))
        link_strictly(nuc, collection)

    # 3. Concentric Electron Shells [2, 8, 2] (K, L, M)
    # Inclined slightly (15 degrees) around X axis for dynamic 3D presentation
    shells = [
        {'name': 'K', 'radius': 0.045, 'count': 2},
        {'name': 'L', 'radius': 0.082, 'count': 8},
        {'name': 'M', 'radius': 0.125, 'count': 2}
    ]
    tilt_rad = math.radians(18.0)
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    for s_idx, shell in enumerate(shells):
        r = shell['radius']
        count = shell['count']
        ring = make_torus_ring(f'{ASSET_ID}_Ring_{shell["name"]}', r, tube_r=0.0007, mat=ring_mat, collection=collection)
        ring.location = (0.0, 0.0, z_atom)
        ring.rotation_euler = (tilt_rad, 0.0, 0.0)

        for e_idx in range(count):
            ang = 2.0 * math.pi * e_idx / count
            ex_local = r * math.cos(ang)
            ey_local = r * math.sin(ang)
            # Apply tilt
            ex = ex_local
            ey = ey_local * cos_t
            ez = z_atom + ey_local * sin_t
            elec = kit.primitive_object(
                f'{ASSET_ID}_Elec_{shell["name"]}_{e_idx}', 'uv_sphere', electron_mat,
                size=(0.0075, 0.0075, 0.0075),
                location=(ex, ey, ez)
            )
            link_strictly(elec, collection)


# -----------------------------------------------------------------------------
# BUILD MAGNESIUM ATOM IONIZATION / DETAIL
# -----------------------------------------------------------------------------
def build_atom_detail(collection):
    proton_mat   = create_emissive_mat('mg-sec-proton', COLOR_PROTON, strength=1.5)
    neutron_mat  = kit.add_material('mg-sec-neutron', COLOR_NEUTRON, metallic=0.3, roughness=0.4)
    electron_mat = create_emissive_mat('mg-sec-electron', COLOR_ELECTRON, strength=3.5)
    ring_mat     = kit.add_machined_metal_material('mg-sec-ring', COLOR_RING, metallic=0.7, roughness=0.25)
    octet_mat    = create_emissive_mat('mg-sec-octet', COLOR_ION_CORE, strength=2.0)
    traj_mat     = create_emissive_mat('mg-sec-traj', COLOR_TRAJECTORY, strength=10.0)
    plinth_mat   = kit.add_material('mg-sec-plinth', COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    gold_mat     = kit.add_machined_metal_material('mg-sec-gold', COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat      = create_emissive_mat('mg-sec-dim', COLOR_CYAN_DIM, strength=10.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f'{ASSET_ID}_Sec_Plinth', 'cube', plinth_mat,
        size=(0.320, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    z_atom = 0.125
    x_atom = 0.040
    y_atom = 0.000

    # 2. Packed Nucleus
    golden_ratio = (1 + math.sqrt(5)) / 2.0
    for i in range(24):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / 24.0)
        r = 0.018 * math.pow((i + 1) / 24.0, 1.0 / 3.0)
        nx = x_atom + r * math.sin(phi) * math.cos(theta)
        ny = y_atom + r * math.sin(phi) * math.sin(theta)
        nz = z_atom + r * math.cos(phi)
        mat = proton_mat if i < 12 else neutron_mat
        nuc = kit.primitive_object(f'{ASSET_ID}_Sec_Nuc_{i}', 'uv_sphere', mat,
                                   size=(0.009, 0.009, 0.009),
                                   location=(nx, ny, nz))
        link_strictly(nuc, collection)

    # 3. K & L Closed Octet Core Shells
    r_k = 0.045
    r_l = 0.082
    ring_k = make_torus_ring(f'{ASSET_ID}_Sec_Ring_K', r_k, tube_r=0.0007, mat=ring_mat, collection=collection)
    ring_k.location = (x_atom, y_atom, z_atom)

    ring_l = make_torus_ring(f'{ASSET_ID}_Sec_Ring_L', r_l, tube_r=0.0009, mat=octet_mat, collection=collection)
    ring_l.location = (x_atom, y_atom, z_atom)

    # K electrons (2)
    for e_idx in range(2):
        ang = math.pi * e_idx
        ex = x_atom + r_k * math.cos(ang)
        ey = y_atom + r_k * math.sin(ang)
        elec = kit.primitive_object(f'{ASSET_ID}_Sec_Elec_K_{e_idx}', 'uv_sphere', electron_mat,
                                   size=(0.0075, 0.0075, 0.0075), location=(ex, ey, z_atom))
        link_strictly(elec, collection)

    # L electrons (8 - stable closed octet)
    for e_idx in range(8):
        ang = 2.0 * math.pi * e_idx / 8.0
        ex = x_atom + r_l * math.cos(ang)
        ey = y_atom + r_l * math.sin(ang)
        elec = kit.primitive_object(f'{ASSET_ID}_Sec_Elec_L_{e_idx}', 'uv_sphere', electron_mat,
                                   size=(0.0075, 0.0075, 0.0075), location=(ex, ey, z_atom))
        link_strictly(elec, collection)

    # 4. Ionization Step: 2 Valence Electrons Ejected Along Trajectories (M-shell)
    r_m = 0.125
    # M-shell ring (dotted/faded appearance)
    ring_m = make_torus_ring(f'{ASSET_ID}_Sec_Ring_M', r_m, tube_r=0.0004, mat=dim_mat, collection=collection)
    ring_m.location = (x_atom, y_atom, z_atom)

    # Electron 1 departing towards top-right
    p_e1_start = (x_atom + r_m * math.cos(math.radians(35.0)), y_atom + r_m * math.sin(math.radians(35.0)), z_atom)
    p_e1_end   = (x_atom + (r_m + 0.035) * math.cos(math.radians(45.0)), y_atom + (r_m + 0.035) * math.sin(math.radians(45.0)), z_atom + 0.015)
    create_cylinder_segment(f'{ASSET_ID}_Traj_1', p_e1_start, p_e1_end, 0.0006, traj_mat, collection)
    e1_obj = kit.primitive_object(f'{ASSET_ID}_Sec_Ejected_1', 'uv_sphere', electron_mat,
                                  size=(0.008, 0.008, 0.008), location=p_e1_end)
    link_strictly(e1_obj, collection)

    # Electron 2 departing towards bottom-right
    p_e2_start = (x_atom + r_m * math.cos(math.radians(-35.0)), y_atom + r_m * math.sin(math.radians(-35.0)), z_atom)
    p_e2_end   = (x_atom + (r_m + 0.035) * math.cos(math.radians(-45.0)), y_atom + (r_m + 0.035) * math.sin(math.radians(-45.0)), z_atom - 0.015)
    create_cylinder_segment(f'{ASSET_ID}_Traj_2', p_e2_start, p_e2_end, 0.0006, traj_mat, collection)
    e2_obj = kit.primitive_object(f'{ASSET_ID}_Sec_Ejected_2', 'uv_sphere', electron_mat,
                                  size=(0.008, 0.008, 0.008), location=p_e2_end)
    link_strictly(e2_obj, collection)

    # 5. Educational Plaque
    plq_x = -0.075
    plq_y = 0.010
    plq_rot = (math.radians(12.0), 0.0, math.radians(35.0))
    plq_norm_x = 0.005 * math.sin(math.radians(35.0))
    plq_norm_y = -0.005 * math.cos(math.radians(35.0))

    plaque_base = kit.primitive_object(f'{ASSET_ID}_Plaque_Base', 'cube', plinth_mat,
                                       size=(0.105, 0.010, 0.065),
                                       location=(plq_x, plq_y, 0.045),
                                       rotation_euler=plq_rot)
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(f'{ASSET_ID}_Plaque_Border', 'cube', gold_mat,
                                         size=(0.101, 0.002, 0.061),
                                         location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.045),
                                         rotation_euler=plq_rot)
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat(f'{ASSET_ID}_Sec_Txt', (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(f'{ASSET_ID}_Plaque_TitleBar', 'cube', txt_mat,
                                     size=(0.085, 0.002, 0.005),
                                     location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.062),
                                     rotation_euler=plq_rot)
    link_strictly(title_bar, collection)

    # Ionization formula: Mg -> Mg2+ + 2e-
    eq_bar = kit.primitive_object(f'{ASSET_ID}_Plaque_EqBar', 'cube', octet_mat,
                                  size=(0.078, 0.002, 0.004),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.050),
                                  rotation_euler=plq_rot)
    link_strictly(eq_bar, collection)

    line_1 = kit.primitive_object(f'{ASSET_ID}_Plaque_Line1', 'cube', dim_mat,
                                  size=(0.070, 0.002, 0.003),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.038),
                                  rotation_euler=plq_rot)
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(f'{ASSET_ID}_Plaque_Line2', 'cube', traj_mat,
                                  size=(0.060, 0.002, 0.003),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.028),
                                  rotation_euler=plq_rot)
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING SETUP
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new('edu_camera')
    cam_data.lens = 42.0
    cam = bpy.data.objects.new('edu_camera', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Framed angled laboratory view showcasing Bohr shells and nucleus
    cam.location = (0.26, -0.34, 0.22)
    cam_target = Vector((0.0, 0.0, 0.120))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new('Key_Light', type='AREA')
    key_light_data.energy = 45.0
    key_light_data.size = 0.40
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new('Key_Light', key_light_data)
    key_light.location = (0.28, -0.25, 0.32)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new('Fill_Light', type='AREA')
    fill_light_data.energy = 20.0
    fill_light_data.size = 0.45
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new('Fill_Light', fill_light_data)
    fill_light.location = (-0.28, -0.20, 0.26)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new('Rim_Light', type='POINT')
    rim_light_data.energy = 30.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new('Rim_Light', rim_light_data)
    rim_light.location = (0.0, 0.30, 0.28)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    full_col = bpy.data.collections.new('Magnesium_Atom_Full')
    sec_col  = bpy.data.collections.new('Magnesium_Atom_Ionization')
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

    # Render Preview 1: Magnesium_Atom_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / 'preview.png')

    # Render Preview 2: Magnesium_Atom_Ionization
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.22, -0.30, 0.18)
    cam_target = Vector((0.0, 0.0, 0.100))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    kit.render_preview(out_dir / 'preview_section.png')

    print(f'=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===')


if __name__ == '__main__':
    main()
