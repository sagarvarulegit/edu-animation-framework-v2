"""
build_bulb.py — Laboratory Incandescent Bulb & Joule Heating Mechanism
NCERT Class 10 Science Chapter 11 (Electricity) & Heating Effects of Electric Current.

Dual Collections:
  1. Bulb_Full:
     - Complete laboratory bench lamp assembly on studio slate plinth.
     - Molded black Bakelite lamp holder socket with twin knurled brass binding posts.
     - Threaded brass Edison base, black glass insulating base ring, center solder contact foot.
     - Optical clear glass envelope with authentic teardrop A19 profile.
     - Central pinch-seal glass stem, dual nickel support wires, and coiled tungsten filament.

  2. Bulb_Section (Internal Circuit Conduction & Joule Heating):
     - Cutaway glass envelope revealing internal electrical architecture:
       * High-temperature glowing incandescent tungsten filament (T approx 2500 deg C).
       * Argon-Nitrogen inert gas atmosphere indicator.
       * Internal conduction circuit path: Terminal A -> Center Foot -> Support Wire 1 -> Filament -> Support Wire 2 -> Threaded Shell -> Terminal B.
       * Luminescent cyan current flow indicators tracing the complete loop.
       * Forward-tilted educational plaque on brass stanchions:
         - "INCANDESCENT LAMP (JOULE HEATING)"
         - "Heating Law: H = I^2 * R * t"
         - "Filament: Tungsten (Melting Point 3380 deg C)"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'bulb'

# Calibrated Laboratory Palette
COLOR_SOCKET_BAKELITE = (0.12, 0.13, 0.15)     # Molded black Bakelite lamp holder
COLOR_GLASS           = (0.98, 0.99, 1.00)     # Crystal clear optical glass envelope
COLOR_BRASS           = (0.86, 0.70, 0.28)     # Machined brass threaded base & binding posts
COLOR_LEAD_WIRE       = (0.75, 0.76, 0.80)     # Nickel / molybdenum support wires
COLOR_FILAMENT_OFF    = (0.45, 0.46, 0.48)     # Cold coiled tungsten wire
COLOR_FILAMENT_GLOW   = (1.00, 0.82, 0.42)     # Incandescent warm white tungsten glow
COLOR_INSULATOR_BASE  = (0.05, 0.05, 0.06)     # Vitrite black glass insulator in screw base
COLOR_SOLDER_FOOT     = (0.70, 0.72, 0.75)     # Lead-tin center solder contact foot
COLOR_CURRENT_CYAN    = (0.20, 0.82, 1.00)     # Luminescent cyan current flow indicator
COLOR_PLINTH          = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM            = (0.95, 0.65, 0.15)     # Educational badge gold accent

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
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                  size=(0.12, 0.10, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.122, 0.102, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)
    return objs

def build_socket_assembly(prefix, collection, mat_holder, mat_brass):
    """Builds the laboratory lamp socket holder with two binding posts."""
    objs = []
    # Cylindrical Bakelite socket on top of plinth (z from 0.012 to 0.034)
    socket_base = kit.primitive_object(f"{prefix}_socket_body", "cylinder", mat_holder,
                                       size=(0.046, 0.046, 0.022),
                                       location=(0.0, 0.0, 0.023))
    objs.append(socket_base)

    # Flanged rim at bottom of socket
    socket_rim = kit.primitive_object(f"{prefix}_socket_rim", "cylinder", mat_holder,
                                      size=(0.054, 0.054, 0.006),
                                      location=(0.0, 0.0, 0.015))
    objs.append(socket_rim)

    # Two knurled brass binding posts on left (-X) and right (+X)
    for sign, name in [(-1, "left"), (1, "right")]:
        stud = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_brass,
                                    size=(0.006, 0.006, 0.018),
                                    location=(sign * 0.038, 0.0, 0.021))
        nut = kit.primitive_object(f"{prefix}_nut_{name}", "cylinder", mat_brass,
                                   size=(0.010, 0.010, 0.008),
                                   location=(sign * 0.038, 0.0, 0.024))
        objs.extend([stud, nut])
    return objs

def build_bulb_full(collection):
    """Collection 1: Complete laboratory incandescent bulb in socket on slate plinth."""
    prefix = "bulb_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_holder   = kit.add_material(f"{prefix}_holder", COLOR_SOCKET_BAKELITE, metallic=0.15, roughness=0.45)
    mat_brass    = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_glass    = kit.add_glass_material(f"{prefix}_glass", tint=COLOR_GLASS, ior=1.52, roughness=0.012)
    mat_support  = kit.add_machined_metal_material(f"{prefix}_support", COLOR_LEAD_WIRE, metallic=0.92, roughness=0.25)
    mat_filament = create_emissive_mat(f"{prefix}_fil", COLOR_FILAMENT_GLOW, strength=6.0)

    # 1. Lamp Socket & Terminals
    all_objs.extend(build_socket_assembly(prefix, collection, mat_holder, mat_brass))

    # 2. Threaded Brass Edison Base (E10 miniature laboratory style, z=0.030 to 0.046)
    base_thread = kit.primitive_object(f"{prefix}_screw_base", "cylinder", mat_brass,
                                       size=(0.020, 0.020, 0.016),
                                       location=(0.0, 0.0, 0.038))
    all_objs.append(base_thread)

    # 3. Glass Stem & Support Wires inside Envelope
    # Glass pinch stem (z=0.044 to 0.060)
    stem = kit.primitive_object(f"{prefix}_glass_stem", "cylinder", mat_glass,
                                size=(0.007, 0.007, 0.016),
                                location=(0.0, 0.0, 0.052))
    all_objs.append(stem)

    # Two nickel support wires extending upward and splaying slightly outward
    wire_l = create_cylinder_segment(f"{prefix}_wire_l", (-0.002, 0.0, 0.058), (-0.0045, 0.0, 0.076), 0.00045, mat_support, collection)
    wire_r = create_cylinder_segment(f"{prefix}_wire_r", ( 0.002, 0.0, 0.058), ( 0.0045, 0.0, 0.076), 0.00045, mat_support, collection)
    if wire_l: all_objs.append(wire_l)
    if wire_r: all_objs.append(wire_r)

    # Coiled Tungsten Filament Bridge (horizontal coil between support tips)
    filament = create_cylinder_segment(f"{prefix}_filament", (-0.0045, 0.0, 0.076), (0.0045, 0.0, 0.076), 0.00035, mat_filament, collection)
    if filament: all_objs.append(filament)

    # 4. Blown Teardrop A19 Glass Envelope (lathe profile, z from 0.044 to 0.106)
    # Profile points: (radius, z)
    globe_profile = [
        (0.000, 0.106),
        (0.005, 0.105),
        (0.014, 0.101),
        (0.022, 0.093),
        (0.025, 0.082),   # Max diameter 50mm
        (0.024, 0.072),
        (0.018, 0.060),
        (0.012, 0.050),
        (0.010, 0.044),
        (0.000, 0.044)
    ]
    globe = kit.lathe_object(f"{prefix}_globe", globe_profile, segments=48, material=mat_glass)
    link_strictly(globe, collection)
    all_objs.append(globe)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_bulb_section(collection):
    """Collection 2: Cutaway Glass Envelope revealing Joule Heating & Internal Conduction Circuit."""
    prefix = "bulb_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_holder   = kit.add_material(f"{prefix}_holder", COLOR_SOCKET_BAKELITE, metallic=0.15, roughness=0.45)
    mat_brass    = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_glass    = kit.add_glass_material(f"{prefix}_glass", tint=COLOR_GLASS, ior=1.52, roughness=0.012)
    mat_support  = kit.add_machined_metal_material(f"{prefix}_support", COLOR_LEAD_WIRE, metallic=0.92, roughness=0.25)
    mat_filament = create_emissive_mat(f"{prefix}_fil", COLOR_FILAMENT_GLOW, strength=18.0)
    mat_cyan_flow= create_emissive_mat(f"{prefix}_cyan", COLOR_CURRENT_CYAN, strength=12.0)
    mat_trim     = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    # 1. Lamp Socket & Terminals
    all_objs.extend(build_socket_assembly(prefix, collection, mat_holder, mat_brass))

    # 2. Threaded Brass Base
    base_thread = kit.primitive_object(f"{prefix}_screw_base", "cylinder", mat_brass,
                                       size=(0.020, 0.020, 0.016),
                                       location=(0.0, 0.0, 0.038))
    all_objs.append(base_thread)

    # 3. Glass Stem & Support Wires
    stem = kit.primitive_object(f"{prefix}_glass_stem", "cylinder", mat_glass,
                                size=(0.007, 0.007, 0.016),
                                location=(0.0, 0.0, 0.052))
    all_objs.append(stem)

    # Support wires
    wire_l = create_cylinder_segment(f"{prefix}_wire_l", (-0.002, 0.0, 0.058), (-0.0045, 0.0, 0.076), 0.00045, mat_support, collection)
    wire_r = create_cylinder_segment(f"{prefix}_wire_r", ( 0.002, 0.0, 0.058), ( 0.0045, 0.0, 0.076), 0.00045, mat_support, collection)
    if wire_l: all_objs.append(wire_l)
    if wire_r: all_objs.append(wire_r)

    # Intensely Glowing Incandescent Tungsten Filament
    filament = create_cylinder_segment(f"{prefix}_filament", (-0.0045, 0.0, 0.076), (0.0045, 0.0, 0.076), 0.00045, mat_filament, collection)
    if filament: all_objs.append(filament)

    # 4. Cutaway Glass Envelope (Lathed, then front hemisphere cut away with boolean)
    globe_profile = [
        (0.000, 0.106),
        (0.005, 0.105),
        (0.014, 0.101),
        (0.022, 0.093),
        (0.025, 0.082),
        (0.024, 0.072),
        (0.018, 0.060),
        (0.012, 0.050),
        (0.010, 0.044),
        (0.000, 0.044)
    ]
    globe = kit.lathe_object(f"{prefix}_globe", globe_profile, segments=48, material=mat_glass)
    # Boolean cutter to remove front half Y < 0
    cutter = kit.primitive_object(f"{prefix}_cutter", "cube", mat_holder,
                                  size=(0.060, 0.040, 0.080),
                                  location=(0.0, -0.020, 0.075))
    bpy.ops.object.select_all(action='DESELECT')
    globe.select_set(True)
    bpy.context.view_layer.objects.active = globe
    mod = globe.modifiers.new(name="Bool_Cut", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    link_strictly(globe, collection)
    all_objs.append(globe)

    # 5. Internal Electrical Conduction Loop (Cyan Flow Tracks)
    # Track from Left Terminal (-X=-0.038) through socket into base foot
    c1 = create_cylinder_segment(f"{prefix}_flow_1", (-0.038, 0.0, 0.020), (-0.010, 0.0, 0.020), 0.0006, mat_cyan_flow, collection)
    c2 = create_cylinder_segment(f"{prefix}_flow_2", (-0.010, 0.0, 0.020), (-0.002, 0.0, 0.058), 0.0006, mat_cyan_flow, collection)
    # Track from Right Support through thread shell to Right Terminal (+X=+0.038)
    c3 = create_cylinder_segment(f"{prefix}_flow_3", ( 0.002, 0.0, 0.058), ( 0.010, 0.0, 0.038), 0.0006, mat_cyan_flow, collection)
    c4 = create_cylinder_segment(f"{prefix}_flow_4", ( 0.010, 0.0, 0.038), ( 0.038, 0.0, 0.020), 0.0006, mat_cyan_flow, collection)
    for c in [c1, c2, c3, c4]:
        if c: all_objs.append(c)

    # 6. Educational Plaque Mounted on Brass Stanchions
    plaque_y = -0.038
    plaque_z = 0.010
    plaque_w = 0.114
    plaque_h = 0.024
    plaque_th = 0.003
    angle_tilt = -math.radians(25.0)
    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')

    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_holder,
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
    for side in [-0.040, 0.040]:
        leg = kit.primitive_object(f"{prefix}_plaque_leg_{'l' if side < 0 else 'r'}", "cylinder", mat_brass,
                                  size=(0.003, 0.003, 0.010),
                                  location=(side, plaque_y + 0.006, 0.008))
        all_objs.append(leg)

    # Embossed Formula & Info Bars on Plaque
    front_offset = 0.0018
    # Title bar: JOULE HEATING
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.095, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: H = I^2 * R * t
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_filament,
                                size=(0.088, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: Tungsten 3380 C
    l_pos3 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, -0.006))
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_brass,
                                size=(0.100, 0.0010, 0.0020),
                                location=(l_pos3.x, plaque_y + l_pos3.y, plaque_z + l_pos3.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub2)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("Bulb_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Bulb_Camera", cam_data)
    cam_obj.location = (0.12, -0.22, 0.16)
    direction = Vector((0.0, 0.0, 0.055)) - cam_obj.location
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
    make_light("Light_Top", "AREA", (0.0, -0.02, 0.35), 22.0, 0.40)
    make_light("Light_Rim", "AREA", (-0.10, 0.25, 0.28), 20.0, 0.35)

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Bulb_Full")
    sec_col  = bpy.data.collections.new("Bulb_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_bulb_full(full_col)
    build_bulb_section(sec_col)
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

    # Render Preview 1: Bulb_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Bulb_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== BULB BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
