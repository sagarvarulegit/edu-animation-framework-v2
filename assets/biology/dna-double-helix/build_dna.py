"""
build_dna.py — High-Fidelity B-DNA Double Helix Model
CBSE Class 10 Biology, Chapter 8: How do Organisms Reproduce? (DNA Copying)
CBSE Class 11 Biology, Chapter 9: Biomolecules (Nucleic Acids) (Fig 9.5)
CBSE Class 12 Biology, Chapter 6: Molecular Basis of Inheritance (Fig 6.2, 6.3)

Key Anatomical / Structural Features:
- Two antiparallel polynucleotide sugar-phosphate backbones coiled in a right-handed double helix.
- Authentic Major Groove (~2.2 nm) and Minor Groove (~1.2 nm) created by ~140° / 220° angular offset.
- Nitrogenous base pairs oriented strictly horizontally (perpendicular to helical axis, zero vertical slope).
- Complementary base pairing per Watson-Crick rules:
  * Adenine (A, Green) pairs with Thymine (T, Red)
  * Guanine (G, Amber) pairs with Cytosine (C, Blue)
- Design token color synchronization:
  * Backbone (Phosphate): Azure (#0ea5e9)
  * Adenine: Green (#22c55e)
  * Thymine: Red (#ef4444)
  * Guanine: Amber (#f59e0b)
  * Cytosine: Blue (#3b82f6)
- ZERO non-manifold elements: backbones constructed via kit.create_smooth_tube(..., cap_ends=True),
  base pair rungs are closed manifold cylinders.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "dna-double-helix"


def build_dna():
    # 1. PBR Materials synchronized with visual/design-tokens.json
    backbone_mat = kit.add_material("dna-backbone", (0.055, 0.647, 0.914), metallic=0.10, roughness=0.35)
    mat_a = kit.add_material("dna-adenine", (0.133, 0.773, 0.369), metallic=0.05, roughness=0.45)   # Green
    mat_t = kit.add_material("dna-thymine", (0.937, 0.267, 0.267), metallic=0.05, roughness=0.45)   # Red
    mat_g = kit.add_material("dna-guanine", (0.961, 0.620, 0.043), metallic=0.05, roughness=0.45)   # Amber
    mat_c = kit.add_material("dna-cytosine", (0.231, 0.510, 0.965), metallic=0.05, roughness=0.45)  # Blue
    h_bond_mat = kit.add_material("dna-h-bond", (0.95, 0.95, 0.98), metallic=0.10, roughness=0.25)

    radius = 0.014      # Helix radius (1.4 cm in visualization scale)
    height = 0.120      # Total height along Y axis (12 cm)
    turns = 2.2         # 2.2 helical turns
    steps = 44          # Spline sample resolution along helix

    # Major and Minor Groove Offset:
    # In B-DNA, the two glycosidic bonds are separated by ~140 degrees (minor groove) and ~220 degrees (major groove)
    groove_offset = math.radians(140.0)

    objects = []

    # 2. Helical Sugar-Phosphate Backbones (Strand 0 and Strand 1)
    for strand in range(2):
        strand_pts = []
        base_angle_offset = strand * groove_offset
        for i in range(steps + 1):
            t = i / steps
            angle = t * turns * 2.0 * math.pi + base_angle_offset
            y = -height / 2.0 + t * height
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            strand_pts.append((x, y, z))

        # Build smooth manifold tube with capped ends (0 non-manifold edges)
        strand_obj = kit.create_smooth_tube(
            f"{ASSET_ID}-backbone-{strand}", strand_pts, radius=0.0022, cap_ends=True, material=backbone_mat
        )
        objects.append(strand_obj)

    # 3. Horizontal Base Pair Rungs Connecting the Two Antiparallel Strands
    # Standard Watson-Crick base pair sequence: [ (A, T), (G, C), (T, A), (C, G) ]
    pair_sequence = [
        (mat_a, mat_t, "A-T"),
        (mat_g, mat_c, "G-C"),
        (mat_t, mat_a, "T-A"),
        (mat_c, mat_g, "C-G"),
        (mat_a, mat_t, "A-T"),
        (mat_g, mat_c, "G-C"),
        (mat_c, mat_g, "C-G"),
        (mat_t, mat_a, "T-A"),
    ]

    # Sample base pair steps along the double helix
    num_rungs = 22
    for r_idx in range(num_rungs):
        t = r_idx / (num_rungs - 1)
        angle0 = t * turns * 2.0 * math.pi
        angle1 = angle0 + groove_offset
        y = -height / 2.0 + t * height

        # Coordinates on Strand 0 and Strand 1 at this exact height y
        x0 = radius * math.cos(angle0)
        z0 = radius * math.sin(angle0)
        x1 = radius * math.cos(angle1)
        z1 = radius * math.sin(angle1)

        p0 = Vector((x0, y, z0))
        p1 = Vector((x1, y, z1))

        # Vector D lies strictly in the horizontal X-Z plane (dy = 0)
        disp = p1 - p0
        length = disp.length
        if length < 0.0001:
            continue

        dir_norm = disp.normalized()
        # Rotation aligning Blender's cylinder Z-axis to horizontal vector dir_norm
        rot_euler = dir_norm.to_track_quat('Z', 'Y').to_euler()

        midpoint = (p0 + p1) * 0.5
        q0 = p0 + dir_norm * (length * 0.25)
        q1 = p0 + dir_norm * (length * 0.75)

        base_pair_type = pair_sequence[r_idx % len(pair_sequence)]
        mat_0 = base_pair_type[0]
        mat_1 = base_pair_type[1]

        # Base from strand 0 to midpoint (half-length)
        base_a = kit.primitive_object(
            f"{ASSET_ID}-pair-{r_idx}-base-0", "cylinder", mat_0,
            size=(0.0024, 0.0024, length * 0.46),
            location=(q0.x, q0.y, q0.z),
            rotation_euler=rot_euler
        )
        # Base from strand 1 to midpoint (half-length)
        base_b = kit.primitive_object(
            f"{ASSET_ID}-pair-{r_idx}-base-1", "cylinder", mat_1,
            size=(0.0024, 0.0024, length * 0.46),
            location=(q1.x, q1.y, q1.z),
            rotation_euler=rot_euler
        )
        # Central hydrogen bond interface node
        h_node = kit.primitive_object(
            f"{ASSET_ID}-pair-{r_idx}-h-bond", "uv_sphere", h_bond_mat,
            size=(0.0026, 0.0026, 0.0026),
            location=(midpoint.x, midpoint.y, midpoint.z)
        )
        objects.extend([base_a, base_b, h_node])

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_dna()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=55.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
