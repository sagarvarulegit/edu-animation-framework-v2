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


def add_material(name, color, metallic=0.0, roughness=0.5, clearcoat=0.0, clearcoat_roughness=0.1, transmission=0.0, ior=1.0, subsurface_weight=0.0):
    """Creates a physically accurate PBR material with clearcoat, transmission, and SSS support."""
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = clearcoat
    if "Clearcoat Roughness" in bsdf.inputs:
        bsdf.inputs["Clearcoat Roughness"].default_value = clearcoat_roughness
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if "IOR" in bsdf.inputs and transmission > 0.0:
        bsdf.inputs["IOR"].default_value = ior
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface_weight
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
    if tokens is not None:
        raw = tokens.TOKENS.get("materials", {}).get(token_material_key, {})
        if "subsurfaceWeight" in raw and "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = raw["subsurfaceWeight"]
        if "subsurfaceRadius" in raw and "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = tuple(raw["subsurfaceRadius"])
        if "subsurfaceScale" in raw and "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = raw["subsurfaceScale"]
    return material


def add_glass_material(name, tint=None, ior=None, roughness=None, transmission=0.98, clearcoat=0.2):
    """Creates a physically accurate borosilicate / optical glass shader with proper transmission and clearcoat."""
    if tokens is not None and "glass_borosilicate" in tokens.MATERIALS:
        cfg = tokens.get_material_config("glass_borosilicate")
        actual_tint = cfg["base_color"][:3] if tint is None else tint
        actual_ior = cfg.get("ior", 1.52) if ior is None else ior
        actual_roughness = cfg.get("roughness", 0.01) if roughness is None else roughness
        actual_transmission = cfg.get("transmission", 0.98) if transmission is None else transmission
    else:
        actual_tint = (0.95, 0.98, 1.0) if tint is None else tint
        actual_ior = 1.52 if ior is None else ior
        actual_roughness = 0.01 if roughness is None else roughness
        actual_transmission = 0.98 if transmission is None else transmission

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*actual_tint, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = actual_roughness
    bsdf.inputs["IOR"].default_value = actual_ior
    bsdf.inputs["Transmission Weight"].default_value = actual_transmission
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = 0.5
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = clearcoat
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


def add_tissue_material(name, base_color=(0.85, 0.25, 0.25, 1.0), roughness=0.35,
                        subsurface_weight=0.3, subsurface_radius=(1.0, 0.2, 0.1), subsurface_scale=0.02):
    """
    Creates a Principled BSDF material configured for biological tissue with Subsurface Scattering
    compatible with Blender 4.2 LTS sockets.
    """
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]

    if isinstance(base_color, str) and tokens is not None:
        full_color = tokens.hex_to_linear(base_color)
    elif len(base_color) == 3:
        full_color = (*base_color, 1.0)
    else:
        full_color = tuple(base_color)

    bsdf.inputs["Base Color"].default_value = full_color
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = roughness

    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface_weight
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = subsurface_weight

    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = tuple(subsurface_radius)

    if "Subsurface Scale" in bsdf.inputs:
        bsdf.inputs["Subsurface Scale"].default_value = subsurface_scale

    if "Subsurface IOR" in bsdf.inputs:
        bsdf.inputs["Subsurface IOR"].default_value = 1.40

    return material


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
        bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
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
    if kind == "cube":
        obj.scale = size
    elif kind == "uv_sphere":
        if len(size) >= 3 and size[0] > 0:
            obj.scale = (1.0, size[1] / size[0], size[2] / size[0])
        else:
            obj.scale = (1.0, 1.0, 1.0)
    else:
        obj.scale = (1.0, 1.0, 1.0)
    obj.data.materials.append(material)
    return obj


def create_smooth_tube(name, points, radius=0.003, resolution=16, material=None, cap_ends=True):
    """
    Generates a smooth 3D bevel tube from 3D spline control points.
    If cap_ends is True, caps endpoints with manifold geometry to ensure clean closed meshes.
    """
    if len(points) < 2:
        raise ValueError("create_smooth_tube requires at least 2 points")

    curve_data = bpy.data.curves.new(name=f"{name}-curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = max(16, resolution)
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = max(2, resolution // 4)
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = Vector(pt) if not isinstance(pt, Vector) else pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)

    # Convert curve to mesh deterministically
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    if prev_active and prev_active.name in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = prev_active

    mesh = obj.data

    if cap_ends:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        boundary_edges = [e for e in bm.edges if e.is_boundary]
        if boundary_edges:
            bmesh.ops.holes_fill(bm, edges=boundary_edges, sides=len(boundary_edges))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    if material is not None:
        obj.data.materials.append(material)

    return obj


smooth_tube_object = create_smooth_tube


def text_mesh_object(name, text, material=None, size=0.012, extrude=0.0006,
                     location=(0.0, 0.0, 0.0), rotation_euler=(0.0, 0.0, 0.0)):
    """
    Creates 3D typographic text converted to a clean polygon mesh suitable for glTF export.
    """
    curve = bpy.data.curves.new(f'{name}-curve', type='FONT')
    curve.body = text
    curve.size = size
    curve.extrude = extrude
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'

    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation_euler

    # Convert to MESH deterministically
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    if prev_active and prev_active.name in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = prev_active

    # Ensure welded, watertight manifold topology
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    if material is not None:
        obj.data.materials.append(material)

    return obj


def _resolve_env_path():
    """Find an HDRI environment map, preferring project-local assets."""
    import os
    candidates = [
        str(Path(os.environ.get("BLENDER_USER_SCRIPTS", "")) / "edu_assets" / "envs" / "studio.exr"),
        str(Path(__file__).resolve().parent / "envs" / "studio.exr"),
        str(Path(__file__).resolve().parent / "envs" / "studio_1k.hdr"),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return Path(candidate)
    return None


def setup_world_and_light():
    world = bpy.data.worlds.new("edu_world")
    world.use_nodes = True
    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Environment node setup supporting HDRI if available, with fallback to studio gradient
    bg_node = nodes.new(type="ShaderNodeBackground")
    bg_node.inputs["Color"].default_value = (0.015, 0.020, 0.030, 1.0)
    if "Roughness" in bg_node.inputs:
        bg_node.inputs["Roughness"].default_value = 0.0
    bg_node.inputs["Strength"].default_value = 0.5  # increased from 0.20 for better base illumination

    output_node = nodes.new(type="ShaderNodeOutputWorld")
    links.new(bg_node.outputs["Background"], output_node.inputs["Surface"])

    # Try to load an HDRI environment map for realistic reflections and ambient lighting
    env_tex = None
    hdri_path = _resolve_env_path()
    if hdri_path is not None:
        env_tex = nodes.new(type="ShaderNodeTexEnvironment")
        env_tex.image = bpy.data.images.load(str(hdri_path))
        links.new(env_tex.outputs["Color"], bg_node.inputs["Color"])
        env_tex.location = (-300, 0)
        bg_node.location = (0, 0)
        output_node.location = (300, 0)
    else:
        # Fallback: procedural sky gradient with warmer tone
        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        tex_coord.location = (-500, 0)
        mapping = nodes.new(type="ShaderNodeMapping")
        mapping.location = (-300, 0)
        mapping.inputs["Rotation"].default_value = (0.0, 0.0, 0.5)
        links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])

        gradient = nodes.new(type="ShaderNodeTexGradient")
        gradient.gradient_type = "LINEAR"
        gradient.location = (-100, 0)
        links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])

        mix = nodes.new(type="ShaderNodeMixRGB")
        mix.blend_type = "MIX"
        mix.inputs["Color1"].default_value = (0.02, 0.03, 0.05, 1.0)
        mix.inputs["Color2"].default_value = (0.15, 0.22, 0.35, 1.0)
        mix.inputs["Fac"].default_value = 0.0
        links.new(gradient.outputs["Fac"], mix.inputs["Fac"])
        links.new(mix.outputs["Color"], bg_node.inputs["Color"])
        tex_coord.location = (-700, 0)
        gradient.location = (-500, 0)
        mix.location = (-300, 0)
        bg_node.location = (0, 0)
        output_node.location = (300, 0)

    bpy.context.scene.world = world

    # Key light: Warmer, stronger directional key light
    key_data = bpy.data.lights.new("edu_key_light", type="AREA")
    key_data.energy = 1500.0
    key_data.color = (1.0, 0.96, 0.90)
    key_data.size = 0.5
    key = bpy.data.objects.new("edu_key_light", key_data)
    bpy.context.collection.objects.link(key)
    key.location = Vector((1.0, -1.2, 1.5))
    key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat("-Z", "Y").to_euler()

    # Rim light: cool back-rim for separation
    rim_data = bpy.data.lights.new("edu_rim_light", type="AREA")
    rim_data.energy = 750.0
    rim_data.color = (0.92, 0.96, 1.0)
    rim_data.size = 0.6
    rim = bpy.data.objects.new("edu_rim_light", rim_data)
    bpy.context.collection.objects.link(rim)
    rim.location = Vector((-0.5, -1.8, 0.9))

    rim.rotation_euler = (Vector((0, 0, 0)) - rim.location).to_track_quat("Z", "Y").to_euler()
    rim.rotation_euler.z += 0.5

    # Fill light: Soft area fill
    fill_data = bpy.data.lights.new("edu_fill_light", type="AREA")
    fill_data.energy = 600.0
    fill_data.color = (0.90, 0.94, 1.0)
    fill_data.size = 0.8
    fill = bpy.data.objects.new("edu_fill_light", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = Vector((0.4, -0.3, 0.6))
    fill.rotation_euler = (Vector((0, 0, 0)) - fill.location).to_track_quat("Z", "Y").to_euler()
    fill.rotation_euler.z += 1.0


def frame_camera(objects, lens=50.0):
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
    cam_data.sensor_width = 32.0  # APS-C sensor
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


def configure_render(width=1280, height=720, samples=24):
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
