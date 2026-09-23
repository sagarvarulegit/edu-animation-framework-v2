"""
build_dna.py — B-DNA Double Helix & Molecular Subunit Architecture
CBSE Class 10 Biology, Chapter 8: How do Organisms Reproduce? (DNA Copying)
CBSE Class 11 Biology, Chapter 9: Biomolecules (Nucleic Acids) (Fig 9.5)
CBSE Class 12 Biology, Chapter 6: Molecular Basis of Inheritance (Fig 6.2, 6.3)

Dual Collections:
1. DNA_Full:
   - Antiparallel B-DNA double helix with authentic Major Groove (~2.2 nm) and Minor Groove (~1.2 nm).
   - 10 base pairs per helical turn (3.4 nm pitch), 2.0 nm diameter.
   - Sugar-phosphate ribbon backbone with embedded phosphate nodes and deoxyribose units.
   - Watson-Crick base-pair rungs (A green, T red, G amber, C blue).
   - Antiparallel directionality tags (5' and 3' terminals on both strands).
   - Polished exhibition pedestal and brass armature.

2. DNA_Detail:
   - High-resolution unzipped / exploded nucleotide architecture (NCERT Fig 6.2).
   - Pentose Deoxyribose sugar 5-carbon rings (1' to 5').
   - Tetrahedral Phosphate groups with phosphodiester ester bonds.
   - Purine double-ring bases (Adenine & Guanine: fused 6-ring + 5-ring).
   - Pyrimidine single-ring bases (Thymine & Cytosine: 6-ring).
   - N-glycosidic linkages between 1' sugar carbon and nitrogenous base.
   - Exact hydrogen bond stoichiometry: 2 dotted H-bonds for A=T, 3 dotted H-bonds for G≡C.
   - 3D terminal direction markers: 5' and 3'.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = "dna-double-helix"

# Calibrated Botanical & Genetic Design Colors
COLOR_BACKBONE  = (0.015, 0.520, 0.780)  # Azure Sugar-Phosphate
COLOR_PHOSPHATE = (0.950, 0.520, 0.050)  # Amber Phosphate Group
COLOR_SUGAR     = (0.120, 0.700, 0.820)  # Deoxyribose Pentose Sugar
COLOR_ADENINE   = (0.080, 0.650, 0.280)  # Green (Purine, 2 rings)
COLOR_THYMINE   = (0.860, 0.150, 0.150)  # Red (Pyrimidine, 1 ring)
COLOR_GUANINE   = (0.880, 0.500, 0.040)  # Amber/Gold (Purine, 2 rings)
COLOR_CYTOSINE  = (0.140, 0.380, 0.920)  # Royal Blue (Pyrimidine, 1 ring)
COLOR_H_BOND    = (0.960, 0.980, 1.000)  # Illuminated Hydrogen Bonds
COLOR_STAND     = (0.120, 0.140, 0.160)  # Matte Dark Exhibition Base
COLOR_BRASS     = (0.820, 0.680, 0.220)

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=6.0):
    mat = kit.add_material(name, color[:3], metallic=0.1, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_regular_prism(name, num_sides, radius, height, material, location, rotation_euler, collection):
    bm = bmesh.new()
    half_h = height * 0.5
    top_verts = []
    bot_verts = []
    for i in range(num_sides):
        ang = 2.0 * math.pi * i / num_sides
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        top_verts.append(bm.verts.new((x, y, half_h)))
        bot_verts.append(bm.verts.new((x, y, -half_h)))
    for i in range(num_sides):
        next_i = (i + 1) % num_sides
        bm.faces.new([top_verts[i], top_verts[next_i], bot_verts[next_i], bot_verts[i]])
    bm.faces.new(top_verts)
    bm.faces.new(list(reversed(bot_verts)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    obj.location = location
    obj.rotation_euler = rotation_euler
    link_strictly(obj, collection)
    return obj

def create_purine_base(name, material, location, sign, collection):
    """
    Purine base (Adenine, Guanine): Fused 6-membered and 5-membered rings.
    sign = +1 if extending from left to right (toward center),
    sign = -1 if extending from right to left (toward center).
    """
    objs = []
    # 5-membered ring attached at the sugar end
    r5 = create_regular_prism(f"{name}_5Ring", 5, radius=0.0032, height=0.0024,
                              material=material, location=(location.x, location.y, location.z),
                              rotation_euler=(0, 0, math.radians(18) if sign > 0 else math.radians(198)),
                              collection=collection)
    objs.append(r5)

    # 6-membered ring extending toward the hydrogen bond center
    r6 = create_regular_prism(f"{name}_6Ring", 6, radius=0.0038, height=0.0024,
                              material=material, location=(location.x + sign * 0.0058, location.y, location.z),
                              rotation_euler=(0, 0, 0), collection=collection)
    objs.append(r6)
    return objs

def create_pyrimidine_base(name, material, location, sign, collection):
    """
    Pyrimidine base (Thymine, Cytosine): Single 6-membered heterocyclic ring.
    """
    r6 = create_regular_prism(f"{name}_6Ring", 6, radius=0.0038, height=0.0024,
                              material=material, location=location,
                              rotation_euler=(0, 0, 0), collection=collection)
    return [r6]

def build_dna_full(collection):
    """Constructs canonical B-DNA double helix with major/minor grooves and pedestal."""
    objs = []

    mat_backbone = kit.add_material("Full_Backbone", COLOR_BACKBONE, metallic=0.18, roughness=0.28)
    mat_phosphate = kit.add_material("Full_Phosphate", COLOR_PHOSPHATE, metallic=0.15, roughness=0.30)
    mat_a = kit.add_material("Full_Adenine", COLOR_ADENINE, metallic=0.08, roughness=0.32)
    mat_t = kit.add_material("Full_Thymine", COLOR_THYMINE, metallic=0.08, roughness=0.32)
    mat_g = kit.add_material("Full_Guanine", COLOR_GUANINE, metallic=0.08, roughness=0.32)
    mat_c = kit.add_material("Full_Cytosine", COLOR_CYTOSINE, metallic=0.08, roughness=0.32)
    mat_h = create_emissive_mat("Full_HBond", COLOR_H_BOND, strength=5.0)
    mat_stand = kit.add_material("Full_Stand", COLOR_STAND, metallic=0.88, roughness=0.22)
    mat_brass = kit.add_material("Full_Brass", COLOR_BRASS, metallic=0.92, roughness=0.18)
    mat_badge_5 = create_emissive_mat("Full_Badge_5", (0.95, 0.35, 0.15), strength=6.0)
    mat_badge_3 = create_emissive_mat("Full_Badge_3", (0.15, 0.65, 0.95), strength=6.0)

    radius = 0.018       # 1.8 cm
    height = 0.150       # 15.0 cm (2.0 turns)
    turns = 2.0
    steps_per_turn = 36
    total_steps = int(turns * steps_per_turn)

    # Authentic Major (220°) and Minor (140°) groove offset
    groove_offset = math.radians(140.0)

    # 1. Antiparallel Sugar-Phosphate Helical Backbones
    for strand in range(2):
        strand_pts = []
        base_angle_offset = strand * groove_offset
        for i in range(total_steps + 1):
            t = i / total_steps
            ang = t * turns * 2.0 * math.pi + base_angle_offset
            z = -height * 0.5 + t * height
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            strand_pts.append((x, y, z))

            # Phosphate nodes along the spiral
            if i % 3 == 0:
                p_node = kit.primitive_object(f"Full_PhosphateNode_{strand}_{i}", "uv_sphere", mat_phosphate,
                                              size=(0.0034, 0.0034, 0.0034),
                                              location=(x, y, z))
                link_strictly(p_node, collection)
                objs.append(p_node)

        strand_obj = kit.create_smooth_tube(f"Full_Strand_{strand}", strand_pts, radius=0.0024, cap_ends=True, material=mat_backbone)
        link_strictly(strand_obj, collection)
        objs.append(strand_obj)

    # 2. Watson-Crick Base-Pair Rungs (10 base pairs per turn = 20 total rungs)
    pair_defs = [
        (mat_a, mat_t, True),   # A (purine, green) - T (pyrimidine, red)
        (mat_g, mat_c, True),   # G (purine, amber) - C (pyrimidine, blue)
        (mat_t, mat_a, False),  # T (pyrimidine) - A (purine)
        (mat_c, mat_g, False),  # C (pyrimidine) - G (purine)
        (mat_a, mat_t, True),
        (mat_g, mat_c, True),
        (mat_c, mat_g, False),
        (mat_t, mat_a, False),
        (mat_a, mat_t, True),
        (mat_g, mat_c, True),
    ]

    num_rungs = 20
    for r in range(num_rungs):
        t = r / (num_rungs - 1)
        ang0 = t * turns * 2.0 * math.pi
        ang1 = ang0 + groove_offset
        z = -height * 0.5 + t * height

        p0 = Vector((radius * math.cos(ang0), radius * math.sin(ang0), z))
        p1 = Vector((radius * math.cos(ang1), radius * math.sin(ang1), z))

        disp = p1 - p0
        length = disp.length
        if length < 1e-4:
            continue
        dir_norm = disp.normalized()
        rot_euler = dir_norm.to_track_quat('Z', 'Y').to_euler()

        mat_l, mat_r, left_is_purine = pair_defs[r % len(pair_defs)]

        ratio_l = 0.55 if left_is_purine else 0.45
        ratio_r = 1.0 - ratio_l

        midpoint = p0 + dir_norm * (length * ratio_l)
        q0 = p0 + dir_norm * (length * ratio_l * 0.5)
        q1 = midpoint + dir_norm * (length * ratio_r * 0.5)

        base_l = kit.primitive_object(f"Full_BaseL_{r}", "cylinder", mat_l,
                                     size=(0.0028, 0.0028, length * ratio_l * 0.88),
                                     location=(q0.x, q0.y, q0.z),
                                     rotation_euler=rot_euler)
        link_strictly(base_l, collection)
        objs.append(base_l)

        base_r = kit.primitive_object(f"Full_BaseR_{r}", "cylinder", mat_r,
                                     size=(0.0028, 0.0028, length * ratio_r * 0.88),
                                     location=(q1.x, q1.y, q1.z),
                                     rotation_euler=rot_euler)
        link_strictly(base_r, collection)
        objs.append(base_r)

        # Hydrogen bond junction bead
        h_node = kit.primitive_object(f"Full_HBond_{r}", "uv_sphere", mat_h,
                                     size=(0.0026, 0.0026, 0.0026),
                                     location=(midpoint.x, midpoint.y, midpoint.z))
        link_strictly(h_node, collection)
        objs.append(h_node)

    # 3. Directionality 5' and 3' Indicators
    badge_defs = [
        ("Full_Tag_5P_Strand1", (radius * math.cos(turns * 2 * math.pi + groove_offset) + 0.003,
                                 radius * math.sin(turns * 2 * math.pi + groove_offset),
                                 height * 0.5 + 0.004), mat_badge_5),
        ("Full_Tag_3P_Strand0", (radius * math.cos(turns * 2 * math.pi) + 0.003,
                                 radius * math.sin(turns * 2 * math.pi),
                                 height * 0.5 + 0.004), mat_badge_3),
        ("Full_Tag_3P_Strand1", (radius * math.cos(groove_offset) + 0.003,
                                 radius * math.sin(groove_offset),
                                 -height * 0.5 - 0.004), mat_badge_3),
        ("Full_Tag_5P_Strand0", (radius + 0.003, 0.0, -height * 0.5 - 0.004), mat_badge_5),
    ]
    for b_name, b_pos, b_mat in badge_defs:
        b_cube = kit.primitive_object(b_name, "cube", b_mat,
                                     size=(0.0045, 0.0045, 0.003),
                                     location=b_pos)
        link_strictly(b_cube, collection)
        objs.append(b_cube)

    # 4. Exhibition Stand & Support Armature
    stand_base = kit.primitive_object("Full_Stand_Base", "cylinder", mat_stand,
                                      size=(0.052, 0.052, 0.008),
                                      location=(0.0, 0.0, -height * 0.5 - 0.016))
    link_strictly(stand_base, collection)
    objs.append(stand_base)

    stand_pillar = kit.primitive_object("Full_Stand_Pillar", "cylinder", mat_brass,
                                        size=(0.004, 0.004, 0.024),
                                        location=(0.0, 0.0, -height * 0.5 - 0.006))
    link_strictly(stand_pillar, collection)
    objs.append(stand_pillar)

    return objs

def build_dna_detail(collection):
    """
    Constructs an unzipped, high-resolution chemical nucleotide ladder (NCERT Fig 6.2).
    Shows Deoxyribose pentose rings, Phosphate tetrahedral nodes, Purine fused rings,
    Pyrimidine rings, and stoichiometric dotted Hydrogen bonds (2 for A=T, 3 for G≡C).
    Zero empty gaps: bases touch the hydrogen bond interface precisely!
    """
    objs = []

    mat_sugar = kit.add_material("Detail_Sugar", COLOR_SUGAR, metallic=0.08, roughness=0.30)
    mat_phosphate = kit.add_material("Detail_Phosphate", COLOR_PHOSPHATE, metallic=0.12, roughness=0.25)
    mat_bond = kit.add_material("Detail_CovalentBond", (0.35, 0.40, 0.45), metallic=0.50, roughness=0.30)
    mat_a = kit.add_material("Detail_Adenine", COLOR_ADENINE, metallic=0.08, roughness=0.32)
    mat_t = kit.add_material("Detail_Thymine", COLOR_THYMINE, metallic=0.08, roughness=0.32)
    mat_g = kit.add_material("Detail_Guanine", COLOR_GUANINE, metallic=0.08, roughness=0.32)
    mat_c = kit.add_material("Detail_Cytosine", COLOR_CYTOSINE, metallic=0.08, roughness=0.32)
    mat_h = create_emissive_mat("Detail_HBond", COLOR_H_BOND, strength=8.0)

    # 3 horizontal base pair steps (A=T, G≡C, T=A)
    step_defs = [
        # (left_is_purine, mat_left, mat_right, num_h_bonds, name_prefix)
        (True,  mat_a, mat_t, 2, "A_T"),
        (True,  mat_g, mat_c, 3, "G_C"),
        (False, mat_t, mat_a, 2, "T_A"),
    ]

    ladder_spacing_z = 0.030
    strand_x_left = -0.026
    strand_x_right = 0.026

    for s_idx, (l_purine, m_left, m_right, h_count, step_name) in enumerate(step_defs):
        z_pos = (1 - s_idx) * ladder_spacing_z  # Top to bottom: s_idx=0 -> +z, s_idx=2 -> -z

        # 1. Left Deoxyribose Pentose Ring (Strand 1: 5' top to 3' bottom)
        sugar_l = create_regular_prism(f"Detail_Sugar_L_{s_idx}", 5, radius=0.0050, height=0.0022,
                                       material=mat_sugar, location=(strand_x_left, 0.0, z_pos),
                                       rotation_euler=(0, 0, math.radians(36)), collection=collection)
        objs.append(sugar_l)

        # 2. Right Deoxyribose Pentose Ring (Strand 2: Antiparallel 3' top to 5' bottom, inverted)
        sugar_r = create_regular_prism(f"Detail_Sugar_R_{s_idx}", 5, radius=0.0050, height=0.0022,
                                       material=mat_sugar, location=(strand_x_right, 0.0, z_pos),
                                       rotation_euler=(0, 0, math.radians(216)), collection=collection)
        objs.append(sugar_r)

        # 3. Phosphate Groups with Phosphodiester Linkages
        p_l = kit.primitive_object(f"Detail_Phosphate_L_{s_idx}", "uv_sphere", mat_phosphate,
                                   size=(0.0034, 0.0034, 0.0034),
                                   location=(strand_x_left - 0.006, 0.0, z_pos + 0.007))
        link_strictly(p_l, collection)
        objs.append(p_l)

        bond_l = kit.primitive_object(f"Detail_EsterBond_L_{s_idx}", "cylinder", mat_bond,
                                      size=(0.0012, 0.0012, 0.009),
                                      location=(strand_x_left - 0.003, 0.0, z_pos + 0.0035),
                                      rotation_euler=(0, math.radians(40), 0))
        link_strictly(bond_l, collection)
        objs.append(bond_l)

        p_r = kit.primitive_object(f"Detail_Phosphate_R_{s_idx}", "uv_sphere", mat_phosphate,
                                   size=(0.0034, 0.0034, 0.0034),
                                   location=(strand_x_right + 0.006, 0.0, z_pos - 0.007))
        link_strictly(p_r, collection)
        objs.append(p_r)

        bond_r = kit.primitive_object(f"Detail_EsterBond_R_{s_idx}", "cylinder", mat_bond,
                                      size=(0.0012, 0.0012, 0.009),
                                      location=(strand_x_right + 0.003, 0.0, z_pos - 0.0035),
                                      rotation_euler=(0, math.radians(-40), 0))
        link_strictly(bond_r, collection)
        objs.append(bond_r)

        # 4. Bases: Positioned so that they meet the hydrogen bond junction exactly at x = ±0.0025
        # Left Base
        if l_purine:
            # Purine extends from sugar (x = -0.018) to junction (x = -0.0025)
            b_objs = create_purine_base(f"Detail_BaseL_{s_idx}", m_left,
                                        location=Vector((strand_x_left + 0.014, 0.0, z_pos)),
                                        sign=+1, collection=collection)
            objs.extend(b_objs)
            # N-glycosidic link
            gly_l = kit.primitive_object(f"Detail_GlycoL_{s_idx}", "cylinder", mat_bond,
                                         size=(0.0012, 0.0012, 0.012),
                                         location=(strand_x_left + 0.007, 0.0, z_pos),
                                         rotation_euler=(0, math.radians(90), 0))
            link_strictly(gly_l, collection)
            objs.append(gly_l)
        else:
            # Pyrimidine is single ring from sugar (x = -0.016) to junction (x = -0.0025)
            b_objs = create_pyrimidine_base(f"Detail_BaseL_{s_idx}", m_left,
                                            location=Vector((-0.0065, 0.0, z_pos)),
                                            sign=+1, collection=collection)
            objs.extend(b_objs)
            gly_l = kit.primitive_object(f"Detail_GlycoL_{s_idx}", "cylinder", mat_bond,
                                         size=(0.0012, 0.0012, 0.012),
                                         location=((strand_x_left - 0.0065)*0.5 + 0.003, 0.0, z_pos),
                                         rotation_euler=(0, math.radians(90), 0))
            link_strictly(gly_l, collection)
            objs.append(gly_l)

        # Right Base
        r_purine = not l_purine
        if r_purine:
            # Purine extends from sugar (x = +0.018) to junction (x = +0.0025)
            b_objs = create_purine_base(f"Detail_BaseR_{s_idx}", m_right,
                                        location=Vector((strand_x_right - 0.014, 0.0, z_pos)),
                                        sign=-1, collection=collection)
            objs.extend(b_objs)
            gly_r = kit.primitive_object(f"Detail_GlycoR_{s_idx}", "cylinder", mat_bond,
                                         size=(0.0012, 0.0012, 0.012),
                                         location=(strand_x_right - 0.007, 0.0, z_pos),
                                         rotation_euler=(0, math.radians(90), 0))
            link_strictly(gly_r, collection)
            objs.append(gly_r)
        else:
            # Pyrimidine is single ring from sugar to junction
            b_objs = create_pyrimidine_base(f"Detail_BaseR_{s_idx}", m_right,
                                            location=Vector((0.0065, 0.0, z_pos)),
                                            sign=-1, collection=collection)
            objs.extend(b_objs)
            gly_r = kit.primitive_object(f"Detail_GlycoR_{s_idx}", "cylinder", mat_bond,
                                         size=(0.0012, 0.0012, 0.012),
                                         location=((strand_x_right + 0.0065)*0.5 - 0.003, 0.0, z_pos),
                                         rotation_euler=(0, math.radians(90), 0))
            link_strictly(gly_r, collection)
            objs.append(gly_r)

        # 5. Stoichiometric Hydrogen Bonds (2 for A=T, 3 for G≡C) bridging the central gap
        h_span_x = 0.0050
        if h_count == 2:
            y_offsets = [-0.0016, 0.0016]
        else:
            y_offsets = [-0.0024, 0.0, 0.0024]

        for h_i, y_off in enumerate(y_offsets):
            for dot_i in range(3):
                frac = (dot_i + 1) / 4.0
                hx = -h_span_x * 0.5 + frac * h_span_x
                h_dot = kit.primitive_object(f"Detail_HDot_{s_idx}_{h_i}_{dot_i}", "uv_sphere", mat_h,
                                             size=(0.0010, 0.0010, 0.0010),
                                             location=(hx, y_off, z_pos))
                link_strictly(h_dot, collection)
                objs.append(h_dot)

    # 6. Vertical Phosphodiester Backbone Connectors
    for s_i in range(len(step_defs) - 1):
        z_curr = (1 - s_i) * ladder_spacing_z
        z_next = (1 - (s_i + 1)) * ladder_spacing_z
        z_mid = (z_curr + z_next) * 0.5

        bb_l = kit.primitive_object(f"Detail_BB_StrandL_{s_i}", "cylinder", mat_bond,
                                   size=(0.0016, 0.0016, ladder_spacing_z),
                                   location=(strand_x_left - 0.005, 0.0, z_mid))
        link_strictly(bb_l, collection)
        objs.append(bb_l)

        bb_r = kit.primitive_object(f"Detail_BB_StrandR_{s_i}", "cylinder", mat_bond,
                                   size=(0.0016, 0.0016, ladder_spacing_z),
                                   location=(strand_x_right + 0.005, 0.0, z_mid))
        link_strictly(bb_r, collection)
        objs.append(bb_r)

    # 7. Directional 5' and 3' Terminal Badges
    tag_mat_5 = create_emissive_mat("Detail_Tag_5", (0.95, 0.35, 0.15), strength=6.0)
    tag_mat_3 = create_emissive_mat("Detail_Tag_3", (0.15, 0.65, 0.95), strength=6.0)

    # Left strand: 5' Top, 3' Bottom
    t5_l = kit.primitive_object("Detail_Tag_5P_L", "cube", tag_mat_5,
                                size=(0.005, 0.004, 0.004),
                                location=(strand_x_left - 0.005, 0.0, ladder_spacing_z + 0.010))
    link_strictly(t5_l, collection)
    objs.append(t5_l)

    t3_l = kit.primitive_object("Detail_Tag_3P_L", "cube", tag_mat_3,
                                size=(0.005, 0.004, 0.004),
                                location=(strand_x_left - 0.005, 0.0, -ladder_spacing_z - 0.010))
    link_strictly(t3_l, collection)
    objs.append(t3_l)

    # Right strand: 3' Top, 5' Bottom (Antiparallel)
    t3_r = kit.primitive_object("Detail_Tag_3P_R", "cube", tag_mat_3,
                                size=(0.005, 0.004, 0.004),
                                location=(strand_x_right + 0.005, 0.0, ladder_spacing_z + 0.010))
    link_strictly(t3_r, collection)
    objs.append(t3_r)

    t5_r = kit.primitive_object("Detail_Tag_5P_R", "cube", tag_mat_5,
                                size=(0.005, 0.004, 0.004),
                                location=(strand_x_right + 0.005, 0.0, -ladder_spacing_z - 0.010))
    link_strictly(t5_r, collection)
    objs.append(t5_r)

    return objs

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.18, -0.22, 0.16), (9.5, 9.6, 9.8), 5.5, 0.25),
        ("Fill_Light", 'AREA', (-0.20, -0.15, 0.10), (7.5, 7.8, 8.2), 3.2, 0.28),
        ("Rim_Light", 'SPOT', (0.0, 0.22, 0.18), (9.0, 9.2, 9.8), 4.5, 0.20),
        ("Bottom_Bounce", 'AREA', (0.0, -0.10, -0.12), (6.0, 6.5, 7.0), 2.0, 0.25),
    ]
    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.15
            light_data.spot_blend = 0.35
        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance=0.28, elev_deg=18, azim_deg=-30):
    elev_rad = math.radians(elev_deg)
    azim_rad = math.radians(azim_deg)
    cam_x = target_center.x + distance * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_center.y - distance * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_center.z + distance * math.sin(elev_rad)
    cam_obj.location = (cam_x, cam_y, cam_z)
    direction = target_center - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

    world = bpy.data.worlds.new("DNA_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.012, 0.015, 0.020, 1.0)
        bg.inputs["Strength"].default_value = 0.50
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: DNA_Full (B-DNA double helix with major/minor grooves & stand)
    col_full = bpy.data.collections.new("DNA_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_dna_full(col_full)

    # 2. Collection: DNA_Detail (Unzipped nucleotide subunit chain per NCERT Fig 6.2)
    col_detail = bpy.data.collections.new("DNA_Detail")
    bpy.context.scene.collection.children.link(col_detail)
    detail_objs = build_dna_detail(col_detail)

    cam_data = bpy.data.cameras.new("DNA_Camera")
    cam_data.lens = 65.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("DNA_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    # Export GLB with both collections active
    set_collection_visibility(full_objs, True)
    set_collection_visibility(detail_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    # Render Preview 1: DNA_Full
    set_collection_visibility(full_objs, True)
    set_collection_visibility(detail_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, -0.005)), distance=0.42, elev_deg=16, azim_deg=-28)
    kit.configure_render(width=1280, height=720, samples=24)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: DNA_Detail (Unzipped chemical nucleotide ladder)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(detail_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.0)), distance=0.175, elev_deg=22, azim_deg=-10)
    preview_detail = out_dir / "preview_section.png"
    kit.render_preview(preview_detail)
    print(f"Rendered: {preview_detail}")

    print("=== DNA DOUBLE HELIX BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
