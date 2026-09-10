"""
build_stoma.py — Microscopic Leaf Stomatal Apparatus & Guard Cells
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'stoma'

def build_stoma():
    guard_mat = kit.add_material('guard-cyto', (0.35, 0.72, 0.38), metallic=0.05, roughness=0.35)
    inner_wall_mat = kit.add_material('guard-inner-wall', (0.15, 0.48, 0.22), metallic=0.1, roughness=0.4)
    chloro_mat = kit.add_material('chloroplast', (0.12, 0.62, 0.18), metallic=0.1, roughness=0.25)
    nucleus_mat = kit.add_material('cell-nucleus', (0.45, 0.22, 0.55), metallic=0.1, roughness=0.3)
    epider_mat = kit.add_material('epidermal-cell', (0.55, 0.82, 0.60), metallic=0.02, roughness=0.5)

    objects = []

def create_crescent_guard_cell(name, sign, mat):
    """
    Creates an authentic crescent/kidney-shaped guard cell in the XY plane (Z is UP).
    sign = -1 for Left Guard Cell, +1 for Right Guard Cell.
    Lies horizontally on a microscope slide peel, visible from the viewer camera.
    """
    bm = bmesh.new()
    num_slices = 28
    num_pts = 16
    
    slices = []
    for s in range(num_slices):
        t = s / (num_slices - 1)  # 0 to 1
        phi = -math.pi / 2 + t * math.pi  # -pi/2 to +pi/2
        
        # Centerline path in XY plane
        cx = sign * (0.0065 + 0.0165 * math.cos(phi))
        cy = 0.028 * math.sin(phi)
        cz = 0.0055
        
        # Tangent vector dT/dphi in XY plane
        dx = -sign * 0.0165 * math.sin(phi)
        dy = 0.028 * math.cos(phi)
        tangent = Vector((dx, dy, 0.0)).normalized()
        
        # In-plane normal vector N (perpendicular to tangent in XY plane)
        normal = Vector((-tangent.y, tangent.x, 0.0))
        if (normal.x * sign) < 0:
            normal = -normal
            
        # Out-of-plane binormal B (along Z axis)
        binormal = Vector((0.0, 0.0, 1.0))
        
        # Cross-sectional radius tapering towards junction poles
        r_scale = 0.0085 * (math.cos(phi) ** 0.42)
        r_scale = max(r_scale, 0.0018)
        
        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            # Elliptical cross section: slightly broader in XY, rounded along Z
            rx = r_scale * (1.05 + 0.15 * math.cos(theta))
            rz = r_scale * 0.85
            
            offset = normal * (rx * math.cos(theta)) + binormal * (rz * math.sin(theta))
            pos = Vector((cx, cy, cz)) + offset
            v = bm.verts.new(pos)
            ring.append(v)
        slices.append(ring)
        
    for s in range(num_slices - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            v1 = slices[s][i]
            v2 = slices[s][next_i]
            v3 = slices[s + 1][next_i]
            v4 = slices[s + 1][i]
            bm.faces.new([v1, v2, v3, v4])
            
    # Cap junction poles where guard cells meet
    pole_bot = bm.verts.new((0.0, -0.0285, 0.0055))
    pole_top = bm.verts.new((0.0, 0.0285, 0.0055))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][i], slices[0][next_i], pole_bot])
        bm.faces.new([slices[-1][i], pole_top, slices[-1][next_i]])
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    
    if mat:
        obj.data.materials.append(mat)
    return obj


def build_stoma():
    # Microscopic botanical PBR shaders
    glass_mat = kit.add_material('slide-glass', (0.88, 0.94, 0.95), roughness=0.10)
    bsdf = glass_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.85
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.52
    guard_mat = kit.add_material('guard-cyto', (0.22, 0.68, 0.28), metallic=0.02, roughness=0.30)
    inner_wall_mat = kit.add_material('guard-inner-wall', (0.08, 0.38, 0.12), metallic=0.05, roughness=0.25)
    chloro_mat = kit.add_material('chloroplast', (0.02, 0.52, 0.08), metallic=0.08, roughness=0.22)
    nucleus_mat = kit.add_material('cell-nucleus', (0.65, 0.18, 0.55), metallic=0.04, roughness=0.28)
    epider_mat = kit.add_material('epidermal-cell', (0.50, 0.80, 0.54), metallic=0.01, roughness=0.45)
    wall_ridge_mat = kit.add_material('epidermal-wall', (0.15, 0.48, 0.18), metallic=0.03, roughness=0.38)

    objects = []

    # 1. Clear Borosilicate Glass Microscope Slide (Stage base)
    slide = kit.primitive_object(
        f'{ASSET_ID}-glass-slide', 'cube', glass_mat,
        size=(0.100, 0.070, 0.0025),
        location=(0.0, 0.0, 0.00125)
    )
    objects.append(slide)

    # 2. Epidermal Peel Base Tissue (Thin translucent peel on slide)
    peel = kit.primitive_object(
        f'{ASSET_ID}-epidermal-peel', 'cube', epider_mat,
        size=(0.076, 0.056, 0.0015),
        location=(0.0, 0.0, 0.003)
    )
    objects.append(peel)

    # 3. Interlocking Epidermal Cell Wall Boundaries (Wavy jigsaw pavement lines)
    # Radiating cell wall dividers
    for i in range(6):
        ang = i * (math.pi / 3.0) + 0.18
        dx = math.cos(ang)
        dy = math.sin(ang)
        wall_div = kit.primitive_object(
            f'{ASSET_ID}-radial-wall-{i}', 'cube', wall_ridge_mat,
            size=(0.022, 0.0018, 0.002),
            location=(dx * 0.028, dy * 0.022, 0.0042)
        )
        wall_div.rotation_euler = (0, 0, ang)
        objects.append(wall_div)

    # Outer perimeter boundary ridge
    for i in range(6):
        ang1 = i * (math.pi / 3.0) + 0.18
        ang2 = (i + 1) * (math.pi / 3.0) + 0.18
        p1 = Vector((math.cos(ang1) * 0.036, math.sin(ang1) * 0.027, 0.0042))
        p2 = Vector((math.cos(ang2) * 0.036, math.sin(ang2) * 0.027, 0.0042))
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        rot_z = math.atan2(delta.y, delta.x)
        rim_seg = kit.primitive_object(
            f'{ASSET_ID}-rim-{i}', 'cube', wall_ridge_mat,
            size=(delta.length, 0.0018, 0.002),
            location=(mid.x, mid.y, mid.z)
        )
        rim_seg.rotation_euler = (0, 0, rot_z)
        objects.append(rim_seg)

    # 4. Paired Authentic Kidney-Shaped Guard Cells (Left & Right in XY plane)
    for sign, name in [(-1, 'left'), (1, 'right')]:
        guard_cell = create_crescent_guard_cell(f'{ASSET_ID}-guard-{name}', sign, guard_mat)
        objects.append(guard_cell)

        # Thickened Inner Cellulosic Wall bordering the Stomatal Aperture (Manifold capped)
        wall_pts = [
            (0.0, -0.025, 0.0055),
            (sign * 0.0035, -0.015, 0.0055),
            (sign * 0.0055, 0.0, 0.0055),
            (sign * 0.0035, 0.015, 0.0055),
            (0.0, 0.025, 0.0055),
        ]
        wall_obj = kit.create_smooth_tube(
            f'{ASSET_ID}-inner-wall-{name}', wall_pts, radius=0.0020, cap_ends=True, material=inner_wall_mat
        )
        objects.append(wall_obj)

        # Prominent Cell Nucleus
        nuc = kit.primitive_object(
            f'{ASSET_ID}-nucleus-{name}', 'uv_sphere', nucleus_mat,
            size=(0.008, 0.006, 0.007),
            location=(sign * 0.017, 0.0, 0.007)
        )
        objects.append(nuc)

        # Distinct Spherical Chloroplast Organelles (Guard cells specifically contain chloroplasts)
        chloro_coords = [
            (sign * 0.014, 0.018, 0.007),
            (sign * 0.017, 0.011, 0.007),
            (sign * 0.020, 0.005, 0.007),
            (sign * 0.020, -0.005, 0.007),
            (sign * 0.017, -0.011, 0.007),
            (sign * 0.014, -0.018, 0.007),
        ]
        for c_idx, (cx, cy, cz) in enumerate(chloro_coords):
            cp = kit.primitive_object(
                f'{ASSET_ID}-chloro-{name}-{c_idx}', 'uv_sphere', chloro_mat,
                size=(0.0048, 0.0040, 0.0048),
                location=(cx, cy, cz)
            )
            objects.append(cp)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_stoma()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
