import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


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


def mesh_object(name, verts, faces, material=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
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
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=48,
                              radius1=size[0] / 2, radius2=size[0] / 2, depth=size[2])
    elif kind == "cone":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=48,
                              radius1=size[0] / 2, radius2=size[1] / 2, depth=size[2])
    else:
        raise ValueError(f"unknown primitive kind: {kind}")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
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
    background.inputs[0].default_value = (0.92, 0.93, 0.95, 1.0)
    background.inputs[1].default_value = 0.55
    bpy.context.scene.world = world

    sun_data = bpy.data.lights.new("edu_key_light", type="SUN")
    sun_data.energy = 3.5
    sun = bpy.data.objects.new("edu_key_light", sun_data)
    bpy.context.collection.objects.link(sun)
    direction = Vector((-0.45, -0.65, -1.0)).normalized()
    sun.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    fill_data = bpy.data.lights.new("edu_fill_light", type="SUN")
    fill_data.energy = 1.2
    fill = bpy.data.objects.new("edu_fill_light", fill_data)
    bpy.context.collection.objects.link(fill)
    fill_direction = Vector((0.7, 0.5, -0.8)).normalized()
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
    distance = max(radius / math.sin(half_fov) * 1.15, 0.05)
    cam_data.clip_end = distance * 20.0 + 10.0

    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    view_direction = Vector((1.0, -1.35, 0.72)).normalized()
    cam.location = center + view_direction * distance
    cam.rotation_euler = (-view_direction).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def configure_render(width=1280, height=720, samples=64):
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
