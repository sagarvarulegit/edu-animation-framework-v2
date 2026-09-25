"""
build_concave_lens.py — Laboratory Biconcave Lens & Optical Ray Divergence
NCERT Class 10 Science Chapter 10 (Light — Reflection and Refraction).

Dual Collections:
  1. Concave_Lens_Full:
     - Real-world optical laboratory bench lens stand on studio slate plinth with leveling screws.
     - Machined brass circular retaining ring holding a crystal-clear biconcave glass lens (thin center, thick edge).
     - Vertical chrome support post with height-adjustment clamp collar and knurled locking knob.

  2. Concave_Lens_Section (Ray Optics Divergence & Virtual Focus):
     - Ray optics demonstration with illuminated emerald laser beams:
       * Incident parallel rays traveling along optical axis from object space.
       * Diverging refraction as rays emerge into image space.
       * Virtual ray extensions projected backward to the virtual Principal Focus (F1).
       * Principal axis line with brass locator pins for F1 and O (Optical Center).
       * Dimension caliper indicating negative focal length -f.
       * Forward-tilted educational plaque on brass stanchions:
         - "BICONCAVE LENS (DIVERGING LENS)"
         - "Lens Formula: 1/v - 1/u = 1/f (f is negative)"
         - "Power of Lens: P = 1 / f < 0 (Negative Dioptre)"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'concave-lens'

# Calibrated Laboratory Palette
COLOR_GLASS         = (0.95, 0.98, 1.00)     # Flint/crown glass biconcave lens (n = 1.55)
COLOR_BRASS_RING    = (0.86, 0.70, 0.28)     # Machined brass lens retaining ring & clamp
COLOR_CHROME_POST   = (0.90, 0.92, 0.95)     # Polished stainless steel / chrome support rod
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate base pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Gold trim and calibration badges
COLOR_RAY_EMERALD   = (0.10, 0.95, 0.45)     # Glowing emerald 532nm laser ray beam
COLOR_RAY_VIRTUAL   = (0.25, 0.75, 1.00)     # Cyan dashed/thinner virtual ray extension
COLOR_AXIS_LINE     = (0.35, 0.40, 0.48)     # Optical principal axis reference line
COLOR_FOCAL_PIN     = (0.95, 0.75, 0.20)     # Brass focal point locator pins

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
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_level_brass", COLOR_BRASS_RING, metallic=0.92, roughness=0.25)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                  size=(0.14, 0.10, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.142, 0.102, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)

    # 4 brass leveling thumb-screws at corners
    for sx in [-0.058, 0.058]:
        for sy in [-0.038, 0.038]:
            screw = kit.primitive_object(f"{prefix}_level_{sx}_{sy}", "cylinder", mat_brass,
                                        size=(0.008, 0.008, 0.005),
                                        location=(sx, sy, 0.013))
            objs.append(screw)
    return objs

def build_optical_stand(prefix, collection, mat_brass, mat_chrome, center_z=0.075):
    """Builds the vertical chrome post, base boss, clamp collar and knurled knob."""
    objs = []
    boss = kit.primitive_object(f"{prefix}_base_boss", "cylinder", mat_brass,
                                size=(0.024, 0.024, 0.008),
                                location=(0.0, 0.0, 0.016))
    objs.append(boss)

    post = kit.primitive_object(f"{prefix}_chrome_post", "cylinder", mat_chrome,
                                size=(0.008, 0.008, center_z - 0.020),
                                location=(0.0, 0.0, (0.016 + center_z - 0.020) * 0.5))
    objs.append(post)

    clamp = kit.primitive_object(f"{prefix}_clamp_collar", "cube", mat_brass,
                                 size=(0.018, 0.014, 0.012),
                                 location=(0.0, 0.0, center_z - 0.028))
    screw = kit.primitive_object(f"{prefix}_locking_screw", "cylinder", mat_brass,
                                 size=(0.008, 0.008, 0.006),
                                 location=(0.012, 0.0, center_z - 0.028),
                                 rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.extend([clamp, screw])
    return objs

def build_biconcave_lens_mesh(name, mat_glass, center_z=0.075):
    """Generates a precision biconcave glass lens via closed lathe revolution."""
    r_max = 0.028
    t_center = 0.0024
    t_edge = 0.0090
    R_c = 0.070
    num_steps = 20

    top_half = []
    bottom_half = []
    for i in range(num_steps + 1):
        r = r_max * (i / num_steps)
        # Saggita curves inward towards center
        sag = math.sqrt(R_c**2) - math.sqrt(max(0.0, R_c**2 - r**2))
        z_t = t_center * 0.5 + sag
        top_half.append((r, z_t))
        bottom_half.append((r, -z_t))

    lens_profile = [(0.0, -t_center * 0.5)] + bottom_half + list(reversed(top_half)) + [(0.0, t_center * 0.5)]
    lens_obj = kit.lathe_object(name, lens_profile, segments=48, material=mat_glass)
    lens_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    lens_obj.location = (0.0, 0.0, center_z)
    return lens_obj

def build_concave_lens_full(collection):
    """Collection 1: Real-world bench lens stand with biconcave glass lens."""
    prefix = "ccv_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_glass  = kit.add_glass_material(f"{prefix}_glass", tint=COLOR_GLASS, ior=1.55, roughness=0.008)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_RING, metallic=0.92, roughness=0.25)
    mat_chrome = kit.add_machined_metal_material(f"{prefix}_chrome", COLOR_CHROME_POST, metallic=0.96, roughness=0.15)

    center_z = 0.075

    # 1. Optical Stand
    all_objs.extend(build_optical_stand(prefix, collection, mat_brass, mat_chrome, center_z=center_z))

    # 2. Biconcave Glass Lens
    lens = build_biconcave_lens_mesh(f"{prefix}_lens", mat_glass, center_z=center_z)
    link_strictly(lens, collection)
    all_objs.append(lens)

    # 3. Turned Brass Circular Retaining Ring Bezel
    rim_profile = [
        (0.0275, 0.0050),
        (0.0310, 0.0050),
        (0.0310, -0.0050),
        (0.0275, -0.0050),
        (0.0275, 0.0050)
    ]
    rim = kit.lathe_object(f"{prefix}_rim", rim_profile, segments=48, material=mat_brass)
    rim.rotation_euler = (math.pi / 2, 0.0, 0.0)
    rim.location = (0.0, 0.0, center_z)
    link_strictly(rim, collection)
    all_objs.append(rim)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_concave_lens_section(collection):
    """Collection 2: Optical Ray Divergence, Virtual Focus F1, and Educational Plaque."""
    prefix = "ccv_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_glass    = kit.add_glass_material(f"{prefix}_glass", tint=COLOR_GLASS, ior=1.55, roughness=0.008)
    mat_brass    = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_RING, metallic=0.92, roughness=0.25)
    mat_chrome   = kit.add_machined_metal_material(f"{prefix}_chrome", COLOR_CHROME_POST, metallic=0.96, roughness=0.15)
    mat_ray      = create_emissive_mat(f"{prefix}_ray", COLOR_RAY_EMERALD, strength=14.0)
    mat_virt     = create_emissive_mat(f"{prefix}_virt", COLOR_RAY_VIRTUAL, strength=10.0)
    mat_axis     = kit.add_material(f"{prefix}_axis", COLOR_AXIS_LINE, metallic=0.15, roughness=0.45)
    mat_pin      = kit.add_machined_metal_material(f"{prefix}_pin", COLOR_FOCAL_PIN, metallic=0.90, roughness=0.25)
    mat_trim     = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_base     = kit.add_material(f"{prefix}_plaque_base", COLOR_PLINTH, metallic=0.15, roughness=0.45)

    center_z = 0.075

    # 1. Optical Stand & Lens
    all_objs.extend(build_optical_stand(prefix, collection, mat_brass, mat_chrome, center_z=center_z))

    lens = build_biconcave_lens_mesh(f"{prefix}_lens", mat_glass, center_z=center_z)
    link_strictly(lens, collection)
    all_objs.append(lens)

    rim_profile = [
        (0.0275, 0.0050),
        (0.0310, 0.0050),
        (0.0310, -0.0050),
        (0.0275, -0.0050),
        (0.0275, 0.0050)
    ]
    rim = kit.lathe_object(f"{prefix}_rim", rim_profile, segments=48, material=mat_brass)
    rim.rotation_euler = (math.pi / 2, 0.0, 0.0)
    rim.location = (0.0, 0.0, center_z)
    link_strictly(rim, collection)
    all_objs.append(rim)

    # 2. Principal Optical Axis along Y
    axis_line = create_cylinder_segment(f"{prefix}_principal_axis", (0.0, -0.055, center_z), (0.0, 0.055, center_z), 0.0004, mat_axis, collection)
    if axis_line: all_objs.append(axis_line)

    # 3. Ray Optics: Parallel incident rays from -Y diverging at lens into +Y
    # Virtual focus F1 is at (0, -0.036, center_z)
    f_virt = -0.036
    y_start = -0.055
    y_lens = 0.0
    y_end = 0.045

    ray_offsets = [
        ( 0.016, 0.0),
        (-0.016, 0.0),
        (0.0,  0.014),
        (0.0, -0.014)
    ]
    for idx, (ox, oz) in enumerate(ray_offsets):
        # Incident ray parallel to Y
        r_inc = create_cylinder_segment(f"{prefix}_r_inc_{idx}", (ox, y_start, center_z + oz), (ox, y_lens, center_z + oz), 0.0006, mat_ray, collection)
        # Diverging emerging ray (appears to originate from virtual focus F1)
        dir_div = Vector((ox, y_lens - f_virt, oz)).normalized()
        p_emerge = Vector((ox, y_lens, center_z + oz)) + dir_div * (y_end - y_lens)
        r_div = create_cylinder_segment(f"{prefix}_r_div_{idx}", (ox, y_lens, center_z + oz), (p_emerge.x, p_emerge.y, p_emerge.z), 0.0006, mat_ray, collection)
        # Virtual backward extension meeting at F1
        r_virt = create_cylinder_segment(f"{prefix}_r_virt_{idx}", (ox, y_lens, center_z + oz), (0.0, f_virt, center_z), 0.0004, mat_virt, collection)
        for r in [r_inc, r_div, r_virt]:
            if r: all_objs.append(r)

    # 4. Focal Point Pin Indicators (O at 0, F1 at virtual focus)
    pin_O  = kit.primitive_object(f"{prefix}_pin_O", "cylinder", mat_pin, size=(0.002, 0.002, 0.008), location=(0.0, 0.0, center_z - 0.004))
    pin_F1 = kit.primitive_object(f"{prefix}_pin_F1", "cylinder", mat_pin, size=(0.0025, 0.0025, 0.010), location=(0.0, f_virt, center_z - 0.005))
    all_objs.extend([pin_O, pin_F1])

    # 5. Dimension Caliper Line for Virtual Focal Length -f
    dim_x = -0.022
    cal_line = create_cylinder_segment(f"{prefix}_cal_line", (dim_x, f_virt, center_z), (dim_x, 0.0, center_z), 0.00045, mat_trim, collection)
    cal_t1   = create_cylinder_segment(f"{prefix}_cal_t1", (dim_x - 0.002, f_virt, center_z), (dim_x + 0.002, f_virt, center_z), 0.00045, mat_trim, collection)
    cal_t2   = create_cylinder_segment(f"{prefix}_cal_t2", (dim_x - 0.002, 0.0, center_z), (dim_x + 0.002, 0.0, center_z), 0.00045, mat_trim, collection)
    badge_f  = kit.primitive_object(f"{prefix}_dim_badge", "cube", mat_trim, size=(0.002, 0.006, 0.003), location=(dim_x, f_virt * 0.5, center_z + 0.002))
    all_objs.extend([cal_line, cal_t1, cal_t2, badge_f])

    # 6. Educational Plaque Mounted on Brass Stanchions
    plaque_y = -0.038
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
    # Title bar: BICONCAVE LENS (DIVERGING)
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: 1/v - 1/u = 1/f (f < 0)
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_virt,
                                size=(0.095, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: P = 1 / f < 0
    l_pos3 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, -0.006))
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_brass,
                                size=(0.110, 0.0010, 0.0020),
                                location=(l_pos3.x, plaque_y + l_pos3.y, plaque_z + l_pos3.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub2)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("Lens_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Lens_Camera", cam_data)
    cam_obj.location = (0.13, -0.22, 0.16)
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

    full_col = bpy.data.collections.new("Concave_Lens_Full")
    sec_col  = bpy.data.collections.new("Concave_Lens_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_concave_lens_full(full_col)
    build_concave_lens_section(sec_col)
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

    # Render Preview 1: Concave_Lens_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Concave_Lens_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== CONCAVE LENS BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
