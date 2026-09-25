"""
build_plane_mirror.py — Laboratory Plane Mirror & Specular Reflection Laws
NCERT Class 10 Science Chapter 10 (Light — Reflection and Refraction) Section 10.1.

Dual Collections:
  1. Plane_Mirror_Full:
     - Real-world optical laboratory bench swivel plane mirror stand on studio slate plinth.
     - Front-surface specular silver mirror pane held in beveled frame with protective backing.
     - Side swivel trunnion pivots with knurled brass locking knobs, upright support stanchions, and leveling screws.

  2. Plane_Mirror_Section (Laws of Reflection & Virtual Image Geometry):
     - Ray optics demonstration with illuminated emerald laser beams:
       * Normal line NN' perpendicular to mirror at point of incidence O.
       * Incident laser ray at angle of incidence angle i.
       * Reflected laser ray at angle of reflection angle r = angle i.
       * Virtual dashed extension rays behind mirror meeting at virtual image point.
       * Object pin (do) in front and Virtual Image pin (di = do) behind mirror showing lateral inversion.
       * Forward-tilted educational plaque on brass stanchions:
         - "PLANE MIRROR (SPECULAR REFLECTION)"
         - "Laws of Reflection: angle i = angle r (Coplanar Rays)"
         - "Image: Virtual, Erect, Same Size (di = do), Laterally Inverted"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'plane-mirror'

# Calibrated Laboratory Palette
COLOR_SILVER_MIRROR = (0.95, 0.96, 0.98)     # High-reflectivity silver mirror surface
COLOR_FRAME_BRASS   = (0.86, 0.70, 0.28)     # Machined brass frame & knurled swivel knobs
COLOR_BACK_SHELL    = (0.12, 0.12, 0.14)     # Protective black bakelite/metal back shell
COLOR_STAND_POST    = (0.90, 0.92, 0.95)     # Polished stainless steel / chrome support rod
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate base pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Gold trim and calibration badges
COLOR_RAY_EMERALD   = (0.10, 0.95, 0.45)     # Glowing emerald 532nm laser ray beam
COLOR_RAY_VIRTUAL   = (0.25, 0.75, 1.00)     # Cyan dashed virtual backward ray extension
COLOR_NORMAL_LINE   = (1.00, 0.85, 0.20)     # Normal reference line NN'
COLOR_OBJECT_PIN    = (0.92, 0.18, 0.18)     # Crimson object pin
COLOR_IMAGE_PIN     = (0.20, 0.50, 0.95)     # Cobalt blue virtual image pin

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
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_level_brass", COLOR_FRAME_BRASS, metallic=0.92, roughness=0.25)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                  size=(0.14, 0.10, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.142, 0.102, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)

    # 4 brass leveling screws
    for sx in [-0.058, 0.058]:
        for sy in [-0.038, 0.038]:
            screw = kit.primitive_object(f"{prefix}_level_{sx}_{sy}", "cylinder", mat_brass,
                                        size=(0.008, 0.008, 0.005),
                                        location=(sx, sy, 0.013))
            objs.append(screw)
    return objs

def build_mirror_frame_assembly(prefix, collection, mat_silver, mat_frame, mat_back, center_z=0.075):
    """Builds the rectangular plane mirror pane, protective back, and brass surround frame."""
    objs = []
    w = 0.065
    h = 0.075
    t_glass = 0.003
    t_back = 0.003
    fw = 0.004

    # Front reflective silver mirror surface (facing -Y)
    mirror = kit.primitive_object(f"{prefix}_mirror_pane", "cube", mat_silver,
                                 size=(w, t_glass, h),
                                 location=(0.0, -0.0015, center_z))
    objs.append(mirror)

    # Protective back shell (+Y)
    back = kit.primitive_object(f"{prefix}_backing", "cube", mat_back,
                               size=(w + 2 * fw, t_back, h + 2 * fw),
                               location=(0.0, 0.0015, center_z))
    objs.append(back)

    # Beveled brass surround frame
    f_top = kit.primitive_object(f"{prefix}_frame_top", "cube", mat_frame,
                                size=(w + 2 * fw, t_glass + t_back, fw),
                                location=(0.0, 0.0, center_z + h * 0.5 + fw * 0.5))
    f_bot = kit.primitive_object(f"{prefix}_frame_bot", "cube", mat_frame,
                                size=(w + 2 * fw, t_glass + t_back, fw),
                                location=(0.0, 0.0, center_z - h * 0.5 - fw * 0.5))
    f_l = kit.primitive_object(f"{prefix}_frame_l", "cube", mat_frame,
                              size=(fw, t_glass + t_back, h),
                              location=(-w * 0.5 - fw * 0.5, 0.0, center_z))
    f_r = kit.primitive_object(f"{prefix}_frame_r", "cube", mat_frame,
                              size=(fw, t_glass + t_back, h),
                              location=( w * 0.5 + fw * 0.5, 0.0, center_z))
    objs.extend([f_top, f_bot, f_l, f_r])
    return objs

def build_swivel_stand(prefix, collection, mat_brass, mat_post, center_z=0.075):
    """Builds the twin side vertical stanchions, pivot trunnions and knurled locking knobs."""
    objs = []
    w_span = 0.076
    # Left and right vertical support stanchions on plinth
    for sign, name in [(-1, "l"), (1, "r")]:
        post = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_post,
                                    size=(0.007, 0.007, center_z - 0.012),
                                    location=(sign * (w_span * 0.5 + 0.006), 0.0, (0.012 + center_z) * 0.5))
        # Pivot trunnion pin through frame
        stud = kit.primitive_object(f"{prefix}_trunnion_{name}", "cylinder", mat_brass,
                                    size=(0.005, 0.005, 0.012),
                                    location=(sign * (w_span * 0.5 + 0.004), 0.0, center_z),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        # Knurled tightening knob
        knob = kit.primitive_object(f"{prefix}_knob_{name}", "cylinder", mat_brass,
                                    size=(0.010, 0.010, 0.006),
                                    location=(sign * (w_span * 0.5 + 0.010), 0.0, center_z),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        objs.extend([post, stud, knob])
    return objs

def build_plane_mirror_full(collection):
    """Collection 1: Real-world optical laboratory bench swivel plane mirror stand."""
    prefix = "pm_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_silver = kit.add_material(f"{prefix}_silver", COLOR_SILVER_MIRROR, metallic=0.98, roughness=0.012)
    mat_frame  = kit.add_machined_metal_material(f"{prefix}_frame", COLOR_FRAME_BRASS, metallic=0.92, roughness=0.25)
    mat_back   = kit.add_material(f"{prefix}_back", COLOR_BACK_SHELL, metallic=0.15, roughness=0.55)
    mat_post   = kit.add_machined_metal_material(f"{prefix}_post", COLOR_STAND_POST, metallic=0.96, roughness=0.15)

    center_z = 0.075

    all_objs.extend(build_swivel_stand(prefix, collection, mat_frame, mat_post, center_z=center_z))
    all_objs.extend(build_mirror_frame_assembly(prefix, collection, mat_silver, mat_frame, mat_back, center_z=center_z))

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_plane_mirror_section(collection):
    """Collection 2: Laws of Reflection (angle i = angle r), Normal NN', and Virtual Image."""
    prefix = "pm_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_silver = kit.add_material(f"{prefix}_silver", COLOR_SILVER_MIRROR, metallic=0.98, roughness=0.012)
    mat_frame  = kit.add_machined_metal_material(f"{prefix}_frame", COLOR_FRAME_BRASS, metallic=0.92, roughness=0.25)
    mat_back   = kit.add_material(f"{prefix}_back", COLOR_BACK_SHELL, metallic=0.15, roughness=0.55)
    mat_post   = kit.add_machined_metal_material(f"{prefix}_post", COLOR_STAND_POST, metallic=0.96, roughness=0.15)
    mat_ray    = create_emissive_mat(f"{prefix}_ray", COLOR_RAY_EMERALD, strength=14.0)
    mat_virt   = create_emissive_mat(f"{prefix}_virt", COLOR_RAY_VIRTUAL, strength=10.0)
    mat_norm   = kit.add_material(f"{prefix}_norm", COLOR_NORMAL_LINE, metallic=0.10, roughness=0.40)
    mat_obj_pin= kit.add_material(f"{prefix}_obj_pin", COLOR_OBJECT_PIN, metallic=0.35, roughness=0.30)
    mat_img_pin= kit.add_material(f"{prefix}_img_pin", COLOR_IMAGE_PIN, metallic=0.35, roughness=0.30)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_base   = kit.add_material(f"{prefix}_plaque_base", COLOR_PLINTH, metallic=0.15, roughness=0.45)

    center_z = 0.075

    all_objs.extend(build_swivel_stand(prefix, collection, mat_frame, mat_post, center_z=center_z))
    all_objs.extend(build_mirror_frame_assembly(prefix, collection, mat_silver, mat_frame, mat_back, center_z=center_z))

    # 1. Normal Line NN' perpendicular to mirror face at center (0, -0.003, center_z)
    norm_line = create_cylinder_segment(f"{prefix}_normal", (0.0, -0.055, center_z), (0.0, 0.040, center_z), 0.00045, mat_norm, collection)
    if norm_line: all_objs.append(norm_line)

    # 2. Incident & Reflected Rays (at angle of incidence theta = 35 deg)
    theta = math.radians(35.0)
    ray_len = 0.055
    y_surf = -0.003
    p_inc = Vector((-ray_len * math.sin(theta), y_surf - ray_len * math.cos(theta), center_z))
    p_ref = Vector(( ray_len * math.sin(theta), y_surf - ray_len * math.cos(theta), center_z))
    p_orig = Vector((0.0, y_surf, center_z))

    # Incident ray (from left object space to mirror center)
    r_inc = create_cylinder_segment(f"{prefix}_r_inc", (p_inc.x, p_inc.y, p_inc.z), (p_orig.x, p_orig.y, p_orig.z), 0.0007, mat_ray, collection)
    # Reflected ray (from mirror center to right observer space)
    r_ref = create_cylinder_segment(f"{prefix}_r_ref", (p_orig.x, p_orig.y, p_orig.z), (p_ref.x, p_ref.y, p_ref.z), 0.0007, mat_ray, collection)
    # Virtual backward ray extension behind mirror face (+Y)
    p_virt = Vector((-ray_len * math.sin(theta), y_surf + ray_len * math.cos(theta), center_z))
    r_virt = create_cylinder_segment(f"{prefix}_r_virt", (p_orig.x, p_orig.y, p_orig.z), (p_virt.x, p_virt.y, p_virt.z), 0.00045, mat_virt, collection)
    all_objs.extend([r_inc, r_ref, r_virt])

    # 3. Object Pin & Virtual Image Pin
    # Real object pin at (-0.025, -0.035, center_z)
    obj_pin = kit.primitive_object(f"{prefix}_obj_pin", "cylinder", mat_obj_pin,
                                  size=(0.003, 0.003, 0.016),
                                  location=(-0.025, -0.035, center_z - 0.008))
    # Virtual image pin behind mirror at (-0.025, +0.035, center_z)
    img_pin = kit.primitive_object(f"{prefix}_img_pin", "cylinder", mat_img_pin,
                                  size=(0.003, 0.003, 0.016),
                                  location=(-0.025,  0.035, center_z - 0.008))
    all_objs.extend([obj_pin, img_pin])

    # 4. Educational Plaque Mounted on Brass Stanchions
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
        leg = kit.primitive_object(f"{prefix}_plaque_leg_{'l' if side < 0 else 'r'}", "cylinder", mat_frame,
                                  size=(0.003, 0.003, 0.010),
                                  location=(side, plaque_y + 0.006, 0.008))
        all_objs.append(leg)

    # Embossed Formula & Info Bars on Plaque
    front_offset = 0.0018
    # Title bar: PLANE MIRROR (REFLECTION)
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: angle i = angle r
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_ray,
                                size=(0.095, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: di = do (Virtual, Erect, Lateral Inversion)
    l_pos3 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, -0.006))
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_frame,
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

    full_col = bpy.data.collections.new("Plane_Mirror_Full")
    sec_col  = bpy.data.collections.new("Plane_Mirror_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_plane_mirror_full(full_col)
    build_plane_mirror_section(sec_col)
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

    # Render Preview 1: Plane_Mirror_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Plane_Mirror_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== PLANE MIRROR BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
