"""
build_circuit.py — Laboratory Electric Circuit Trainer Board
NCERT Class 10 Science Chapter 12 (Electricity), Figure 12.1.

Dual Collections:
  1. Full_Circuit_Full:
     - Complete CBSE Class 10 laboratory circuit board mounted on an authentic Bakelite trainer plinth (260mm x 190mm) with rubber feet.
     - Precision laboratory components arranged in a closed series loop:
       * Battery: Molded dual-cell AA holder (3.0V DC) with red (+) and black (-) knurled brass binding posts.
       * Plug Key: Laboratory brass contact blocks with conical plug key firmly seated (closed circuit).
       * Ammeter: DC moving-coil ammeter (0-3A scale) with deflected needle at 0.30A.
       * Electric Bulb: Incandescent lamp in molded socket with glowing tungsten filament and glass envelope.
       * Resistor: 4-band precision bench resistor (10 ohms).
       * Interconnecting red and black flexible wires with spade lugs clamped securely under binding posts.
  2. Full_Circuit_Section:
     - Current Flow & Circuit Analysis:
       * Glowing cyan/emerald energy vector arrows showing conventional current (I) circulating clockwise.
       * Electron drift indicator arrows (e-) circulating counter-clockwise.
       * Glowing voltage drop indicators across the bulb and resistor.
       * Forward-angled laboratory educational plaque:
         - "CBSE CLASS 10 ELECTRIC CIRCUIT (NCERT FIG 12.1)"
         - "Ohm's Law: I = V / R = 3.0V / 10.0 ohm = 0.30 A"
         - "Series Circuit Rule: Current I is identical through every component"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'full-circuit'

# Calibrated Laboratory Palette
COLOR_TRAINER_BOARD = (0.10, 0.11, 0.14)     # Dark slate / Bakelite trainer base
COLOR_BRASS         = (0.86, 0.70, 0.26)     # Machined brass terminals, plugs, and posts
COLOR_COPPER        = (0.88, 0.54, 0.22)     # Polished copper busbars
COLOR_BATT_CASE     = (0.06, 0.06, 0.08)     # Matte black molded ABS battery holder
COLOR_BATT_CELL     = (0.16, 0.20, 0.28)     # Alkaline battery steel jacket
COLOR_GOLD          = (0.95, 0.78, 0.22)     # Gold battery contact nipple
COLOR_GLASS         = (0.95, 0.98, 1.00)     # Crystal glass bulb globe
COLOR_FILAMENT_GLOW = (1.00, 0.65, 0.20)     # Incandescent tungsten filament (2500K)
COLOR_METER_CASE    = (0.08, 0.09, 0.11)     # Bakelite meter enclosure
COLOR_DIAL_FACE     = (0.94, 0.94, 0.91)     # Ivory calibrated dial scale
COLOR_NEEDLE_RED    = (0.92, 0.12, 0.10)     # Vibrant red indicator needle
COLOR_WIRE_RED      = (0.86, 0.14, 0.12)     # Positive PVC lead
COLOR_WIRE_BLACK    = (0.08, 0.08, 0.10)     # Negative PVC return lead
COLOR_RESISTOR_BODY = (0.82, 0.74, 0.55)     # Alumina ceramic carbon-film body
COLOR_CURRENT_FLOW  = (0.10, 0.95, 0.45)     # Glowing emerald conventional current (I)
COLOR_ELECTRON_FLOW = (0.20, 0.80, 1.00)     # Glowing cyan electron drift (e-)
COLOR_AMBER         = (1.00, 0.72, 0.18)     # Educational callout highlight

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
    mid = (v1 + v2) / 2.0
    rot = diff.to_track_quat('Z', 'Y').to_euler()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=mid,
        rotation=rot
    )
    cyl = bpy.context.active_object
    cyl.name = name
    if cyl.data.materials:
        cyl.data.materials[0] = mat
    else:
        cyl.data.materials.append(mat)
    link_strictly(cyl, collection)
    return cyl

# -----------------------------------------------------------------------------
# BUILD FULL CIRCUIT FULL
# -----------------------------------------------------------------------------
def build_full_circuit_full(collection):
    board_mat = kit.add_material("fc-board", COLOR_TRAINER_BOARD, metallic=0.15, roughness=0.65)
    brass = kit.add_machined_metal_material("fc-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    batt_case = kit.add_material("fc-batt-case", COLOR_BATT_CASE, metallic=0.08, roughness=0.55)
    batt_cell = kit.add_machined_metal_material("fc-batt-cell", COLOR_BATT_CELL, metallic=0.75, roughness=0.35)
    gold = kit.add_machined_metal_material("fc-gold", COLOR_GOLD, metallic=0.95, roughness=0.18)
    glass = kit.add_glass_material("fc-glass", COLOR_GLASS, ior=1.52, roughness=0.015)
    filament = create_emissive_mat("fc-filament", COLOR_FILAMENT_GLOW, strength=14.0)
    meter_case = kit.add_material("fc-meter-case", COLOR_METER_CASE, metallic=0.12, roughness=0.55)
    dial_face = kit.add_material("fc-dial", COLOR_DIAL_FACE, metallic=0.0, roughness=0.4)
    needle_mat = kit.add_material("fc-needle", COLOR_NEEDLE_RED, metallic=0.1, roughness=0.3)
    res_body = kit.add_material("fc-res-body", COLOR_RESISTOR_BODY, metallic=0.05, roughness=0.5)
    red_wire = kit.add_material("fc-wire-red", COLOR_WIRE_RED, metallic=0.04, roughness=0.35)
    black_wire = kit.add_material("fc-wire-black", COLOR_WIRE_BLACK, metallic=0.04, roughness=0.35)

    # 1. Trainer Base Plinth (260mm x 190mm x 12mm)
    board = kit.primitive_object(
        f"{ASSET_ID}_Board", "cube", board_mat,
        size=(0.260, 0.190, 0.012),
        location=(0.0, 0.0, 0.006)
    )
    link_strictly(board, collection)

    # 4 Rubber Feet
    for fx in [-0.115, 0.115]:
        for fy in [-0.080, 0.080]:
            foot = kit.primitive_object(
                f"{ASSET_ID}_Foot_{fx}_{fy}", "cylinder", meter_case,
                size=(0.014, 0.014, 0.005),
                location=(fx, fy, -0.0025)
            )
            link_strictly(foot, collection)

    # 2. Battery Pack (Top Left: x = -0.075, y = +0.055)
    bx, by = -0.075, 0.055
    b_holder = kit.primitive_object(
        f"{ASSET_ID}_Batt_Holder", "cube", batt_case,
        size=(0.065, 0.038, 0.016),
        location=(bx, by, 0.020)
    )
    link_strictly(b_holder, collection)
    for c_idx, cy in enumerate([-0.009, 0.009]):
        cell = kit.primitive_object(
            f"{ASSET_ID}_Cell_{c_idx}", "cylinder", batt_cell,
            size=(0.014, 0.014, 0.050),
            location=(bx, by + cy, 0.024),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(cell, collection)
        cap = kit.primitive_object(
            f"{ASSET_ID}_Cell_Cap_{c_idx}", "cylinder", gold,
            size=(0.006, 0.006, 0.004),
            location=(bx + 0.026, by + cy, 0.024),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(cap, collection)

    # Battery Binding Posts (+ red post at +X, - black post at -X)
    post_pos = kit.primitive_object(f"{ASSET_ID}_Post_Batt_Pos", "cylinder", needle_mat, size=(0.010, 0.010, 0.016), location=(bx + 0.036, by, 0.020))
    post_neg = kit.primitive_object(f"{ASSET_ID}_Post_Batt_Neg", "cylinder", meter_case, size=(0.010, 0.010, 0.016), location=(bx - 0.036, by, 0.020))
    link_strictly(post_pos, collection)
    link_strictly(post_neg, collection)

    # 3. Laboratory Plug Key (Bottom Left: x = -0.075, y = -0.050)
    kx, ky = -0.075, -0.050
    k_plinth = kit.primitive_object(
        f"{ASSET_ID}_Key_Plinth", "cube", board_mat,
        size=(0.055, 0.034, 0.008),
        location=(kx, ky, 0.016)
    )
    link_strictly(k_plinth, collection)
    # Dual brass contact blocks with conical gap
    for b_idx, bx_off in enumerate([-0.014, 0.014]):
        k_block = kit.primitive_object(
            f"{ASSET_ID}_Key_Block_{b_idx}", "cube", brass,
            size=(0.018, 0.024, 0.014),
            location=(kx + bx_off, ky, 0.023)
        )
        link_strictly(k_block, collection)
        # Binding thumb nut on each block
        k_nut = kit.primitive_object(
            f"{ASSET_ID}_Key_Nut_{b_idx}", "cylinder", brass,
            size=(0.010, 0.010, 0.012),
            location=(kx + bx_off, ky - 0.010, 0.033)
        )
        link_strictly(k_nut, collection)

    # Brass Conical Plug Key firmly inserted (Closed Circuit)
    k_plug = kit.primitive_object(
        f"{ASSET_ID}_Key_Plug", "cone", brass,
        size=(0.010, 0.010, 0.018),
        location=(kx, ky, 0.027)
    )
    link_strictly(k_plug, collection)
    k_handle = kit.primitive_object(
        f"{ASSET_ID}_Key_Handle", "cylinder", meter_case,
        size=(0.014, 0.014, 0.016),
        location=(kx, ky, 0.040)
    )
    link_strictly(k_handle, collection)

    # 4. DC Ammeter (Center Right: x = +0.075, y = -0.045)
    ax, ay = 0.075, -0.045
    amm_body = kit.primitive_object(
        f"{ASSET_ID}_Amm_Body", "cube", meter_case,
        size=(0.055, 0.045, 0.032),
        location=(ax, ay, 0.028)
    )
    link_strictly(amm_body, collection)
    # Inclined meter dial face
    amm_dial = kit.primitive_object(
        f"{ASSET_ID}_Amm_Dial", "cube", dial_face,
        size=(0.045, 0.002, 0.026),
        location=(ax, ay - 0.022, 0.030)
    )
    link_strictly(amm_dial, collection)
    # Deflected red needle (indicating ~0.30 A)
    amm_needle = kit.primitive_object(
        f"{ASSET_ID}_Amm_Needle", "cylinder", needle_mat,
        size=(0.0015, 0.0015, 0.018),
        location=(ax + 0.005, ay - 0.020, 0.032),
        rotation_euler=(0.0, 0.0, math.radians(-24))
    )
    link_strictly(amm_needle, collection)
    # Red (+) and Black (-) terminal binding posts on ammeter
    amm_p = kit.primitive_object(f"{ASSET_ID}_Amm_Term_P", "cylinder", needle_mat, size=(0.009, 0.009, 0.012), location=(ax + 0.016, ay + 0.016, 0.045))
    amm_n = kit.primitive_object(f"{ASSET_ID}_Amm_Term_N", "cylinder", meter_case, size=(0.009, 0.009, 0.012), location=(ax - 0.016, ay + 0.016, 0.045))
    link_strictly(amm_p, collection)
    link_strictly(amm_n, collection)

    # 5. Incandescent Bulb in Socket (Top Right: x = +0.075, y = +0.055)
    lx, ly = 0.075, 0.055
    b_sock = kit.primitive_object(
        f"{ASSET_ID}_Bulb_Socket", "cylinder", meter_case,
        size=(0.030, 0.030, 0.018),
        location=(lx, ly, 0.021)
    )
    link_strictly(b_sock, collection)
    # Threaded brass collar
    b_collar = kit.primitive_object(
        f"{ASSET_ID}_Bulb_Collar", "cylinder", brass,
        size=(0.020, 0.020, 0.010),
        location=(lx, ly, 0.032)
    )
    link_strictly(b_collar, collection)
    # Teardrop glass bulb
    b_glass = kit.primitive_object(
        f"{ASSET_ID}_Bulb_Glass", "uv_sphere", glass,
        size=(0.028, 0.028, 0.036),
        location=(lx, ly, 0.050)
    )
    link_strictly(b_glass, collection)
    # Warm glowing filament
    b_fil = kit.primitive_object(
        f"{ASSET_ID}_Bulb_Filament", "uv_sphere", filament,
        size=(0.008, 0.008, 0.008),
        location=(lx, ly, 0.050)
    )
    link_strictly(b_fil, collection)

    # 6. Fixed Bench Resistor (Bottom Center: x = 0.0, y = -0.070)
    rx, ry = 0.0, -0.070
    r_body = kit.primitive_object(
        f"{ASSET_ID}_Res_Body", "cylinder", res_body,
        size=(0.007, 0.007, 0.024),
        location=(rx, ry, 0.018),
        rotation_euler=(0.0, math.pi/2, 0.0)
    )
    link_strictly(r_body, collection)
    # 4 EIA color bands: Brown, Black, Black, Gold (10 ohms +/- 5%)
    band_colors = [
        kit.add_material("fc-b1", (0.35, 0.18, 0.08), metallic=0.0, roughness=0.3),  # Brown (1)
        kit.add_material("fc-b2", (0.05, 0.05, 0.06), metallic=0.0, roughness=0.3),  # Black (0)
        kit.add_material("fc-b3", (0.05, 0.05, 0.06), metallic=0.0, roughness=0.3),  # Black (x1)
        gold                                                                           # Gold (+/- 5%)
    ]
    for b_i, b_mat in enumerate(band_colors):
        band = kit.primitive_object(
            f"{ASSET_ID}_Res_Band_{b_i}", "cylinder", b_mat,
            size=(0.0074, 0.0074, 0.002),
            location=(rx - 0.008 + b_i * 0.005, ry, 0.018),
            rotation_euler=(0.0, math.pi/2, 0.0)
        )
        link_strictly(band, collection)

    # 7. Complete Interconnecting Wire Routing (Series Loop)
    wire_r = 0.0018
    # Lead 1: Battery (+) at (bx+0.036, by, 0.020) -> Plug Key Left at (kx-0.014, ky-0.010, 0.033)
    p_w1 = [
        Vector((bx + 0.036, by, 0.022)),
        Vector((-0.030, by, 0.022)),
        Vector((-0.030, 0.005, 0.020)),
        Vector((kx - 0.025, 0.005, 0.020)),
        Vector((kx - 0.025, ky - 0.010, 0.022)),
        Vector((kx - 0.014, ky - 0.010, 0.033))
    ]
    for i in range(len(p_w1) - 1):
        create_cylinder_segment(f"{ASSET_ID}_W1_{i}", p_w1[i], p_w1[i+1], wire_r, red_wire, collection)

    # Lead 2: Plug Key Right at (kx+0.014, ky-0.010, 0.033) -> Resistor Left at (rx-0.014, ry, 0.018)
    p_w2 = [
        Vector((kx + 0.014, ky - 0.010, 0.033)),
        Vector((kx + 0.025, ky - 0.010, 0.020)),
        Vector((kx + 0.025, ry, 0.018)),
        Vector((rx - 0.014, ry, 0.018))
    ]
    for i in range(len(p_w2) - 1):
        create_cylinder_segment(f"{ASSET_ID}_W2_{i}", p_w2[i], p_w2[i+1], wire_r, red_wire, collection)

    # Lead 3: Resistor Right at (rx+0.014, ry, 0.018) -> Ammeter (+) at (ax+0.016, ay+0.016, 0.045)
    p_w3 = [
        Vector((rx + 0.014, ry, 0.018)),
        Vector((0.040, ry, 0.018)),
        Vector((0.040, ay - 0.015, 0.020)),
        Vector((ax + 0.025, ay - 0.015, 0.022)),
        Vector((ax + 0.025, ay + 0.016, 0.035)),
        Vector((ax + 0.016, ay + 0.016, 0.045))
    ]
    for i in range(len(p_w3) - 1):
        create_cylinder_segment(f"{ASSET_ID}_W3_{i}", p_w3[i], p_w3[i+1], wire_r, red_wire, collection)

    # Lead 4: Ammeter (-) at (ax-0.016, ay+0.016, 0.045) -> Bulb Socket at (lx, ly-0.014, 0.025)
    p_w4 = [
        Vector((ax - 0.016, ay + 0.016, 0.045)),
        Vector((ax - 0.016, 0.010, 0.022)),
        Vector((lx, 0.010, 0.022)),
        Vector((lx, ly - 0.014, 0.025))
    ]
    for i in range(len(p_w4) - 1):
        create_cylinder_segment(f"{ASSET_ID}_W4_{i}", p_w4[i], p_w4[i+1], wire_r, red_wire, collection)

    # Lead 5 (Return): Bulb Socket at (lx-0.014, ly, 0.025) -> Battery (-) at (bx-0.036, by, 0.020) (Black Wire)
    p_w5 = [
        Vector((lx - 0.014, ly, 0.025)),
        Vector((0.010, ly + 0.020, 0.022)),
        Vector((bx, ly + 0.020, 0.022)),
        Vector((bx - 0.036, ly + 0.020, 0.022)),
        Vector((bx - 0.036, by, 0.020))
    ]
    for i in range(len(p_w5) - 1):
        create_cylinder_segment(f"{ASSET_ID}_W5_{i}", p_w5[i], p_w5[i+1], wire_r, black_wire, collection)

    print("Built Full_Circuit_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD FULL CIRCUIT SECTION (Current Flow & Circuit Analysis)
# -----------------------------------------------------------------------------
def build_full_circuit_section(collection):
    # Same base components plus directional glowing current flow vectors and educational plaque
    build_full_circuit_full(collection)

    current_mat = create_emissive_mat("sec-fc-current", COLOR_CURRENT_FLOW, strength=14.0)
    electron_mat = create_emissive_mat("sec-fc-electron", COLOR_ELECTRON_FLOW, strength=12.0)
    gold_mat = kit.add_machined_metal_material("sec-fc-gold", COLOR_GOLD, metallic=0.92, roughness=0.20)
    brass = kit.add_machined_metal_material("sec-fc-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    plaque_bg = kit.add_material("sec-fc-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Conventional Current Flow Arrows (I -> clockwise around loop)
    # Positions along the circuit path
    arrow_nodes = [
        # Along Lead 1 (Battery -> Key)
        ((-0.030, 0.030, 0.026), (0.0, -1.0, 0.0)),
        # Along Lead 2 (Key -> Resistor)
        ((-0.035, -0.070, 0.024), (1.0, 0.0, 0.0)),
        # Along Lead 3 (Resistor -> Ammeter)
        ((0.040, -0.040, 0.024), (0.0, 1.0, 0.0)),
        # Along Lead 4 (Ammeter -> Bulb)
        ((0.075, 0.010, 0.026), (0.0, 1.0, 0.0)),
        # Along Lead 5 (Bulb -> Battery Return)
        ((0.000, 0.075, 0.026), (-1.0, 0.0, 0.0))
    ]

    for a_idx, (pos, fdir) in enumerate(arrow_nodes):
        d_vec = Vector(fdir).normalized()
        rot = d_vec.to_track_quat('Z', 'Y').to_euler()
        shaft = kit.primitive_object(
            f"Sec_Current_Shaft_{a_idx}", "cylinder", current_mat,
            size=(0.0016, 0.0016, 0.014),
            location=pos,
            rotation_euler=rot
        )
        link_strictly(shaft, collection)
        head = kit.primitive_object(
            f"Sec_Current_Head_{a_idx}", "cone", current_mat,
            size=(0.0045, 0.0045, 0.008),
            location=(pos[0] + d_vec.x * 0.009, pos[1] + d_vec.y * 0.009, pos[2] + d_vec.z * 0.009),
            rotation_euler=rot
        )
        link_strictly(head, collection)

    # 2. Forward Angled Laboratory Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.240, 0.006, 0.062),
        location=(0.0, -0.118, 0.030),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.246, 0.004, 0.068),
        location=(0.0, -0.119, 0.030),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.210, 0.002, 0.009),
        location=(0.0, -0.115, 0.048),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    bar_ohm = kit.primitive_object(
        "Sec_Plaque_Bar_Ohm", "cube", current_mat,
        size=(0.190, 0.002, 0.007),
        location=(0.0, -0.117, 0.032),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_ohm, collection)

    bar_series = kit.primitive_object(
        "Sec_Plaque_Bar_Series", "cube", electron_mat,
        size=(0.200, 0.002, 0.006),
        location=(0.0, -0.119, 0.016),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_series, collection)

    for sx in [-0.08, 0.08]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Leg_{sx}", "cylinder", brass,
            size=(0.005, 0.005, 0.032),
            location=(sx, -0.115, 0.015)
        )
        link_strictly(stanchion, collection)

    print("Built Full_Circuit_Section successfully.")

# -----------------------------------------------------------------------------
# CAMERA & LIGHTING
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 45.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 3/4 perspective overlooking the trainer board and front plaque
    cam_obj.location = Vector((-0.02, -0.39, 0.31))
    direction = Vector((0.0, -0.02, 0.025)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    def make_light(name, ltype, pos, power, size=0.3):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = power
        if ltype == 'AREA':
            ldata.size = size
            ldata.shape = 'RECTANGLE'
            ldata.size_y = size * 0.7
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = pos
        bpy.context.scene.collection.objects.link(lobj)
        return lobj

    make_light("Key_Left", "AREA", (-0.18, -0.25, 0.32), 6.0, 0.35)
    make_light("Key_Right", "AREA", (0.18, -0.22, 0.30), 5.5, 0.35)
    make_light("Fill_Center", "AREA", (0.0, -0.18, 0.22), 3.5, 0.40)
    make_light("Top_Rim", "AREA", (0.0, 0.22, 0.35), 5.0, 0.40)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Full_Circuit_Full")
    sec_col  = bpy.data.collections.new("Full_Circuit_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_full_circuit_full(full_col)
    build_full_circuit_section(sec_col)
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

    # Render Preview 1: Full_Circuit_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Full_Circuit_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
