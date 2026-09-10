"""
build_trophic_pyramid.py — 4-Tier 3D Ecological Step Pyramid & 10% Energy Flow
CBSE Class 10 Biology, Chapter 15: Our Environment (Fig 15.2)
CBSE Class 12 Biology, Chapter 14: Ecosystem — Energy Flow (Fig 14.4)

Features:
- 4 Stepped Ecological Tiers representing Lindeman's 10% Energy Transfer:
  * Tier 0: Producers (10,000 J, Lush Green)
  * Tier 1: Herbivores / Primary Consumers (1,000 J, Golden Yellow)
  * Tier 2: Carnivores / Secondary Consumers (100 J, Orange)
  * Tier 3: Apex Predators / Tertiary Consumers (10 J, Crimson Red)
- White highlight borders demarcating tier boundaries.
- Ascending luminescent energy loss indicator arrow with manifold non-degenerate cone head.
- Clean manifold topology with zero non-manifold elements.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'trophic-level-pyramid'


def build_trophic_pyramid():
    t1_green = kit.add_material('tier1-producers', (0.12, 0.65, 0.32), metallic=0.10, roughness=0.35)
    t2_gold = kit.add_material('tier2-herbivores', (0.88, 0.72, 0.18), metallic=0.10, roughness=0.35)
    t3_orange = kit.add_material('tier3-carnivores', (0.92, 0.45, 0.14), metallic=0.10, roughness=0.35)
    t4_red = kit.add_material('tier4-apex', (0.85, 0.15, 0.18), metallic=0.10, roughness=0.35)
    accent_mat = kit.add_material('pyramid-trim', (0.95, 0.95, 0.98), metallic=0.15, roughness=0.20)
    arrow_mat = kit.add_material('energy-arrow', (0.22, 0.74, 0.97), metallic=0.10, roughness=0.25)
    arrow_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.22, 0.74, 0.97, 1.0)
    arrow_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.5

    objects = []

    # 4 Stepped Tiers (Width, Height, Z_center, Material, Energy Label)
    tier_specs = [
        (0.180, 0.032, 0.016, t1_green, 'producers-10000J'),
        (0.130, 0.032, 0.048, t2_gold, 'herbivores-1000J'),
        (0.085, 0.032, 0.080, t3_orange, 'carnivores-100J'),
        (0.045, 0.032, 0.112, t4_red, 'apex-10J'),
    ]

    for idx, (width, h, z_pos, mat, name) in enumerate(tier_specs):
        tier = kit.primitive_object(
            f'{ASSET_ID}-tier-{idx}', 'cube', mat,
            size=(width, width, h),
            location=(0.0, 0.0, z_pos)
        )
        objects.append(tier)

        # White highlight border around tier top edge
        trim = kit.primitive_object(
            f'{ASSET_ID}-trim-{idx}', 'cube', accent_mat,
            size=(width + 0.002, width + 0.002, 0.002),
            location=(0.0, 0.0, z_pos + h / 2)
        )
        objects.append(trim)

    # Ascending Energy Loss Arrow along Left Side (-X)
    arrow_shaft = kit.primitive_object(
        f'{ASSET_ID}-arrow-shaft', 'cylinder', arrow_mat,
        size=(0.004, 0.004, 0.12),
        location=(-0.115, 0.0, 0.065)
    )

    # Non-degenerate solid 3D cone arrow head (radius = 0.006, depth = 0.018)
    bm_head = bmesh.new()
    bmesh.ops.create_cone(
        bm_head, cap_ends=True, cap_tris=True, segments=32,
        radius1=0.006, radius2=0.0, depth=0.018
    )
    bmesh.ops.recalc_face_normals(bm_head, faces=bm_head.faces)
    head_mesh = bpy.data.meshes.new(f'{ASSET_ID}-arrow-head-mesh')
    bm_head.to_mesh(head_mesh)
    bm_head.free()
    for p in head_mesh.polygons:
        p.use_smooth = True
    arrow_head = bpy.data.objects.new(f'{ASSET_ID}-arrow-head', head_mesh)
    bpy.context.collection.objects.link(arrow_head)
    arrow_head.location = (-0.115, 0.0, 0.132)
    arrow_head.data.materials.append(arrow_mat)

    objects.extend([arrow_shaft, arrow_head])

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_trophic_pyramid()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')


if __name__ == '__main__':
    main()
