"""
build_switch.py — Laboratory Plug Key / Knife Switch
NCERT Class 10 Science Chapter 11 (Electricity) Fig 11.1 & Fig 11.2 (Circuit Symbols & Plug Key).

Dual Collections:
  1. Switch_Full:
     - Real-world laboratory plug key mounted on studio slate plinth with rubber feet.
     - Two heavy machined solid brass blocks separated by a precision conical socket gap.
     - Twin knurled brass binding posts with wire-clamping holes.
     - Tapered solid brass plug key with molded black phenolic fluted handle inserted into socket (Closed Key [(.)], Circuit Closed).

  2. Switch_Section (Open vs Closed Contact Mechanism & Exploded Plug Key):
     - Plug key elevated above the tapered socket revealing the air gap:
       * Tapered ground-metal contact surfaces of the brass plug and blocks.
       * Infinite air resistance gap (R = inf, Open Key [ ], Circuit Open).
       * Luminescent cyan current flow vectors indicating open vs closed circuit conduction.
       * Forward-tilted educational plaque on brass stanchions:
         - "LABORATORY PLUG KEY (CIRCUIT SWITCH)"
         - "Open Key: [  ] -> Air Gap (R = inf, Current I = 0)"
         - "Closed Key: [(.)] -> Plug Inserted (Low Contact R, I = V / R)"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'switch'

# Calibrated Laboratory Palette
COLOR_BASE_SLATE     = (0.12, 0.14, 0.18)     # Studio slate / ebonite base
COLOR_BRASS_BLOCK    = (0.86, 0.70, 0.28)     # Precision machined brass contact blocks
COLOR_BRASS_PLUG     = (0.90, 0.74, 0.32)     # High-luster tapered brass key plug
COLOR_HANDLE_EBONITE = (0.08, 0.08, 0.10)     # Fluted black phenolic insulating handle
COLOR_FOOT_RUBBER    = (0.04, 0.04, 0.05)     # Molded rubber base feet
COLOR_CURRENT_CYAN   = (0.20, 0.82, 1.00)     # Luminescent cyan current conduction indicator
COLOR_AIR_GAP_ALERT  = (1.00, 0.30, 0.20)     # Emissive orange-red open gap warning indicator
COLOR_TRIM           = (0.95, 0.65, 0.15)     # Educational badge gold accent

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
    center = (v1 + v2) * 0.5

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=12,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(diff)
    obj.rotation_euler = rot_quat.to_euler()
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj

def build_shared_plinth(prefix, collection):
    objs = []
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_BASE_SLATE, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_foot   = kit.add_material(f"{prefix}_foot", COLOR_FOOT_RUBBER, metallic=0.05, roughness=0.8)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                  size=(0.13, 0.08, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.132, 0.082, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)

    # 4 rubber feet
    for sx in [-0.052, 0.052]:
        for sy in [-0.028, 0.028]:
            foot = kit.primitive_object(f"{prefix}_foot_{sx}_{sy}", "cylinder", mat_foot,
                                        size=(0.008, 0.008, 0.003),
                                        location=(sx, sy, -0.0015))
            objs.append(foot)
    return objs

def build_brass_blocks_and_posts(prefix, collection, mat_brass):
    """Builds the two heavy brass blocks and knurled binding posts."""
    objs = []
    # Left Block (-X) & Right Block (+X)
    # Size: 0.034 x 0.030 x 0.016, base z=0.012 -> center z=0.020
    # Left block from x = -0.040 to -0.006 (center -0.023)
    # Right block from x = +0.006 to +0.040 (center +0.023)
    # Central gap is 0.012m wide (with conical hole for plug)
    for sign, name in [(-1, "left"), (1, "right")]:
        block = kit.primitive_object(f"{prefix}_block_{name}", "cube", mat_brass,
                                    size=(0.034, 0.028, 0.016),
                                    location=(sign * 0.023, 0.0, 0.020))
        # Binding post on outer corner
        stud = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_brass,
                                    size=(0.006, 0.006, 0.018),
                                    location=(sign * 0.032, 0.0, 0.033))
        nut = kit.primitive_object(f"{prefix}_nut_{name}", "cylinder", mat_brass,
                                   size=(0.010, 0.010, 0.008),
                                   location=(sign * 0.032, 0.0, 0.036))
        objs.extend([block, stud, nut])
    return objs

def build_switch_full(collection):
    """Collection 1: Complete laboratory plug key in closed state (plug inserted)."""
    prefix = "sw_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_BLOCK, metallic=0.92, roughness=0.25)
    mat_plug   = kit.add_machined_metal_material(f"{prefix}_plug", COLOR_BRASS_PLUG, metallic=0.95, roughness=0.18)
    mat_handle = kit.add_material(f"{prefix}_handle", COLOR_HANDLE_EBONITE, metallic=0.15, roughness=0.35)

    all_objs.extend(build_brass_blocks_and_posts(prefix, collection, mat_brass))

    # Tapered Brass Plug Key inserted in center (x=0, y=0, z=0.016)
    plug_pin = kit.primitive_object(f"{prefix}_plug_pin", "cylinder", mat_plug,
                                    size=(0.011, 0.011, 0.018),
                                    location=(0.0, 0.0, 0.020))
    all_objs.append(plug_pin)

    # Fluted phenolic insulating handle on top of plug
    handle = kit.primitive_object(f"{prefix}_handle", "cylinder", mat_handle,
                                  size=(0.016, 0.016, 0.022),
                                  location=(0.0, 0.0, 0.038))
    handle_top = kit.primitive_object(f"{prefix}_handle_top", "cylinder", mat_handle,
                                      size=(0.018, 0.018, 0.004),
                                      location=(0.0, 0.0, 0.048))
    all_objs.extend([handle, handle_top])

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_switch_section(collection):
    """Collection 2: Exploded/Open Plug Key showing conical air gap, contact mechanics, and plaque."""
    prefix = "sw_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_brass    = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_BLOCK, metallic=0.92, roughness=0.25)
    mat_plug     = kit.add_machined_metal_material(f"{prefix}_plug", COLOR_BRASS_PLUG, metallic=0.95, roughness=0.18)
    mat_handle   = kit.add_material(f"{prefix}_handle", COLOR_HANDLE_EBONITE, metallic=0.15, roughness=0.35)
    mat_air_gap  = create_emissive_mat(f"{prefix}_air_gap", COLOR_AIR_GAP_ALERT, strength=10.0)
    mat_cyan_flow= create_emissive_mat(f"{prefix}_cyan", COLOR_CURRENT_CYAN, strength=12.0)
    mat_trim     = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    all_objs.extend(build_brass_blocks_and_posts(prefix, collection, mat_brass))

    # Elevated Plug Key (showing open state [ ])
    # Elevated along Z to z = 0.052 (lifted 32mm above socket)
    elev_z = 0.052
    plug_pin = kit.primitive_object(f"{prefix}_plug_pin", "cylinder", mat_plug,
                                    size=(0.011, 0.011, 0.018),
                                    location=(0.0, 0.0, elev_z))
    all_objs.append(plug_pin)

    handle = kit.primitive_object(f"{prefix}_handle", "cylinder", mat_handle,
                                  size=(0.016, 0.016, 0.022),
                                  location=(0.0, 0.0, elev_z + 0.018))
    handle_top = kit.primitive_object(f"{prefix}_handle_top", "cylinder", mat_handle,
                                      size=(0.018, 0.018, 0.004),
                                      location=(0.0, 0.0, elev_z + 0.028))
    all_objs.extend([handle, handle_top])

    # Vertical alignment guide dashed/emissive ray
    guide_ray = create_cylinder_segment(f"{prefix}_guide_ray", (0.0, 0.0, 0.020), (0.0, 0.0, elev_z - 0.009), 0.0005, mat_cyan_flow, collection)
    if guide_ray: all_objs.append(guide_ray)

    # Glowing Air Gap Alert in the socket (demonstrating infinite resistance R = inf)
    air_gap = kit.primitive_object(f"{prefix}_air_gap_ind", "cylinder", mat_air_gap,
                                   size=(0.010, 0.010, 0.014),
                                   location=(0.0, 0.0, 0.020))
    all_objs.append(air_gap)

    # Conduction tracks approaching gap from terminals
    c1 = create_cylinder_segment(f"{prefix}_flow_1", (-0.032, 0.0, 0.020), (-0.006, 0.0, 0.020), 0.0006, mat_cyan_flow, collection)
    c2 = create_cylinder_segment(f"{prefix}_flow_2", ( 0.006, 0.0, 0.020), ( 0.032, 0.0, 0.020), 0.0006, mat_cyan_flow, collection)
    if c1: all_objs.append(c1)
    if c2: all_objs.append(c2)

    # Educational Plaque Mounted on Brass Stanchions
    plaque_y = -0.032
    plaque_z = 0.010
    plaque_w = 0.124
    plaque_h = 0.024
    plaque_th = 0.003
    angle_tilt = -math.radians(25.0)
    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')

    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_handle,
                                       size=(plaque_w, plaque_th, plaque_h),
                                       location=(0.0, plaque_y, plaque_z),
                                       rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(plaque_face)

    # Gold rim border
    plaque_trim = kit.primitive_object(f"{prefix}_plaque_trim", "cube", mat_trim,
                                       size=(plaque_w + 0.004, plaque_th * 0.8, plaque_h + 0.004),
                                       location=(0.0, plaque_y, plaque_z),
                                       rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(plaque_trim)

    # Twin brass stanchions
    for side in [-0.045, 0.045]:
        leg = kit.primitive_object(f"{prefix}_plaque_leg_{'l' if side < 0 else 'r'}", "cylinder", mat_brass,
                                  size=(0.003, 0.003, 0.010),
                                  location=(side, plaque_y + 0.006, 0.008))
        all_objs.append(leg)

    # Embossed Formula & Info Bars on Plaque
    front_offset = 0.0018
    # Title bar: PLUG KEY (CIRCUIT SWITCH)
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: Open Key [ ] -> Air Gap (I = 0)
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_air_gap,
                                size=(0.095, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: Closed Key [(.)] -> Circuit On
    l_pos3 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, -0.006))
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_cyan_flow,
                                size=(0.108, 0.0010, 0.0020),
                                location=(l_pos3.x, plaque_y + l_pos3.y, plaque_z + l_pos3.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub2)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("Switch_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Switch_Camera", cam_data)
    cam_obj.location = (0.12, -0.22, 0.16)
    direction = Vector((0.0, 0.0, 0.030)) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    def make_light(name, ltype, loc, energy, size):
        ldata = bpy.data.lights.new(name, ltype)
        ldata.energy = energy
        if ltype == 'AREA':
            ldata.size = size
        lobj = bpy.data.objects.new(name, ldata)
        lobj.location = loc
        bpy.context.scene.collection.objects.link(lobj)
        return lobj

    make_light("Light_Key", "AREA", (0.30, -0.25, 0.35), 28.0, 0.40)
    make_light("Light_Fill", "AREA", (-0.25, -0.25, 0.28), 16.0, 0.40)
    make_light("Light_Top", "AREA", (0.0, -0.02, 0.32), 22.0, 0.40)
    make_light("Light_Rim", "AREA", (-0.10, 0.25, 0.28), 20.0, 0.35)

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Switch_Full")
    sec_col  = bpy.data.collections.new("Switch_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_switch_full(full_col)
    build_switch_section(sec_col)
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

    # Render Preview 1: Switch_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Switch_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== SWITCH BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
