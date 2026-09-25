"""
build_resistor.py — Laboratory Fixed Resistor & Carbon Film Spiral Architecture
NCERT Class 10 Science Chapter 11 (Electricity) & Class 12 Physics (Current Electricity).

Dual Collections:
  1. Resistor_Full:
     - Real-world laboratory bench resistor on studio slate plinth with twin knurled brass binding posts.
     - Contoured high-alumina ceramic body with tinned axial copper leads clamped into posts.
     - Standard 4-band EIA color code rings: Brown (1), Black (0), Red (x10^2), Gold (+/-5%) = 1000 ohms (1 k-ohm).

  2. Resistor_Section (Internal Helical Film Spiral & Micro-Architecture):
     - Longitudinal cutaway through resistor body revealing:
       * Dense high-alumina ceramic (Al2O3) core substrate rod.
       * Helical laser-cut spiral resistive track showing path length l and cross-section A.
       * Welded nickel alloy end-caps and internal solder lead joints.
       * Conformal insulating lacquer protective coating.
       * Luminescent cyan current conduction pathway through the spiral path.
       * Dimension caliper indicating active resistive track length l.
       * Forward-tilted educational plaque on brass stanchions:
         - "FIXED RESISTOR (OHMIC CONDUCTOR)"
         - "Ohm's Law: V = I * R"
         - "Resistance: R = rho * (l / A) [Helical Film Spiral]"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'resistor'

# Calibrated Laboratory Palette
COLOR_CERAMIC_BODY   = (0.84, 0.78, 0.62)     # High-alumina insulating ceramic substrate
COLOR_LEAD_TINNED    = (0.85, 0.86, 0.90)     # Tinned copper axial wire leads
COLOR_NICKEL_CAP     = (0.78, 0.80, 0.84)     # Pressed nickel end-caps
COLOR_CARBON_TRACK   = (0.10, 0.10, 0.12)     # Carbon / metal thin film spiral track
COLOR_BRASS          = (0.86, 0.70, 0.28)     # Knurled brass binding posts & terminals
COLOR_BAND_BROWN     = (0.36, 0.18, 0.08)     # EIA Band 1: Digit 1
COLOR_BAND_BLACK     = (0.05, 0.05, 0.05)     # EIA Band 2: Digit 0
COLOR_BAND_RED       = (0.85, 0.14, 0.12)     # EIA Band 3: Multiplier 10^2
COLOR_BAND_GOLD      = (0.85, 0.72, 0.22)     # EIA Band 4: Tolerance +/-5%
COLOR_CURRENT_CYAN   = (0.20, 0.82, 1.00)     # Luminescent cyan current flow indicator
COLOR_PLINTH         = (0.12, 0.14, 0.18)     # Studio slate pedestal
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
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                  size=(0.14, 0.08, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.142, 0.082, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)
    return objs

def build_binding_posts(prefix, collection, mat_brass):
    """Builds the left and right knurled brass binding posts on the plinth."""
    objs = []
    for sign, name in [(-1, "left"), (1, "right")]:
        stud = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_brass,
                                    size=(0.006, 0.006, 0.018),
                                    location=(sign * 0.045, 0.0, 0.021))
        nut = kit.primitive_object(f"{prefix}_nut_{name}", "cylinder", mat_brass,
                                   size=(0.010, 0.010, 0.008),
                                   location=(sign * 0.045, 0.0, 0.024))
        objs.extend([stud, nut])
    return objs

def build_resistor_full(collection):
    """Collection 1: Real-world bench resistor with 4 color code bands on plinth."""
    prefix = "res_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_brass   = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_body    = kit.add_material(f"{prefix}_body", COLOR_CERAMIC_BODY, metallic=0.05, roughness=0.45)
    mat_lead    = kit.add_machined_metal_material(f"{prefix}_lead", COLOR_LEAD_TINNED, metallic=0.95, roughness=0.18)
    mat_brown   = kit.add_material(f"{prefix}_brown", COLOR_BAND_BROWN, metallic=0.10, roughness=0.35)
    mat_black   = kit.add_material(f"{prefix}_black", COLOR_BAND_BLACK, metallic=0.10, roughness=0.35)
    mat_red     = kit.add_material(f"{prefix}_red", COLOR_BAND_RED, metallic=0.10, roughness=0.35)
    mat_gold    = kit.add_machined_metal_material(f"{prefix}_gold", COLOR_BAND_GOLD, metallic=0.90, roughness=0.25)

    all_objs.extend(build_binding_posts(prefix, collection, mat_brass))

    # Center of resistor suspended horizontally at z = 0.022
    cz = 0.022
    # Resistor body length 0.028m (28mm), diameter 0.010m (10mm)
    body = kit.primitive_object(f"{prefix}_body", "cylinder", mat_body,
                               size=(0.010, 0.010, 0.026),
                               location=(0.0, 0.0, cz),
                               rotation_euler=(0.0, math.pi / 2, 0.0))
    all_objs.append(body)

    # Flanged bulbous end collars
    for sign, name in [(-1, "l"), (1, "r")]:
        collar = kit.primitive_object(f"{prefix}_collar_{name}", "cylinder", mat_body,
                                     size=(0.0112, 0.0112, 0.003),
                                     location=(sign * 0.0125, 0.0, cz),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
        all_objs.append(collar)

    # 4 EIA Color Bands along the cylinder body:
    # Band 1: Brown at x = -0.008
    # Band 2: Black at x = -0.003
    # Band 3: Red   at x = +0.002
    # Band 4: Gold  at x = +0.008
    bands = [
        (-0.008, mat_brown, "1_brown"),
        (-0.003, mat_black, "2_black"),
        ( 0.002, mat_red,   "3_red"),
        ( 0.008, mat_gold,  "4_gold")
    ]
    for pos_x, mat, name in bands:
        band = kit.primitive_object(f"{prefix}_band_{name}", "cylinder", mat,
                                   size=(0.0104, 0.0104, 0.0022),
                                   location=(pos_x, 0.0, cz),
                                   rotation_euler=(0.0, math.pi / 2, 0.0))
        all_objs.append(band)

    # Axial Tinned Leads extending from resistor ends into the binding posts (-X=-0.045, +X=+0.045)
    lead_l = create_cylinder_segment(f"{prefix}_lead_l", (-0.014, 0.0, cz), (-0.045, 0.0, cz), 0.0010, mat_lead, collection)
    lead_r = create_cylinder_segment(f"{prefix}_lead_r", ( 0.014, 0.0, cz), ( 0.045, 0.0, cz), 0.0010, mat_lead, collection)
    if lead_l: all_objs.append(lead_l)
    if lead_r: all_objs.append(lead_r)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_resistor_section(collection):
    """Collection 2: Cutaway Resistor showing internal ceramic core rod, helical carbon film track, and plaque."""
    prefix = "res_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_brass      = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_core       = kit.add_material(f"{prefix}_core", (0.92, 0.92, 0.94), metallic=0.05, roughness=0.35)
    mat_carbon_film= kit.add_material(f"{prefix}_film", COLOR_CARBON_TRACK, metallic=0.35, roughness=0.45)
    mat_nickel_cap = kit.add_machined_metal_material(f"{prefix}_cap", COLOR_NICKEL_CAP, metallic=0.92, roughness=0.22)
    mat_lead       = kit.add_machined_metal_material(f"{prefix}_lead", COLOR_LEAD_TINNED, metallic=0.95, roughness=0.18)
    mat_cyan_flow  = create_emissive_mat(f"{prefix}_cyan", COLOR_CURRENT_CYAN, strength=14.0)
    mat_trim       = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_base       = kit.add_material(f"{prefix}_plaque_base", COLOR_PLINTH, metallic=0.15, roughness=0.45)

    all_objs.extend(build_binding_posts(prefix, collection, mat_brass))

    cz = 0.024
    # 1. Inner Alumina Ceramic Core Rod (solid rod, radius 0.0035m, length 0.026m)
    core = kit.primitive_object(f"{prefix}_ceramic_core", "cylinder", mat_core,
                                size=(0.007, 0.007, 0.026),
                                location=(0.0, 0.0, cz),
                                rotation_euler=(0.0, math.pi / 2, 0.0))
    all_objs.append(core)

    # 2. Helical Carbon Film Spiral Track (modeled as series of spiraling turns along X)
    # 8 helical turns wrapped around the ceramic core
    num_turns = 8
    pitch = 0.022 / num_turns
    for i in range(num_turns):
        tx = -0.011 + (i + 0.5) * pitch
        ring = kit.primitive_object(f"{prefix}_turn_{i}", "cylinder", mat_cyan_flow if i % 2 == 0 else mat_carbon_film,
                                    size=(0.0078, 0.0078, pitch * 0.45),
                                    location=(tx, 0.0, cz),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        all_objs.append(ring)

    # 3. Pressed Nickel Alloy End Caps crimped over the rod ends
    for sign, name in [(-1, "l"), (1, "r")]:
        cap = kit.primitive_object(f"{prefix}_end_cap_{name}", "cylinder", mat_nickel_cap,
                                   size=(0.0084, 0.0084, 0.004),
                                   location=(sign * 0.013, 0.0, cz),
                                   rotation_euler=(0.0, math.pi / 2, 0.0))
        all_objs.append(cap)

    # 4. Axial Leads
    lead_l = create_cylinder_segment(f"{prefix}_lead_l", (-0.014, 0.0, cz), (-0.045, 0.0, cz), 0.0010, mat_lead, collection)
    lead_r = create_cylinder_segment(f"{prefix}_lead_r", ( 0.014, 0.0, cz), ( 0.045, 0.0, cz), 0.0010, mat_lead, collection)
    if lead_l: all_objs.append(lead_l)
    if lead_r: all_objs.append(lead_r)

    # 5. Dimension Caliper Line above Resistor showing effective track length l
    dim_z = cz + 0.012
    dim_line = create_cylinder_segment(f"{prefix}_dim_line", (-0.011, 0.0, dim_z), (0.011, 0.0, dim_z), 0.00045, mat_trim, collection)
    tick_l   = create_cylinder_segment(f"{prefix}_dim_tl", (-0.011, 0.0, dim_z - 0.002), (-0.011, 0.0, dim_z + 0.002), 0.00045, mat_trim, collection)
    tick_r   = create_cylinder_segment(f"{prefix}_dim_tr", ( 0.011, 0.0, dim_z - 0.002), ( 0.011, 0.0, dim_z + 0.002), 0.00045, mat_trim, collection)
    badge_l  = kit.primitive_object(f"{prefix}_dim_badge", "cube", mat_trim,
                                    size=(0.005, 0.001, 0.003),
                                    location=(0.0, 0.0, dim_z + 0.002))
    all_objs.extend([dim_line, tick_l, tick_r, badge_l])

    # 6. Educational Plaque Mounted on Brass Stanchions
    plaque_y = -0.032
    plaque_z = 0.010
    plaque_w = 0.126
    plaque_h = 0.024
    plaque_th = 0.003
    angle_tilt = -math.radians(25.0)
    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')

    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_base,
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
    # Title bar: FIXED RESISTOR (OHMIC)
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: Ohm's Law: V = I * R
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_cyan_flow,
                                size=(0.092, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: R = rho * (l / A)
    l_pos3 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, -0.006))
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_brass,
                                size=(0.112, 0.0010, 0.0020),
                                location=(l_pos3.x, plaque_y + l_pos3.y, plaque_z + l_pos3.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub2)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("Resistor_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Resistor_Camera", cam_data)
    cam_obj.location = (0.12, -0.22, 0.16)
    direction = Vector((0.0, 0.0, 0.022)) - cam_obj.location
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

    full_col = bpy.data.collections.new("Resistor_Full")
    sec_col  = bpy.data.collections.new("Resistor_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_resistor_full(full_col)
    build_resistor_section(sec_col)
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

    # Render Preview 1: Resistor_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Resistor_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== RESISTOR BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
