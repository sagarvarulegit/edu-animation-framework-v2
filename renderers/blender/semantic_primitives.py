import bpy
from mathutils import Vector

import edu_asset_kit as kit

LOOKS = {
    "magnesium-oxide": {"color": (0.93, 0.93, 0.91), "metallic": 0.0, "roughness": 0.95},
}


def _fcurves_for(anim_data, data_path):
    action = anim_data.action
    if action is None:
        return []
    try:
        return action.fcurves
    except AttributeError:
        pass
    slot = anim_data.action_slot
    for layer in action.layers:
        for strip in layer.strips:
            bag = strip.channelbag(slot)
            if bag is not None and bag.fcurves.find(data_path) is not None:
                return bag.fcurves
    return []


def _key_easing(obj, data_path, index, frame, easing):
    fcurves = _fcurves_for(obj.animation_data, data_path)
    fcurve = fcurves.find(data_path, index=index)
    if fcurve is None:
        return
    for point in fcurve.keyframe_points:
        if round(point.co.x) == frame:
            point.interpolation = "BEZIER"
            point.easing = easing


def appear(target, start, duration, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    target.scale = (0.0001, 0.0001, 0.0001)
    target.keyframe_insert("scale", frame=f0)
    target.scale = (1.0, 1.0, 1.0)
    target.keyframe_insert("scale", frame=f1)
    for i in range(3):
            _key_easing(target, "scale", i, f0, "EASE_OUT")


def disappear(target, start, duration, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    target.scale = (1.0, 1.0, 1.0)
    target.keyframe_insert("scale", frame=f0)
    target.scale = (0.0001, 0.0001, 0.0001)
    target.keyframe_insert("scale", frame=f1)
    for i in range(3):
        _key_easing(target, "scale", i, f0, "EASE_IN")


def camera_move(cam_obj, cam_data, from_shot, to_shot, start, duration, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    pose_keys = [(f0, from_shot), (f1, to_shot)]
    for frame, shot in pose_keys:
        cam_obj.location = Vector(shot["position"])
        cam_obj.keyframe_insert("location", frame=frame)
        direction = Vector(shot["target"]) - Vector(shot["position"])
        cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        cam_obj.keyframe_insert("rotation_euler", frame=frame)
        cam_data.lens = shot.get("lens", 50.0)
        cam_data.keyframe_insert("lens", frame=frame)
    for i in range(3):
        _key_easing(cam_obj, "location", i, f0, "EASE_IN_OUT")
        _key_easing(cam_obj, "rotation_euler", i, f0, "EASE_IN_OUT")


def show_label(text, location, end, cam, name="edu-label"):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.size = 0.014
    curve.align_x = "CENTER"
    material = bpy.data.materials.new(f"{name}-ink")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Emission Color"].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = Vector(location)
    track = obj.constraints.new("TRACK_TO")
    track.target = cam
    track.track_axis = "TRACK_Z"
    track.up_axis = "UP_Y"
    return obj


def show_equation(text, location, cam, name, size=0.026):
    obj = show_label(text, location, 0, cam, name=f"equation-{name}")
    obj.data.size = size
    obj.data.extrude = 0.0003
    return obj


def show_molecule(model, name, position):
    """Create a labeled-by-colour conceptual molecular model, never a scale claim."""
    parent = bpy.data.objects.new(f"molecule-{name}", None)
    bpy.context.collection.objects.link(parent)
    parent.location = Vector(position)
    magnesium = kit.add_material(f"molecule-{name}-magnesium", (0.22, 0.58, 0.38), 0.15, 0.32)
    oxygen = kit.add_material(f"molecule-{name}-oxygen", (0.85, 0.12, 0.12), 0.05, 0.28)
    bond = kit.add_material(f"molecule-{name}-bond", (0.32, 0.35, 0.40), 0.7, 0.25)

    def sphere(part, material, location, diameter=0.025):
        obj = kit.primitive_object(f"{name}-{part}", "uv_sphere", material, size=(diameter, diameter, diameter), location=location)
        obj.parent = parent
        return obj

    def connector(part, a, b):
        start, end = Vector(a), Vector(b)
        vector = end - start
        obj = kit.primitive_object(f"{name}-{part}", "cylinder", bond, size=(0.005, 0.005, vector.length), location=(start + end) / 2)
        obj.rotation_euler = Vector((0, 0, 1)).rotation_difference(vector).to_euler()
        obj.parent = parent

    if model == "magnesium":
        sphere("mg", magnesium, (0, 0, 0), 0.030)
    elif model == "oxygen":
        sphere("o-left", oxygen, (-0.018, 0, 0))
        sphere("o-right", oxygen, (0.018, 0, 0))
        connector("o-bond", (-0.010, 0, 0), (0.010, 0, 0))
    elif model == "magnesium-oxide":
        sphere("mg", magnesium, (-0.016, 0, 0), 0.030)
        sphere("o", oxygen, (0.016, 0, 0))
        connector("mg-o-bond", (-0.004, 0, 0), (0.004, 0, 0))
    else:
        raise ValueError(f"unsupported conceptual molecule model: {model}")
    return parent


def label_pop(obj, start, end, fps):
    f_in = max(2, round(start * fps))
    f_peak = f_in + 4
    f_out_start = max(f_peak + 1, round((end - 0.2) * fps))
    f_gone = max(f_out_start + 1, round(end * fps))
    obj.scale = (0.0001, 0.0001, 0.0001)
    obj.keyframe_insert("scale", frame=f_in)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert("scale", frame=f_peak)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert("scale", frame=f_out_start)
    obj.scale = (0.0001, 0.0001, 0.0001)
    obj.keyframe_insert("scale", frame=f_gone)
    for i in range(3):
        _key_easing(obj, "scale", i, f_in, "EASE_OUT")
        _key_easing(obj, "scale", i, f_out_start, "EASE_IN")


def move(target, start, duration, offset, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    target.location = Vector(target.location)
    target.keyframe_insert("location", frame=f0)
    target.location = Vector(target.location) + Vector(offset)
    target.keyframe_insert("location", frame=f1)
    for i in range(3):
        _key_easing(target, "location", i, f0, "EASE_IN_OUT")


def _mesh_materials(parent):
    materials = []
    for child in parent.children:
        if child.type == "MESH":
            for slot in child.material_slots:
                if slot.material is not None and slot.material.use_nodes:
                    materials.append(slot.material)
    return materials


def heat(parent, start, duration, color, strength, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    for material in _mesh_materials(parent):
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        emission = bsdf.inputs["Emission Strength"]
        emission.default_value = 0.0
        emission.keyframe_insert("default_value", frame=f0)
        emission.default_value = strength
        emission.keyframe_insert("default_value", frame=f1)


import math

def burn(parent, start, duration, strength, fps):
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))
    f_peak = f0 + max(1, round(0.3 * (f1 - f0)))
    for material in _mesh_materials(parent):
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        emission = bsdf.inputs["Emission Strength"]
        emission.default_value = 0.0
        emission.keyframe_insert("default_value", frame=f0)
        emission.default_value = strength
        emission.keyframe_insert("default_value", frame=f_peak)
        emission.default_value = 0.05 * strength
        emission.keyframe_insert("default_value", frame=f1)

    light_data = bpy.data.lights.new("burn-glow", type="POINT")
    light_data.energy = 0.0
    light_data.color = (1.0, 0.98, 0.95)
    light_data.shadow_soft_size = 0.015
    light = bpy.data.objects.new("burn-glow", light_data)
    bpy.context.collection.objects.link(light)
    light.parent = parent
    light.location = (0.0, 0.0, 0.0)
    light_data.energy = 0.0
    light_data.keyframe_insert("energy", frame=f0)
    light_data.energy = strength * 4.0
    light_data.keyframe_insert("energy", frame=f_peak)
    light_data.energy = strength * 0.2
    light_data.keyframe_insert("energy", frame=f1)


def show_flame(parent, offset, entry, fps):
    flame = bpy.data.objects.new("burner-flame", None)
    bpy.context.collection.objects.link(flame)
    flame.location = Vector(parent.location) + Vector(offset)

    # Outer luminous yellow-amber flame envelope
    outer = kit.add_material("flame-outer-yellow", (1.0, 0.65, 0.02),
                             metallic=0.0, roughness=0.3)
    outer_bsdf = outer.node_tree.nodes.get("Principled BSDF")
    outer_bsdf.inputs["Emission Color"].default_value = (1.0, 0.68, 0.05, 1.0)
    outer_bsdf.inputs["Emission Strength"].default_value = 14.0
    cone_outer = kit.primitive_object("flame-outer", "cone", outer,
                                      size=(0.014, 0.003, 0.046),
                                      location=(0.0, 0.0, 0.023))
    cone_outer.parent = flame

    # Inner bright golden-yellow core
    inner = kit.add_material("flame-inner-gold", (1.0, 0.85, 0.15),
                             metallic=0.0, roughness=0.3)
    inner_bsdf = inner.node_tree.nodes.get("Principled BSDF")
    inner_bsdf.inputs["Emission Color"].default_value = (1.0, 0.90, 0.25, 1.0)
    inner_bsdf.inputs["Emission Strength"].default_value = 20.0
    cone_inner = kit.primitive_object("flame-inner", "cone", inner,
                                      size=(0.007, 0.0015, 0.026),
                                      location=(0.0, 0.0, 0.013))
    cone_inner.parent = flame

    # Warm golden point light casting illumination on the burner & surroundings
    light_data = bpy.data.lights.new("flame-light", type="POINT")
    light_data.energy = 3.5
    light_data.color = (1.0, 0.70, 0.15)
    light_data.shadow_soft_size = 0.02
    light = bpy.data.objects.new("flame-light", light_data)
    bpy.context.collection.objects.link(light)
    light.parent = flame
    light.location = (0.0, 0.0, 0.022)

    start = entry["start"]
    end = entry.get("end")
    if end is not None:
        label_pop(flame, start, end, fps)
    else:
        appear(flame, start, entry.get("duration", 0.5), fps)


def collect_ash(source_parent, target_parent, start, duration, fps):
    """
    Animates the physical collection of white magnesium oxide ash:
    1. Spawns cascading white ash flakes dropping from the burning ribbon into the watch glass.
    2. Gradually grows the white MgO powder mound inside the watch glass bowl from 0 to full size.
    """
    f0 = max(1, round(start * fps))
    f1 = max(f0 + 1, round((start + duration) * fps))

    # 1. Animate target MgO powder heap scaling up inside the watch glass
    target_parent.scale = (0.0001, 0.0001, 0.0001)
    target_parent.keyframe_insert("scale", frame=f0)
    f_mid = f0 + round(0.5 * (f1 - f0))
    target_parent.scale = (0.55, 0.55, 0.55)
    target_parent.keyframe_insert("scale", frame=f_mid)
    target_parent.scale = (1.0, 1.0, 1.0)
    target_parent.keyframe_insert("scale", frame=f1)
    for i in range(3):
        _key_easing(target_parent, "scale", i, f0, "EASE_OUT")

    # 2. Spawn cascading falling ash flakes from source down into the target watch glass
    ash_mat = kit.add_material("falling-ash-flake", (0.98, 0.98, 0.97), metallic=0.0, roughness=0.9)
    ash_bsdf = ash_mat.node_tree.nodes.get("Principled BSDF")
    ash_bsdf.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    ash_bsdf.inputs["Emission Strength"].default_value = 5.0

    dst_pos = Vector(target_parent.location)
    src_pos = Vector((dst_pos.x, dst_pos.y, 0.145))

    num_flakes = 24
    for i in range(num_flakes):
        flake = kit.primitive_object(f"ash-flake-{i:02d}", "uv_sphere", ash_mat,
                                     size=(0.0032, 0.0032, 0.0032),
                                     location=(0.0, 0.0, 0.0))
        
        flake_t_start = start + (i / num_flakes) * (duration * 0.80)
        flake_dur = 0.40 + (i % 4) * 0.08
        
        ff0 = max(1, round(flake_t_start * fps))
        ff1 = max(ff0 + 1, round((flake_t_start + flake_dur) * fps))
        
        angle = i * 2.39996
        rad = 0.006 + (i % 4) * 0.003
        spawn_loc = Vector((src_pos.x + math.cos(angle) * rad,
                            src_pos.y + math.sin(angle) * rad,
                            src_pos.z - 0.005))
        land_loc = Vector((dst_pos.x + math.cos(angle) * (rad * 0.6),
                           dst_pos.y + math.sin(angle) * (rad * 0.6),
                           dst_pos.z + 0.003))
        
        flake.location = spawn_loc
        flake.scale = (0.0001, 0.0001, 0.0001)
        flake.keyframe_insert("location", frame=ff0)
        flake.keyframe_insert("scale", frame=ff0)
        
        ff_pop = ff0 + 2
        flake.scale = (1.0, 1.0, 1.0)
        flake.keyframe_insert("scale", frame=ff_pop)
        
        flake.location = land_loc
        flake.keyframe_insert("location", frame=ff1)
        flake.scale = (0.0001, 0.0001, 0.0001)
        flake.keyframe_insert("scale", frame=ff1)


def transform(parent, look, start, fps):
    f = max(1, round(start * fps))
    params = LOOKS[look]
    material = kit.add_material(f"look-{look}", params["color"],
                                params["metallic"], params["roughness"])
    for child in [c for c in parent.children if c.type == "MESH"]:
        duplicate = child.copy()
        duplicate.name = f"{child.name}-{look}"
        duplicate.data = child.data.copy()
        duplicate.data.materials.clear()
        duplicate.data.materials.append(material)
        duplicate.parent = child.parent
        bpy.context.scene.collection.objects.link(duplicate)

        child.hide_render = False
        child.keyframe_insert("hide_render", frame=max(1, f - 1))
        child.hide_render = True
        child.keyframe_insert("hide_render", frame=f)

        duplicate.hide_render = True
        duplicate.keyframe_insert("hide_render", frame=max(1, f - 1))
        duplicate.hide_render = False
        duplicate.keyframe_insert("hide_render", frame=f)
