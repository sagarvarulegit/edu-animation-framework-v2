"""
build_convex_mirror.py — Laboratory Convex Spherical Mirror & Optical Ray Reflection
NCERT Class 10 Science Chapter 10 (Light — Reflection and Refraction) Fig 10.5 & 10.8.

Dual Collections:
  1. Convex_Mirror_Full:
     - Real-world optical laboratory bench spherical convex mirror stand on studio slate plinth.
     - Machined brass circular bezel retaining ring holding a front-silvered convex spherical mirror dish (bulging forward).
     - Protective rear backing shell, swivel bracket, vertical chrome support post, and leveling screws.

  2. Convex_Mirror_Section (Ray Reflection, Virtual Focus F, Center of Curvature C):
     - Ray optics demonstration with illuminated emerald laser beams:
       * Principal axis line passing through Pole P, virtual Focus F, and Center of Curvature C.
       * Incident parallel rays traveling along optical axis from object space (-Y).
       * Reflected diverging rays spreading outwards into object space.
       * Virtual backward ray extensions meeting at virtual Focus F behind the mirror.
       * Brass locator pins for P, F, and C with focal length dimension caliper.
       * Forward-tilted educational plaque on brass stanchions:
         - "CONVEX SPHERICAL MIRROR (DIVERGING)"
         - "Mirror Formula: 1/v + 1/u = 1/f (f is virtual)"
         - "Application: Vehicle Rear-View Mirror (Wide Field of View)"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'convex-mirror'

# Calibrated Laboratory Palette
COLOR_SILVER_MIRROR = (0.95, 0.96, 0.98)     # High-reflectivity silver mirror surface
COLOR_BACK_SHELL    = (0.12, 0.12, 0.14)     # Protective black bakelite/metal back shell
COLOR_BRASS_RING    = (0.86, 0.70, 0.28)     # Machined brass bezel ring & swivel clamp
COLOR_CHROME_POST   = (0.90, 0.92, 0.95)     # Polished stainless steel / chrome support rod
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate base pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Gold trim and calibration badges
COLOR_RAY_EMERALD   = (0.10, 0.95, 0.45)     # Glowing emerald 532nm laser ray beam
COLOR_RAY_VIRTUAL   = (0.25, 0.75, 1.00)     # Cyan dashed/thinner virtual ray extension
COLOR_NORMAL_LINE   = (1.00, 0.85, 0.20)     # Normal reference lines from center of curvature C
COLOR_AXIS_LINE     = (0.35, 0.40, 0.48)     # Optical principal axis reference line
COLOR_FOCAL_PIN     = (0.95, 0.75, 0.20)     # Brass locator pins for P, F, C

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

    # 4 brass leveling screws at corners
    for sx in [-0.058, 0.058]:
        for sy in [-0.038, 0.038]:
            screw = kit.primitive_object(f"{prefix}_level_{sx}_{sy}", "cylinder", mat_brass,
                                        size=(0.008, 0.008, 0.005),
                                        location=(sx, sy, 0.013))
            objs.append(screw)
    return objs

def build_mirror_stand(prefix, collection, mat_brass, mat_chrome, center_z=0.075):
    """Builds the vertical chrome post, swivel bracket, and knurled clamp."""
    objs = []
    boss = kit.primitive_object(f"{prefix}_base_boss", "cylinder", mat_brass,
                                size=(0.024, 0.024, 0.008),
                                location=(0.0, 0.0, 0.016))
    objs.append(boss)

    post = kit.primitive_object(f"{prefix}_chrome_post", "cylinder", mat_chrome,
                                size=(0.008, 0.008, center_z - 0.020),
                                location=(0.0, 0.0, (0.016 + center_z - 0.020) * 0.5))
    objs.append(post)

    clamp = kit.primitive_object(f"{prefix}_swivel_bracket", "cube", mat_brass,
                                 size=(0.020, 0.014, 0.014),
                                 location=(0.0, 0.006, center_z - 0.026))
    screw = kit.primitive_object(f"{prefix}_locking_screw", "cylinder", mat_brass,
                                 size=(0.008, 0.008, 0.006),
                                 location=(0.013, 0.006, center_z - 0.026),
                                 rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.extend([clamp, screw])
    return objs

def build_convex_dish_mesh(name, mat_silver, mat_back, center_z=0.075):
    """Builds a high-reflectivity front-surface convex spherical dish with protective back shell."""
    r_max = 0.030
    R_c = 0.080   # Radius of curvature: f = R_c / 2 = 0.040m
    num_steps = 24
    t_dish = 0.002

    # Dish front curves outward towards -Y (bulging forward into object space)
    dish_front = []
    for i in range(num_steps + 1):
        r = r_max * (i / num_steps)
        # Saggita of convex mirror (center bulges forward at +sag in local Z)
        sag = math.sqrt(max(0.0, R_c**2 - r**2)) - math.sqrt(R_c**2 - r_max**2)
        dish_front.append((r, sag))

    dish_back = [(r, z - t_dish) for r, z in reversed(dish_front)]
    dish_profile = dish_front + dish_back

    dish_obj = kit.lathe_object(name, dish_profile, segments=48, material=mat_silver)
    # Rotate so bulge points towards -Y
    dish_obj.rotation_euler = (-math.pi / 2, 0.0, 0.0)
    dish_obj.location = (0.0, 0.0, center_z)
    return dish_obj

def build_convex_mirror_full(collection):
    """Collection 1: Real-world optical laboratory bench convex mirror stand."""
    prefix = "m_cvx_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_silver = kit.add_material(f"{prefix}_silver", COLOR_SILVER_MIRROR, metallic=0.98, roughness=0.012)
    mat_back   = kit.add_material(f"{prefix}_back", COLOR_BACK_SHELL, metallic=0.15, roughness=0.55)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_RING, metallic=0.92, roughness=0.25)
    mat_chrome = kit.add_machined_metal_material(f"{prefix}_chrome", COLOR_CHROME_POST, metallic=0.96, roughness=0.15)

    center_z = 0.075

    # 1. Optical Stand
    all_objs.extend(build_mirror_stand(prefix, collection, mat_brass, mat_chrome, center_z=center_z))

    # 2. Convex Mirror Dish
    dish = build_convex_dish_mesh(f"{prefix}_dish", mat_silver, mat_back, center_z=center_z)
    link_strictly(dish, collection)
    all_objs.append(dish)

    # 3. Brass Bezel Ring
    bezel_profile = [
        (0.0295, 0.002),
        (0.0330, 0.002),
        (0.0330, -0.008),
        (0.0295, -0.008),
        (0.0295, 0.002)
    ]
    bezel = kit.lathe_object(f"{prefix}_bezel", bezel_profile, segments=48, material=mat_brass)
    bezel.rotation_euler = (math.pi / 2, 0.0, 0.0)
    bezel.location = (0.0, 0.0, center_z)
    link_strictly(bezel, collection)
    all_objs.append(bezel)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_convex_mirror_section(collection):
    """Collection 2: Optical Ray Reflection, Virtual Focus F, Center of Curvature C, and Plaque."""
    prefix = "m_cvx_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_silver   = kit.add_material(f"{prefix}_silver", COLOR_SILVER_MIRROR, metallic=0.98, roughness=0.012)
    mat_back     = kit.add_material(f"{prefix}_back", COLOR_BACK_SHELL, metallic=0.15, roughness=0.55)
    mat_brass    = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS_RING, metallic=0.92, roughness=0.25)
    mat_chrome   = kit.add_machined_metal_material(f"{prefix}_chrome", COLOR_CHROME_POST, metallic=0.96, roughness=0.15)
    mat_ray      = create_emissive_mat(f"{prefix}_ray", COLOR_RAY_EMERALD, strength=14.0)
    mat_virt     = create_emissive_mat(f"{prefix}_virt", COLOR_RAY_VIRTUAL, strength=10.0)
    mat_axis     = kit.add_material(f"{prefix}_axis", COLOR_AXIS_LINE, metallic=0.15, roughness=0.45)
    mat_pin      = kit.add_machined_metal_material(f"{prefix}_pin", COLOR_FOCAL_PIN, metallic=0.90, roughness=0.25)
    mat_trim     = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_base     = kit.add_material(f"{prefix}_plaque_base", COLOR_PLINTH, metallic=0.15, roughness=0.45)

    center_z = 0.075

    # 1. Optical Stand & Mirror
    all_objs.extend(build_mirror_stand(prefix, collection, mat_brass, mat_chrome, center_z=center_z))

    dish = build_convex_dish_mesh(f"{prefix}_dish", mat_silver, mat_back, center_z=center_z)
    link_strictly(dish, collection)
    all_objs.append(dish)

    bezel_profile = [
        (0.0295, 0.002),
        (0.0330, 0.002),
        (0.0330, -0.008),
        (0.0295, -0.008),
        (0.0295, 0.002)
    ]
    bezel = kit.lathe_object(f"{prefix}_bezel", bezel_profile, segments=48, material=mat_brass)
    bezel.rotation_euler = (math.pi / 2, 0.0, 0.0)
    bezel.location = (0.0, 0.0, center_z)
    link_strictly(bezel, collection)
    all_objs.append(bezel)

    # 2. Principal Optical Axis along Y
    # Pole P is at (0, -0.006, center_z), Focus F is at y = +0.034 (behind mirror), Center C is at y = +0.074
    f_virt = 0.034
    c_virt = 0.074
    axis_line = create_cylinder_segment(f"{prefix}_axis", (0.0, -0.065, center_z), (0.0, 0.080, center_z), 0.0004, mat_axis, collection)
    if axis_line: all_objs.append(axis_line)

    # 3. Ray Optics: Parallel incident rays from -Y reflecting off convex surface (diverging)
    ray_offsets = [
        ( 0.018, 0.0),
        (-0.018, 0.0),
        (0.0,  0.016),
        (0.0, -0.016)
    ]
    y_start = -0.065

    for idx, (ox, oz) in enumerate(ray_offsets):
        # Surface point on convex dish (bulging towards -Y)
        r_sq = ox**2 + oz**2
        R_c = 0.080
        sag = math.sqrt(max(0.0, R_c**2 - r_sq)) - math.sqrt(R_c**2 - 0.030**2)
        y_surf = -sag
        p_surf = Vector((ox, y_surf, center_z + oz))

        # Incident parallel ray to surface
        r_inc = create_cylinder_segment(f"{prefix}_r_inc_{idx}", (ox, y_start, center_z + oz), (p_surf.x, p_surf.y, p_surf.z), 0.0006, mat_ray, collection)
        # Diverging reflected ray (appears to emanate from virtual focus F at (0, f_virt, center_z))
        p_focus = Vector((0.0, f_virt, center_z))
        dir_div = (p_surf - p_focus).normalized()
        p_div_end = p_surf + dir_div * 0.045
        r_ref = create_cylinder_segment(f"{prefix}_r_ref_{idx}", (p_surf.x, p_surf.y, p_surf.z), (p_div_end.x, p_div_end.y, p_div_end.z), 0.0006, mat_ray, collection)
        # Virtual backward extension behind mirror to focus F
        r_virt = create_cylinder_segment(f"{prefix}_r_virt_{idx}", (p_surf.x, p_surf.y, p_surf.z), (0.0, f_virt, center_z), 0.0004, mat_virt, collection)
        for r in [r_inc, r_ref, r_virt]:
            if r: all_objs.append(r)

    # 4. Focal Point Pin Indicators (Pole P at 0, virtual Focus F at +f, virtual Center C at +2f)
    pin_P = kit.primitive_object(f"{prefix}_pin_P", "cylinder", mat_pin, size=(0.002, 0.002, 0.008), location=(0.0, 0.0, center_z - 0.004))
    pin_F = kit.primitive_object(f"{prefix}_pin_F", "cylinder", mat_pin, size=(0.0025, 0.0025, 0.010), location=(0.0, f_virt, center_z - 0.005))
    all_objs.extend([pin_P, pin_F])

    # 5. Dimension Caliper Line for Virtual Focal Length f
    dim_x = -0.024
    cal_line = create_cylinder_segment(f"{prefix}_cal_line", (dim_x, 0.0, center_z), (dim_x, f_virt, center_z), 0.00045, mat_trim, collection)
    cal_t1   = create_cylinder_segment(f"{prefix}_cal_t1", (dim_x - 0.002, 0.0, center_z), (dim_x + 0.002, 0.0, center_z), 0.00045, mat_trim, collection)
    cal_t2   = create_cylinder_segment(f"{prefix}_cal_t2", (dim_x - 0.002, f_virt, center_z), (dim_x + 0.002, f_virt, center_z), 0.00045, mat_trim, collection)
    badge_f  = kit.primitive_object(f"{prefix}_dim_badge", "cube", mat_trim, size=(0.002, 0.005, 0.003), location=(dim_x, f_virt * 0.5, center_z + 0.002))
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
    # Title bar: CONVEX MIRROR (DIVERGING)
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: 1/v + 1/u = 1/f (f is virtual)
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_virt,
                                size=(0.095, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: Rear-View Mirror
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
    cam_data = bpy.data.cameras.new("Mirror_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Mirror_Camera", cam_data)
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

    full_col = bpy.data.collections.new("Convex_Mirror_Full")
    sec_col  = bpy.data.collections.new("Convex_Mirror_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_convex_mirror_full(full_col)
    build_convex_mirror_section(sec_col)
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

    # Render Preview 1: Convex_Mirror_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Convex_Mirror_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== CONVEX MIRROR BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()