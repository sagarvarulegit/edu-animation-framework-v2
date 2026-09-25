"""
build_battery.py — Laboratory DC Battery Source (Dual-Cell 3.0V) & Dry Cell Cross-Section
NCERT Class 10 Science Chapter 11 (Electricity) & Class 12 Physics (Current Electricity).

Dual Collections:
  1. Battery_Full:
     - Laboratory dual-cell battery holder box on slate plinth.
     - Twin knurled brass binding posts (Red +, Black -).
     - Two standard AA dry cells connected in series (1.5V + 1.5V = 3.0V DC).
     - Authentic gold/navy jackets, brass positive contact pips, zinc base plates, polarity markings.
     - Nickel-plated contact springs and series interconnect strap.

  2. Battery_Section (Internal Electrochemical Architecture):
     - Longitudinal cutaway cross-section of Leclanché dry cell:
       * Central cylindrical graphite / carbon rod (Cathode +).
       * Brass terminal cap contact.
       * Manganese dioxide (MnO2) + powdered carbon depolarizer mixture.
       * Ammonium chloride (NH4Cl) + Zinc chloride (ZnCl2) electrolyte paste.
       * Porous separator paper liner.
       * Outer Zinc container can (Anode -).
       * Pitch/resin top insulating seal.
       * Luminescent cyan current flow vectors and electron drift indicators.
       * Forward-tilted educational plaque on brass stanchions:
         - "DRY CELL (LECLANCHÉ CELL - 1.5V DC)"
         - "Anode (-): Zn(s) -> Zn2+(aq) + 2e-"
         - "Cathode (+): 2MnO2 + 2NH4+ + 2e- -> Mn2O3 + 2NH3 + H2O"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'battery'

# Calibrated Laboratory Palette
COLOR_HOLDER_BAKELITE = (0.12, 0.13, 0.15)     # Molded black Bakelite battery holder
COLOR_CELL_JACKET     = (0.08, 0.14, 0.28)     # Navy blue cell insulator jacket
COLOR_CELL_GOLD       = (0.85, 0.68, 0.22)     # Golden metallic upper sleeve
COLOR_BRASS           = (0.86, 0.70, 0.28)     # Machined brass knurled binding posts & pips
COLOR_NICKEL          = (0.82, 0.84, 0.88)     # Nickel-plated steel springs & zinc can
COLOR_TERM_RED        = (0.88, 0.16, 0.16)     # Positive red terminal collar
COLOR_TERM_BLACK      = (0.10, 0.10, 0.12)     # Negative black terminal collar
COLOR_GRAPHITE_ROD    = (0.05, 0.05, 0.06)     # Pure carbon / graphite cathode electrode
COLOR_MNO2_DEPOLAR    = (0.18, 0.18, 0.22)     # MnO2 + carbon black depolarizer mix
COLOR_ELECTROLYTE     = (0.78, 0.82, 0.75)     # NH4Cl paste electrolyte
COLOR_SEPARATOR       = (0.92, 0.90, 0.82)     # Porous fibrous separator paper
COLOR_PITCH_SEAL      = (0.03, 0.03, 0.04)     # Insulating asphalt / pitch top seal
COLOR_CURRENT_CYAN    = (0.20, 0.82, 1.00)     # Luminescent cyan current / electron flow
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
                                  size=(0.14, 0.10, 0.012),
                                  location=(0.0, 0.0, 0.006))
    objs.append(plinth)

    trim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                                size=(0.142, 0.102, 0.002),
                                location=(0.0, 0.0, 0.001))
    objs.append(trim)
    return objs

def build_single_cell(prefix, subname, collection, loc, mat_jacket, mat_gold, mat_brass, mat_nickel, mat_red):
    """Builds a single authentic AA dry cell lying horizontally or standing."""
    objs = []
    cx, cy, cz = loc
    # Cell radius 0.007m (14mm diameter), length 0.048m (48mm)
    # Main navy sleeve
    cell_body = kit.primitive_object(f"{prefix}_{subname}_body", "cylinder", mat_jacket,
                                     size=(0.014, 0.014, 0.034),
                                     location=(cx, cy, cz),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.append(cell_body)

    # Gold upper sleeve near positive end (+X)
    cell_gold = kit.primitive_object(f"{prefix}_{subname}_gold", "cylinder", mat_gold,
                                     size=(0.0142, 0.0142, 0.012),
                                     location=(cx + 0.016, cy, cz),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.append(cell_gold)

    # Positive insulator shoulder ring
    shoulder = kit.primitive_object(f"{prefix}_{subname}_shoulder", "cylinder", mat_red,
                                    size=(0.013, 0.013, 0.002),
                                    location=(cx + 0.0225, cy, cz),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.append(shoulder)

    # Brass positive pip button
    pip = kit.primitive_object(f"{prefix}_{subname}_pip", "cylinder", mat_brass,
                              size=(0.0055, 0.0055, 0.004),
                              location=(cx + 0.0245, cy, cz),
                              rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.append(pip)

    # Negative zinc base disc (-X)
    neg_plate = kit.primitive_object(f"{prefix}_{subname}_neg_plate", "cylinder", mat_nickel,
                                     size=(0.0138, 0.0138, 0.002),
                                     location=(cx - 0.023, cy, cz),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
    objs.append(neg_plate)

    # Plus / Minus polarity decals
    # '+' on gold jacket (+X)
    plus_h = kit.primitive_object(f"{prefix}_{subname}_plus_h", "cube", mat_red,
                                 size=(0.003, 0.0008, 0.0005),
                                 location=(cx + 0.016, cy - 0.0072, cz + 0.002))
    plus_v = kit.primitive_object(f"{prefix}_{subname}_plus_v", "cube", mat_red,
                                 size=(0.0008, 0.003, 0.0005),
                                 location=(cx + 0.016, cy - 0.0072, cz + 0.002))
    # '-' on navy body (-X)
    minus_h = kit.primitive_object(f"{prefix}_{subname}_minus_h", "cube", mat_nickel,
                                  size=(0.003, 0.0008, 0.0005),
                                  location=(cx - 0.012, cy - 0.0072, cz + 0.002))
    objs.extend([plus_h, plus_v, minus_h])
    return objs

def build_battery_full(collection):
    """Collection 1: Real-world bench battery pack with dual AA cells in series."""
    prefix = "batt_full"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_holder = kit.add_material(f"{prefix}_holder", COLOR_HOLDER_BAKELITE, metallic=0.15, roughness=0.45)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_nickel = kit.add_machined_metal_material(f"{prefix}_nickel", COLOR_NICKEL, metallic=0.95, roughness=0.20)
    mat_jacket = kit.add_material(f"{prefix}_jacket", COLOR_CELL_JACKET, metallic=0.25, roughness=0.40)
    mat_gold   = kit.add_machined_metal_material(f"{prefix}_gold", COLOR_CELL_GOLD, metallic=0.88, roughness=0.25)
    mat_red    = kit.add_material(f"{prefix}_red", COLOR_TERM_RED, metallic=0.15, roughness=0.35)
    mat_black  = kit.add_material(f"{prefix}_black", COLOR_TERM_BLACK, metallic=0.15, roughness=0.40)

    # 1. Molded Battery Cradle Box on Plinth
    # Outer box: 0.075 x 0.055 x 0.024, base z=0.012 -> center z=0.024
    cradle_base = kit.primitive_object(f"{prefix}_cradle_base", "cube", mat_holder,
                                       size=(0.076, 0.052, 0.005),
                                       location=(0.0, -0.005, 0.0145))
    cradle_back = kit.primitive_object(f"{prefix}_cradle_back", "cube", mat_holder,
                                       size=(0.076, 0.004, 0.022),
                                       location=(0.0, 0.020, 0.023))
    cradle_front = kit.primitive_object(f"{prefix}_cradle_front", "cube", mat_holder,
                                        size=(0.076, 0.004, 0.022),
                                        location=(0.0, -0.030, 0.023))
    cradle_left = kit.primitive_object(f"{prefix}_cradle_left", "cube", mat_holder,
                                       size=(0.005, 0.052, 0.022),
                                       location=(-0.037, -0.005, 0.023))
    cradle_right = kit.primitive_object(f"{prefix}_cradle_right", "cube", mat_holder,
                                        size=(0.005, 0.052, 0.022),
                                        location=(0.037, -0.005, 0.023))
    cradle_divider = kit.primitive_object(f"{prefix}_cradle_div", "cube", mat_holder,
                                         size=(0.072, 0.003, 0.016),
                                         location=(0.0, -0.005, 0.020))
    all_objs.extend([cradle_base, cradle_back, cradle_front, cradle_left, cradle_right, cradle_divider])

    # 2. Terminal Binding Posts on Rear Upright Lip
    # Red (+) on right (+X=0.025), Black (-) on left (-X=-0.025)
    for sign, color_mat, name in [(1, mat_red, "pos"), (-1, mat_black, "neg")]:
        collar = kit.primitive_object(f"{prefix}_collar_{name}", "cylinder", color_mat,
                                      size=(0.012, 0.012, 0.004),
                                      location=(sign * 0.026, 0.032, 0.014))
        stud = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_brass,
                                    size=(0.006, 0.006, 0.018),
                                    location=(sign * 0.026, 0.032, 0.021))
        nut = kit.primitive_object(f"{prefix}_nut_{name}", "cylinder", mat_brass,
                                   size=(0.010, 0.010, 0.008),
                                   location=(sign * 0.026, 0.032, 0.024))
        all_objs.extend([collar, stud, nut])

    # 3. Contact Springs & Straps
    # Cell 1 (Y = +0.008): positive at +X, negative spring at -X
    # Cell 2 (Y = -0.018): negative spring at +X, positive at -X (series loop)
    # Series busbar connecting Cell 1 (+) to Cell 2 (-) at +X end
    series_bar = kit.primitive_object(f"{prefix}_series_bar", "cube", mat_nickel,
                                      size=(0.003, 0.026, 0.012),
                                      location=(0.034, -0.005, 0.024))
    all_objs.append(series_bar)

    # Negative springs (spiral / conical coils)
    spring1 = kit.primitive_object(f"{prefix}_spring_1", "cylinder", mat_nickel,
                                  size=(0.010, 0.010, 0.005),
                                  location=(-0.032, 0.008, 0.024),
                                  rotation_euler=(0.0, math.pi / 2, 0.0))
    spring2 = kit.primitive_object(f"{prefix}_spring_2", "cylinder", mat_nickel,
                                  size=(0.010, 0.010, 0.005),
                                  location=(0.031, -0.018, 0.024),
                                  rotation_euler=(0.0, math.pi / 2, 0.0))
    all_objs.extend([spring1, spring2])

    # 4. Insert Two AA Cells
    cell1_objs = build_single_cell(prefix, "c1", collection, (0.003, 0.008, 0.024),
                                   mat_jacket, mat_gold, mat_brass, mat_nickel, mat_red)
    cell2_objs = build_single_cell(prefix, "c2", collection, (-0.003, -0.018, 0.024),
                                   mat_jacket, mat_gold, mat_brass, mat_nickel, mat_red)
    all_objs.extend(cell1_objs)
    all_objs.extend(cell2_objs)

    for obj in all_objs:
        link_strictly(obj, collection)
    return all_objs

def build_battery_section(collection):
    """Collection 2: Cutaway Cross-Section of Chemical Dry Cell with Educational Plaque."""
    prefix = "batt_sec"
    all_objs = []
    all_objs.extend(build_shared_plinth(prefix, collection))

    mat_zinc       = kit.add_machined_metal_material(f"{prefix}_zinc", COLOR_NICKEL, metallic=0.92, roughness=0.25)
    mat_separator  = kit.add_material(f"{prefix}_separator", COLOR_SEPARATOR, metallic=0.05, roughness=0.7)
    mat_electrolyte= kit.add_material(f"{prefix}_paste", COLOR_ELECTROLYTE, metallic=0.05, roughness=0.6)
    mat_mno2       = kit.add_material(f"{prefix}_mno2", COLOR_MNO2_DEPOLAR, metallic=0.10, roughness=0.6)
    mat_graphite   = kit.add_material(f"{prefix}_carbon", COLOR_GRAPHITE_ROD, metallic=0.20, roughness=0.45)
    mat_brass      = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    mat_pitch      = kit.add_material(f"{prefix}_pitch", COLOR_PITCH_SEAL, metallic=0.08, roughness=0.3)
    mat_cyan_glow  = create_emissive_mat(f"{prefix}_glow", COLOR_CURRENT_CYAN, strength=12.0)
    mat_trim       = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    # Center location for cutaway dry cell standing vertically on plinth
    # Z ranges from z=0.012 to z=0.065
    cz = 0.038
    cx = 0.0
    cy = 0.005

    # Half cutaway: models are half-cylinders along Y>=cy (or angle from 0 to pi)
    # 1. Outer Zinc Can (Anode -): Outer r=0.014, thickness 0.001
    bm_can = bmesh.new()
    bmesh.ops.create_cone(bm_can, cap_ends=True, cap_tris=False, segments=32,
                          radius1=0.014, radius2=0.014, depth=0.048)
    mesh_can = bpy.data.meshes.new(f"{prefix}_zinc_can")
    bm_can.to_mesh(mesh_can)
    bm_can.free()
    for poly in mesh_can.polygons:
        poly.use_smooth = True
    can_obj = bpy.data.objects.new(f"{prefix}_zinc_can", mesh_can)
    can_obj.location = (cx, cy, cz)
    can_obj.data.materials.append(mat_zinc)
    link_strictly(can_obj, collection)
    all_objs.append(can_obj)

    # 2. Porous Paper Separator Liner
    bm_sep = bmesh.new()
    bmesh.ops.create_cone(bm_sep, cap_ends=True, cap_tris=False, segments=32,
                          radius1=0.013, radius2=0.013, depth=0.046)
    mesh_sep = bpy.data.meshes.new(f"{prefix}_separator")
    bm_sep.to_mesh(mesh_sep)
    bm_sep.free()
    for poly in mesh_sep.polygons:
        poly.use_smooth = True
    sep_obj = bpy.data.objects.new(f"{prefix}_separator", mesh_sep)
    sep_obj.location = (cx, cy, cz - 0.001)
    sep_obj.data.materials.append(mat_separator)
    link_strictly(sep_obj, collection)
    all_objs.append(sep_obj)

    # 3. Ammonium Chloride Electrolyte Paste Layer
    bm_elec = bmesh.new()
    bmesh.ops.create_cone(bm_elec, cap_ends=True, cap_tris=False, segments=32,
                           radius1=0.0115, radius2=0.0115, depth=0.044)
    mesh_elec = bpy.data.meshes.new(f"{prefix}_electrolyte")
    bm_elec.to_mesh(mesh_elec)
    bm_elec.free()
    for poly in mesh_elec.polygons:
        poly.use_smooth = True
    elec_obj = bpy.data.objects.new(f"{prefix}_electrolyte", mesh_elec)
    elec_obj.location = (cx, cy, cz - 0.001)
    elec_obj.data.materials.append(mat_electrolyte)
    link_strictly(elec_obj, collection)
    all_objs.append(elec_obj)

    # 4. Manganese Dioxide (MnO2) Depolarizer Mixture
    bm_mno2 = bmesh.new()
    bmesh.ops.create_cone(bm_mno2, cap_ends=True, cap_tris=False, segments=32,
                          radius1=0.0085, radius2=0.0085, depth=0.042)
    mesh_mno2 = bpy.data.meshes.new(f"{prefix}_mno2_depolar")
    bm_mno2.to_mesh(mesh_mno2)
    bm_mno2.free()
    for poly in mesh_mno2.polygons:
        poly.use_smooth = True
    mno2_obj = bpy.data.objects.new(f"{prefix}_mno2_depolar", mesh_mno2)
    mno2_obj.location = (cx, cy, cz - 0.001)
    mno2_obj.data.materials.append(mat_mno2)
    link_strictly(mno2_obj, collection)
    all_objs.append(mno2_obj)

    # 5. Central Carbon / Graphite Rod (Cathode +)
    carbon_rod = kit.primitive_object(f"{prefix}_carbon_rod", "cylinder", mat_graphite,
                                      size=(0.0055, 0.0055, 0.048),
                                      location=(cx, cy, cz + 0.003))
    all_objs.append(carbon_rod)

    # 6. Brass Top Contact Cap
    brass_cap = kit.primitive_object(f"{prefix}_brass_cap", "cylinder", mat_brass,
                                     size=(0.0065, 0.0065, 0.006),
                                     location=(cx, cy, cz + 0.026))
    all_objs.append(brass_cap)

    # 7. Pitch / Asphalt Top Insulating Seal Ring
    pitch_seal = kit.primitive_object(f"{prefix}_pitch_seal", "cylinder", mat_pitch,
                                      size=(0.0135, 0.0135, 0.004),
                                      location=(cx, cy, cz + 0.022))
    all_objs.append(pitch_seal)

    # Bisect cutter for front half-cutaway (cutter removes front Y < cy)
    cutter = kit.primitive_object(f"{prefix}_cutter", "cube", mat_pitch,
                                  size=(0.040, 0.030, 0.060),
                                  location=(cx, cy - 0.015, cz))
    for target in [can_obj, sep_obj, elec_obj, mno2_obj, pitch_seal]:
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        bpy.context.view_layer.objects.active = target
        mod = target.modifiers.new(name="Bool_Cut", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

    # 8. Luminescent Cyan Current & Charge Migration Indicator Beams
    # Flow from zinc can towards positive terminal
    flow1 = create_cylinder_segment(f"{prefix}_flow_1", (cx - 0.013, cy, cz - 0.018), (cx - 0.013, cy, cz + 0.018), 0.0006, mat_cyan_glow, collection)
    flow2 = create_cylinder_segment(f"{prefix}_flow_2", (cx + 0.013, cy, cz - 0.018), (cx + 0.013, cy, cz + 0.018), 0.0006, mat_cyan_glow, collection)
    if flow1: all_objs.append(flow1)
    if flow2: all_objs.append(flow2)

    # 9. Educational Plaque Mounted on Brass Stanchions
    # Plaque at front y = -0.038, z=0.012, tilted backward towards camera (-25 deg)
    plaque_y = -0.038
    plaque_z = 0.010
    plaque_w = 0.126
    plaque_h = 0.024
    plaque_th = 0.003
    angle_tilt = -math.radians(25.0)
    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')

    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_zinc,
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
    # Title bar
    l_pos1 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.006))
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(0.105, 0.0012, 0.0030),
                                     location=(l_pos1.x, plaque_y + l_pos1.y, plaque_z + l_pos1.z),
                                     rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(title_bar)

    # Formula bar 1: Anode
    l_pos2 = rot_m @ Vector((0.0, -plaque_th * 0.5 - front_offset, 0.000))
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_cyan_glow,
                                size=(0.095, 0.0010, 0.0022),
                                location=(l_pos2.x, plaque_y + l_pos2.y, plaque_z + l_pos2.z),
                                rotation_euler=(angle_tilt, 0.0, 0.0))
    all_objs.append(sub1)

    # Formula bar 2: Cathode
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
    cam_data = bpy.data.cameras.new("Battery_Camera")
    cam_data.lens = 50.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("Battery_Camera", cam_data)
    # 3/4 isometric perspective
    cam_obj.location = (0.12, -0.22, 0.18)
    # Point towards center (0, 0, 0.025)
    direction = Vector((0.0, 0.0, 0.025)) - cam_obj.location
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

    make_light("Light_Key", "AREA", (0.32, -0.25, 0.35), 28.0, 0.40)
    make_light("Light_Fill", "AREA", (-0.25, -0.25, 0.28), 16.0, 0.40)
    make_light("Light_Top", "AREA", (0.0, -0.02, 0.32), 22.0, 0.40)
    make_light("Light_Rim", "AREA", (-0.10, 0.25, 0.28), 20.0, 0.35)

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Battery_Full")
    sec_col  = bpy.data.collections.new("Battery_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_battery_full(full_col)
    build_battery_section(sec_col)
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

    # Render Preview 1: Battery_Full
    kit.configure_render(width=1280, height=720, samples=32)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Battery_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print("=== BATTERY BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
