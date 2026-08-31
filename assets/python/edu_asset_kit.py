import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector, Matrix

try:
    import edu_design_tokens as tokens
except ImportError:
    tokens = None


def output_dir(default):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    path = Path(args.out) if args.out else Path(default)
    path.mkdir(parents=True, exist_ok=True)
    return path


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def add_material(name, color, metallic=0.0, roughness=0.5):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def add_material_from_token(name, token_material_key):
    """Creates a material using standardized PBR tokens from visual/design-tokens.json."""
    if tokens is None:
        return add_material(name, (0.8, 0.8, 0.8), 0.0, 0.5)
    cfg = tokens.get_material_config(token_material_key)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = cfg["base_color"]
    bsdf.inputs["Metallic"].default_value = cfg["metallic"]
    bsdf.inputs["Roughness"].default_value = cfg["roughness"]
    if "transmission" in cfg and "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = cfg["transmission"]
    if "ior" in cfg and "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = cfg["ior"]
    if "emission_color" in cfg and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = cfg["emission_color"]
        bsdf.inputs["Emission Strength"].default_value = cfg["emission_strength"]
    return material


def add_glass_material(name, tint=None, ior=None, roughness=None):
    """Creates a physically accurate borosilicate / optical glass shader from design tokens."""
    if tokens is not None and "glass_borosilicate" in tokens.MATERIALS:
        cfg = tokens.get_material_config("glass_borosilicate")
        actual_tint = cfg["base_color"][:3] if tint is None else tint
        actual_ior = cfg["ior"] if ior is None else ior
        actual_roughness = cfg["roughness"] if roughness is None else roughness
    else:
        actual_tint = (0.95, 0.98, 1.0) if tint is None else tint
        actual_ior = 1.52 if ior is None else ior
        actual_roughness = 0.02 if roughness is None else roughness

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*actual_tint, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = actual_roughness
    bsdf.inputs["IOR"].default_value = actual_ior
    bsdf.inputs["Transmission Weight"].default_value = 0.96
    return material


def add_machined_metal_material(name, color=None, metallic=None, roughness=None):
    """Creates a realistic machined/turned metal (steel/aluminum) material from design tokens."""
    if tokens is not None and "metal_machined_steel" in tokens.MATERIALS:
        cfg = tokens.get_material_config("metal_machined_steel")
        actual_color = cfg["base_color"][:3] if color is None else color
        actual_metallic = cfg["metallic"] if metallic is None else metallic
        actual_roughness = cfg["roughness"] if roughness is None else roughness
    else:
        actual_color = (0.85, 0.85, 0.88) if color is None else color
        actual_metallic = 0.95 if metallic is None else metallic
        actual_roughness = 0.25 if roughness is None else roughness

    return add_material(name, actual_color, metallic=actual_metallic, roughness=actual_roughness)


def lathe_object(name, profile_points, segments=64, material=None, location=(0.0, 0.0, 0.0), rotation_euler=(0.0, 0.0, 0.0)):
    """
    Revolves a 2D profile [(radius, z), ...] around the Z-axis 360 degrees.
    Produces high-fidelity glassware, turned metal collars, burners, and bulbs with quad topology.
    """
    bm = bmesh.new()
    num_pts = len(profile_points)
    
    # Generate vertices along radial slices
    ring_verts = []
    for s in range(segments):
        theta = 2.0 * math.pi * s / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        slice_verts = []
        for r, z in profile_points:
            x = r * cos_t
            y = r * sin_t
            v = bm.verts.new((x, y, z))
            slice_verts.append(v)
        ring_verts.append(slice_verts)

    # Build quad faces between adjacent radial slices
    for s in range(segments):
        next_s = (s + 1) % segments
        for p in range(num_pts - 1):
            v1 = ring_verts[s][p]
            v2 = ring_verts[next_s][p]
            v3 = ring_verts[next_s][p + 1]
            v4 = ring_verts[s][p + 1]
            
            # Check for apex/center point collapsing (radius = 0)
            if profile_points[p][0] == 0.0:
                bm.faces.new([v1, v4, v3])
            elif profile_points[p + 1][0] == 0.0:
                bm.faces.new([v1, v2, v3])
            else:
                bm.faces.new([v1, v2, v3, v4])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    # Enable smooth shading across all polygons
    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation_euler
    
    if material is not None:
        obj.data.materials.append(material)
        
    return obj


def mesh_object(name, verts, faces, material=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj


def primitive_object(name, kind, material, size=(1.0, 1.0, 1.0), location=(0.0, 0.0, 0.0),
                     rotation_euler=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    if kind == "cube":
        bmesh.ops.create_cube(bm, size=1.0)
    elif kind == "cylinder":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=64,
                              radius1=size[0] / 2, radius2=size[0] / 2, depth=size[2])
    elif kind == "cone":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=64,
                              radius1=size[0] / 2, radius2=size[1] / 2, depth=size[2])
    elif kind == "uv_sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=size[0] / 2)
    else:
        raise ValueError(f"unknown primitive kind: {kind}")
        
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    if kind in ["cylinder", "cone", "uv_sphere"]:
        for poly in mesh.polygons:
            poly.use_smooth = True
            
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation_euler
    obj.scale = (1.0, 1.0, 1.0) if kind != "cube" else size
    obj.data.materials.append(material)
    return obj


def setup_world_and_light():
    world = bpy.data.worlds.new("edu_world")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    # Deep dark slate studio background (#0a0f1d) for pristine visual contrast
    background.inputs[0].default_value = (0.015, 0.020, 0.030, 1.0)
    background.inputs[1].default_value = 0.20
    bpy.context.scene.world = world

    # Key light: Focused soft studio key light
    sun_data = bpy.data.lights.new("edu_key_light", type="SUN")
    sun_data.energy = 2.4
    sun_data.color = (1.0, 0.97, 0.92)
    sun = bpy.data.objects.new("edu_key_light", sun_data)
    bpy.context.collection.objects.link(sun)
    direction = Vector((-0.45, -0.65, -0.90)).normalized()
    sun.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Rim light: Crisp cool contour rim light for edge definition on glassware and metals
    rim_data = bpy.data.lights.new("edu_rim_light", type="SUN")
    rim_data.energy = 2.0
    rim_data.color = (0.75, 0.88, 1.0)
    rim = bpy.data.objects.new("edu_rim_light", rim_data)
    bpy.context.collection.objects.link(rim)
    rim_direction = Vector((0.75, 0.60, -0.60)).normalized()
    rim.rotation_euler = rim_direction.to_track_quat("-Z", "Y").to_euler()

    # Subtle soft fill light
    fill_data = bpy.data.lights.new("edu_fill_light", type="SUN")
    fill_data.energy = 0.8
    fill_data.color = (0.90, 0.92, 0.98)
    fill = bpy.data.objects.new("edu_fill_light", fill_data)
    bpy.context.collection.objects.link(fill)
    fill_direction = Vector((0.30, -0.80, -0.40)).normalized()
    fill.rotation_euler = fill_direction.to_track_quat("-Z", "Y").to_euler()


def frame_camera(objects, lens=55.0):
    bpy.context.view_layer.update()
    points = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    center = sum(points, Vector()) / len(points)
    radius = max((p - center).length for p in points)
    radius = max(radius, 0.02)

    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = lens
    scene = bpy.context.scene
    sensor_w = cam_data.sensor_width
    sensor_h = sensor_w * scene.render.resolution_y / scene.render.resolution_x
    half_fov = min(math.atan(sensor_w / (2.0 * lens)),
                   math.atan(sensor_h / (2.0 * lens)))
    distance = max(radius / math.sin(half_fov) * 1.22, 0.05)
    cam_data.clip_end = distance * 20.0 + 10.0

    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    view_direction = Vector((1.1, -1.4, 0.75)).normalized()
    cam.location = center + view_direction * distance
    cam.rotation_euler = (-view_direction).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def configure_render(width=1280, height=720, samples=48):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB",
                              export_cameras=False, export_lights=False,
                              export_apply=True)


def render_preview(path):
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
