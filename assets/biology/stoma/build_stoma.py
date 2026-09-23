"""
build_stoma.py — Microscopic Leaf Stomatal Apparatus & Guard Cells (NCERT Class 10 Fig 5.3)
CBSE Class 10 Science Chapter 5: Life Processes (Nutrition & Respiration in Plants)
Figure 5.3: (a) Open and (b) closed stomatal pore
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'stoma'

# Botanical Histology Colors (Calibrated for AgX High-Contrast)
COLOR_GUARD_CYTO = (0.05, 0.32, 0.10)      # Rich chlorophyll cellular green
COLOR_INNER_WALL = (0.012, 0.08, 0.02)     # Thickened, inelastic, rigid inner wall
COLOR_OUTER_WALL = (0.12, 0.45, 0.16)      # Thin, flexible outer wall
COLOR_CHLOROPLAST = (0.008, 0.18, 0.02)    # Vivid deep green photosynthetic disks
COLOR_NUCLEUS = (0.55, 0.06, 0.35)         # Distinct magenta/purple chromatin
COLOR_VACUOLE = (0.15, 0.55, 0.75)         # Translucent cellular sap vacuole
COLOR_EPIDERMAL = (0.18, 0.38, 0.20)       # Epidermal pavement cell cytoplasm
COLOR_EPIDERMAL_WALL = (0.04, 0.18, 0.06)  # Pavement cell wall boundary
COLOR_SUBSTOMA = (0.005, 0.015, 0.008)     # Deep dark substomatal air chamber
COLOR_VAPOR = (0.45, 0.88, 1.00)           # Transpiring H2O vapor beads

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

def create_guard_cell_mesh(name, sign, is_open, mat_cyto, mat_inner_wall, collection):
    """
    Procedurally constructs an anatomically precise kidney-shaped guard cell.
    sign = -1 for Left Guard Cell, +1 for Right Guard Cell.
    is_open = True (Turgid, outward bowed pore) vs False (Flaccid, touching inner walls).
    """
    bm = bmesh.new()
    num_slices = 36
    num_pts = 16

    half_len_y = 0.0350

    slices = []
    inner_wall_pts = []

    for s in range(num_slices):
        t = s / (num_slices - 1)  # 0 to 1
        phi = -math.pi * 0.5 + t * math.pi  # -pi/2 to +pi/2
        cos_p = math.cos(phi)
        sin_p = math.sin(phi)

        if is_open:
            # Turgid, kidney-shaped: inner edge bows outward creating stomatal aperture
            inner_x = sign * (0.0070 * (cos_p ** 0.8))
            cell_w  = 0.0125 * (cos_p ** 0.35) + 0.0020
            outer_x = inner_x + sign * cell_w
        else:
            # Flaccid, straight: inner edge meets midline x = 0 (touching)
            inner_x = sign * 0.0002
            cell_w  = 0.0095 * (cos_p ** 0.35) + 0.0015
            outer_x = inner_x + sign * cell_w

        cx = (inner_x + outer_x) * 0.5
        cy = half_len_y * sin_p
        cz = 0.0060

        # Semi-axes of cross section
        rx = abs(outer_x - inner_x) * 0.5
        rz = 0.0060 * (cos_p ** 0.35) + 0.0010

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            # theta = 0 -> outer edge (+sign * rx)
            # theta = pi -> inner edge (-sign * rx)
            px = cx + math.cos(theta) * rx * sign
            py = cy
            pz = cz + math.sin(theta) * rz
            v = bm.verts.new((px, py, pz))
            ring.append(v)

        slices.append(ring)
        inner_wall_pts.append(Vector((inner_x, cy, cz)))

    for s in range(num_slices - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            bm.faces.new([slices[s][i], slices[s][next_i],
                          slices[s + 1][next_i], slices[s + 1][i]])

    # Cap poles at junction tips
    pole_bot = bm.verts.new((0.0, -half_len_y - 0.0005, 0.0060))
    pole_top = bm.verts.new((0.0,  half_len_y + 0.0005, 0.0060))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][i], slices[0][next_i], pole_bot])
        bm.faces.new([slices[-1][i], pole_top, slices[-1][next_i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_cyto)
    link_strictly(obj, collection)

    # 2. Thickened Inelastic Inner Cellulose Wall along the pore aperture
    bm_w = bmesh.new()
    w_res = 10
    w_thick = 0.0026 if is_open else 0.0020
    w_rings = []
    for pt in inner_wall_pts:
        ring = []
        for r_i in range(w_res):
            ang = 2.0 * math.pi * r_i / w_res
            vx = pt.x + math.cos(ang) * (w_thick * 0.7) * sign
            vy = pt.y
            vz = pt.z + math.sin(ang) * (w_thick * 1.1)
            ring.append(bm_w.verts.new((vx, vy, vz)))
        w_rings.append(ring)

    for s in range(len(inner_wall_pts) - 1):
        for r_i in range(w_res):
            next_r = (r_i + 1) % w_res
            bm_w.faces.new([w_rings[s][r_i], w_rings[s][next_r],
                            w_rings[s+1][next_r], w_rings[s+1][r_i]])

    bm_w.faces.new(w_rings[0])
    bm_w.faces.new(list(reversed(w_rings[-1])))
    bmesh.ops.recalc_face_normals(bm_w, faces=bm_w.faces)
    mesh_w = bpy.data.meshes.new(f"{name}_InnerWall")
    bm_w.to_mesh(mesh_w)
    bm_w.free()
    for p in mesh_w.polygons:
        p.use_smooth = True
    inner_wall_obj = bpy.data.objects.new(f"{name}_InnerWall", mesh_w)
    inner_wall_obj.data.materials.append(mat_inner_wall)
    link_strictly(inner_wall_obj, collection)

    return obj, inner_wall_obj

def build_organelles(prefix, sign, is_open, mat_nuc, mat_chloro, mat_vac, collection):
    objs = []
    cx_base = sign * (0.0135 if is_open else 0.0050)

    # 1. Prominent Kidney Guard Cell Nucleus
    nuc_pos = Vector((cx_base + sign * 0.001, 0.006, 0.0090))
    nuc = kit.primitive_object(f"{prefix}_Nucleus_{sign}", "uv_sphere", mat_nuc,
                               size=(0.007, 0.006, 0.005),
                               location=nuc_pos)
    link_strictly(nuc, collection)
    objs.append(nuc)

    # 2. Central Vacuole (Turgid and swollen in open; contracted in closed)
    vac_size = (0.009, 0.024, 0.0065) if is_open else (0.005, 0.016, 0.004)
    vac_pos = Vector((cx_base + sign * 0.0005, -0.004, 0.0080))
    vac = kit.primitive_object(f"{prefix}_Vacuole_{sign}", "uv_sphere", mat_vac,
                               size=vac_size,
                               location=vac_pos)
    link_strictly(vac, collection)
    objs.append(vac)

    # 3. Green Photosynthetic Chloroplasts (8 distinct lens-shaped organelles per guard cell)
    chloro_offsets = [
        ( 0.002,  0.022),
        ( 0.005,  0.016),
        ( 0.006,  0.009),
        ( 0.006, -0.010),
        ( 0.005, -0.017),
        ( 0.002, -0.023),
        (-0.002,  0.018),
        (-0.002, -0.017),
    ]

    for c_i, (ox, oy) in enumerate(chloro_offsets):
        cp_pos = Vector((cx_base + sign * ox, oy, 0.0085))
        cp = kit.primitive_object(f"{prefix}_Chloroplast_{sign}_{c_i}", "uv_sphere", mat_chloro,
                                 size=(0.0038, 0.0038, 0.0022),
                                 location=cp_pos)
        link_strictly(cp, collection)
        objs.append(cp)

    return objs

def build_epidermal_pavement(prefix, mat_peel, mat_wall, collection):
    objs = []
    # 1. Base Epidermal Leaf Layer
    peel_w, peel_l, peel_h = 0.140, 0.120, 0.003
    peel = kit.primitive_object(f"{prefix}_Epidermal_Pavement_Base", "cube", mat_peel,
                                size=(peel_w, peel_l, peel_h),
                                location=(0.0, 0.0, peel_h * 0.5))
    link_strictly(peel, collection)
    objs.append(peel)

    # 2. Interlocking Cell Walls of surrounding epidermal pavement cells
    cell_angles = [30, 75, 120, 160, 205, 250, 290, 335]
    for idx, deg in enumerate(cell_angles):
        rad = math.radians(deg)
        dx = math.cos(rad)
        dy = math.sin(rad)
        p_start = Vector((dx * 0.025, dy * 0.030, peel_h))
        p_mid   = Vector((dx * 0.040 + math.sin(rad * 3) * 0.004, dy * 0.044 - math.cos(rad * 3) * 0.004, peel_h))
        p_end   = Vector((dx * 0.062, dy * 0.054, peel_h))

        pts = [p_start, p_mid, p_end]
        for p_i in range(len(pts) - 1):
            v1, v2 = pts[p_i], pts[p_i + 1]
            diff = v2 - v1
            wall_seg = kit.primitive_object(f"{prefix}_Epidermal_Wall_{idx}_{p_i}", "cube", mat_wall,
                                           size=(0.0020, diff.length, 0.0028),
                                           location=((v1.x + v2.x)*0.5, (v1.y + v2.y)*0.5, peel_h + 0.0014))
            wall_seg.rotation_euler = (0.0, 0.0, math.atan2(diff.y, diff.x) - math.pi * 0.5)
            link_strictly(wall_seg, collection)
            objs.append(wall_seg)

    # Epidermal Cell Nuclei (Epidermal cells have nuclei, but NO chloroplasts)
    mat_epi_nuc = kit.add_material(f"{prefix}_epi_nuc", (0.42, 0.16, 0.38), metallic=0.04, roughness=0.35)
    epi_nuc_coords = [
        (-0.044,  0.034),
        ( 0.044,  0.032),
        (-0.046, -0.030),
        ( 0.045, -0.031),
        ( 0.000,  0.048),
        ( 0.000, -0.048),
    ]
    for n_i, (nx, ny) in enumerate(epi_nuc_coords):
        enuc = kit.primitive_object(f"{prefix}_Epi_Nucleus_{n_i}", "uv_sphere", mat_epi_nuc,
                                   size=(0.0055, 0.0048, 0.0035),
                                   location=(nx, ny, peel_h + 0.0018))
        link_strictly(enuc, collection)
        objs.append(enuc)

    return objs

def build_stoma_apparatus(prefix, is_open, collection):
    objs = []

    # Calibrated Materials
    mat_glass = kit.add_material(f"{prefix}_glass_slide", (0.85, 0.90, 0.94), roughness=0.08)
    bsdf_glass = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_glass and "Transmission Weight" in bsdf_glass.inputs:
        bsdf_glass.inputs["Transmission Weight"].default_value = 0.88

    mat_cyto = kit.add_material(f"{prefix}_guard_cyto", COLOR_GUARD_CYTO, metallic=0.01, roughness=0.30, transmission=0.20, subsurface_weight=0.30)
    mat_inner_wall = kit.add_material(f"{prefix}_inner_wall", COLOR_INNER_WALL, metallic=0.02, roughness=0.20)
    mat_chloro = kit.add_material(f"{prefix}_chloroplast", COLOR_CHLOROPLAST, metallic=0.04, roughness=0.18)
    mat_nuc = kit.add_material(f"{prefix}_nucleus", COLOR_NUCLEUS, metallic=0.03, roughness=0.25)
    mat_vac = kit.add_material(f"{prefix}_vacuole", COLOR_VACUOLE, metallic=0.01, roughness=0.22)
    if bsdf := mat_vac.node_tree.nodes.get("Principled BSDF"):
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.65

    mat_peel = kit.add_material(f"{prefix}_peel_base", COLOR_EPIDERMAL, metallic=0.01, roughness=0.38)
    mat_wall = kit.add_material(f"{prefix}_peel_wall", COLOR_EPIDERMAL_WALL, metallic=0.02, roughness=0.30)
    mat_substoma = kit.add_material(f"{prefix}_substoma_cavity", COLOR_SUBSTOMA, metallic=0.0, roughness=0.80)

    # 1. Borosilicate Glass Slide Base
    slide_w, slide_l, slide_h = 0.170, 0.140, 0.003
    slide = kit.primitive_object(f"{prefix}_Glass_Slide", "cube", mat_glass,
                                size=(slide_w, slide_l, slide_h),
                                location=(0.0, 0.0, -slide_h * 0.5))
    link_strictly(slide, collection)
    objs.append(slide)

    # 2. Interlocking Epidermal Pavement Tissue
    objs.extend(build_epidermal_pavement(prefix, mat_peel, mat_wall, collection))

    # 3. Substomatal Cavity (Dark chamber directly under the pore, visible only when open)
    if is_open:
        cavity = kit.primitive_object(f"{prefix}_Substomatal_Cavity", "uv_sphere", mat_substoma,
                                     size=(0.016, 0.046, 0.006),
                                     location=(0.0, 0.0, 0.001))
        link_strictly(cavity, collection)
        objs.append(cavity)

    # 4. Paired Guard Cells (Left = -1, Right = +1)
    for sign in [-1, 1]:
        sname = "Left" if sign < 0 else "Right"
        gc_obj, wall_obj = create_guard_cell_mesh(f"{prefix}_GuardCell_{sname}", sign, is_open, mat_cyto, mat_inner_wall, collection)
        objs.append(gc_obj)
        if wall_obj:
            objs.append(wall_obj)

        org_objs = build_organelles(f"{prefix}_{sname}", sign, is_open, mat_nuc, mat_chloro, mat_vac, collection)
        objs.extend(org_objs)

    # 5. Transpiration Water Vapor Stream (Only in Open state)
    if is_open:
        mat_vapor = create_emissive_mat(f"{prefix}_transpiration_vapor", COLOR_VAPOR, strength=10.0)
        vapor_coords = [
            ( 0.000,  0.000, 0.009),
            ( 0.001,  0.008, 0.014),
            (-0.001, -0.008, 0.015),
            ( 0.002,  0.016, 0.021),
            (-0.002, -0.015, 0.023),
            ( 0.000,  0.002, 0.028),
            ( 0.003, -0.004, 0.034),
            (-0.002,  0.006, 0.037),
        ]
        for v_i, (vx, vy, vz) in enumerate(vapor_coords):
            v_size = 0.0014 + v_i * 0.0002
            vapor_bead = kit.primitive_object(f"{prefix}_Vapor_{v_i}", "uv_sphere", mat_vapor,
                                              size=(v_size, v_size, v_size),
                                              location=(vx, vy, vz))
            link_strictly(vapor_bead, collection)
            objs.append(vapor_bead)

    return objs

def setup_microscope_lighting():
    lights = [
        ("Key_Condenser", 'AREA', (0.10, -0.12, 0.18), (9.5, 9.5, 9.2), 3.2, 0.20),
        ("Fill_Illuminator", 'AREA', (-0.12, -0.10, 0.15), (7.8, 8.0, 8.5), 2.2, 0.22),
        ("Top_Rim", 'SPOT', (0.0, 0.14, 0.16), (8.5, 8.8, 9.2), 2.8, 0.18),
    ]

    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.10
            light_data.spot_blend = 0.35

        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance=0.185, elev_deg=56, azim_deg=-20):
    elev_rad = math.radians(elev_deg)
    azim_rad = math.radians(azim_deg)

    cam_x = target_center.x + distance * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_center.y - distance * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_center.z + distance * math.sin(elev_rad)

    cam_obj.location = (cam_x, cam_y, cam_z)

    direction = target_center - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

    world = bpy.data.worlds.new("Stoma_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.012, 0.016, 0.018, 1.0)
        bg.inputs["Strength"].default_value = 0.4
    bpy.context.scene.world = world

    setup_microscope_lighting()

    # 1. Collection: Stoma_Open (NCERT Fig 5.3a - Turgid Guard Cells, Wide Aperture & Transpiration Stream)
    col_open = bpy.data.collections.new("Stoma_Open")
    bpy.context.scene.collection.children.link(col_open)
    open_objs = build_stoma_apparatus("Open", is_open=True, collection=col_open)

    # 2. Collection: Stoma_Closed (NCERT Fig 5.3b - Flaccid Guard Cells, Closed Pore & Touching Inner Walls)
    col_closed = bpy.data.collections.new("Stoma_Closed")
    bpy.context.scene.collection.children.link(col_closed)
    closed_objs = build_stoma_apparatus("Closed", is_open=False, collection=col_closed)

    cam_data = bpy.data.cameras.new("Microscope_Camera")
    cam_data.lens = 65.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Microscope_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    set_collection_visibility(open_objs, True)
    set_collection_visibility(closed_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    # Render Preview 1: Stoma_Open (Fig 5.3a)
    set_collection_visibility(open_objs, True)
    set_collection_visibility(closed_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.006)), distance=0.185, elev_deg=56, azim_deg=-20)
    kit.configure_render(width=1280, height=720, samples=24)
    preview_open = out_dir / "preview.png"
    kit.render_preview(preview_open)
    print(f"Rendered: {preview_open}")

    # Render Preview 2: Stoma_Closed (Fig 5.3b)
    set_collection_visibility(open_objs, False)
    set_collection_visibility(closed_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.006)), distance=0.185, elev_deg=56, azim_deg=-20)
    preview_closed = out_dir / "preview_section.png"
    kit.render_preview(preview_closed)
    print(f"Rendered: {preview_closed}")

    print("=== STOMA APPARATUS BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()

