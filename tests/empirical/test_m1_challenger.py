"""
Empirical Test Harness for Milestone 1 Primitives (Challenger M1-1)
Focus:
- edu_asset_kit.create_smooth_tube topology, manifoldness, edge cases
- edu_asset_kit.add_tissue_material Blender 4.2 LTS Principled BSDF SSS sockets
- edu_asset_kit.add_material_from_token SSS integration
"""

import sys
import math
from pathlib import Path

# Add python library paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))

import bpy
import bmesh
from mathutils import Vector
import edu_asset_kit as kit

def analyze_mesh_topology(mesh):
    """Inspects mesh manifoldness and topological properties."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    total_verts = len(bm.verts)
    total_edges = len(bm.edges)
    total_faces = len(bm.faces)

    boundary_edges = [e for e in bm.edges if e.is_boundary]
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
    zero_area_faces = [f for f in bm.faces if f.calc_area() <= 1e-12]

    bm.free()

    return {
        "verts": total_verts,
        "edges": total_edges,
        "faces": total_faces,
        "boundary_edges": len(boundary_edges),
        "non_manifold_edges": len(non_manifold_edges),
        "non_manifold_verts": len(non_manifold_verts),
        "zero_area_faces": len(zero_area_faces)
    }

def run_tests():
    print("=" * 70)
    print("RUNNING CHALLENGER M1-1 EMPIRICAL TESTS")
    print("=" * 70)

    results = []

    def report(name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if details:
            print(f"       Details: {details}")
        results.append((name, passed, details))

    # -------------------------------------------------------------
    # Test Suite 1: Geometry — create_smooth_tube
    # -------------------------------------------------------------
    print("\n--- Test Suite 1: Geometry — create_smooth_tube ---")

    # Case 1.1: 2-point tube (basic segment)
    kit.reset_scene()
    tube_2pt = kit.create_smooth_tube("tube_2pt", [(0, 0, 0), (0, 0, 1)], radius=0.01, resolution=16, cap_ends=True)
    top_2pt = analyze_mesh_topology(tube_2pt.data)
    p = (top_2pt["non_manifold_edges"] == 0 and top_2pt["boundary_edges"] == 0 and top_2pt["non_manifold_verts"] == 0)
    report("1.1 2-point tube capped manifold check", p, f"{top_2pt}")

    # Case 1.2: 10-point spline tube (smooth spiral)
    kit.reset_scene()
    pts_10 = [(math.cos(i * 0.6) * 0.1, math.sin(i * 0.6) * 0.1, i * 0.02) for i in range(10)]
    tube_10pt = kit.create_smooth_tube("tube_10pt", pts_10, radius=0.005, resolution=16, cap_ends=True)
    top_10pt = analyze_mesh_topology(tube_10pt.data)
    p = (top_10pt["non_manifold_edges"] == 0 and top_10pt["boundary_edges"] == 0 and top_10pt["non_manifold_verts"] == 0)
    report("1.2 10-point spiral tube capped manifold check", p, f"{top_10pt}")

    # Case 1.3: Closed-loop spline (first point == last point)
    kit.reset_scene()
    pts_closed = [(0, 0, 0), (0.1, 0, 0), (0.1, 0.1, 0), (0, 0.1, 0), (0, 0, 0)]
    tube_closed = kit.create_smooth_tube("tube_closed", pts_closed, radius=0.005, resolution=16, cap_ends=True)
    top_closed = analyze_mesh_topology(tube_closed.data)
    p = (top_closed["non_manifold_edges"] == 0 and top_closed["boundary_edges"] == 0)
    report("1.3 Closed-loop tube capped manifold check", p, f"{top_closed}")

    # Case 1.4: Colinear points
    kit.reset_scene()
    pts_colinear = [(0, 0, 0), (0.02, 0, 0), (0.05, 0, 0), (0.1, 0, 0), (0.15, 0, 0)]
    tube_colinear = kit.create_smooth_tube("tube_colinear", pts_colinear, radius=0.004, resolution=16, cap_ends=True)
    top_colinear = analyze_mesh_topology(tube_colinear.data)
    p = (top_colinear["non_manifold_edges"] == 0 and top_colinear["boundary_edges"] == 0)
    report("1.4 Colinear points tube capped manifold check", p, f"{top_colinear}")

    # Case 1.5: Sharp turns (90-degree orthogonal corner)
    kit.reset_scene()
    pts_sharp = [(0, 0, 0), (0.1, 0, 0), (0.1, 0.1, 0)]
    tube_sharp = kit.create_smooth_tube("tube_sharp", pts_sharp, radius=0.005, resolution=16, cap_ends=True)
    top_sharp = analyze_mesh_topology(tube_sharp.data)
    p = (top_sharp["non_manifold_edges"] == 0 and top_sharp["boundary_edges"] == 0)
    report("1.5 Sharp 90-degree turn tube capped manifold check", p, f"{top_sharp}")

    # Case 1.6: Hairpin 180-degree turn (Loop of Henle anatomy stress test)
    kit.reset_scene()
    pts_hairpin = [(0, 0, 0.1), (0, 0, 0.01), (0.005, 0, 0.00), (0.01, 0, 0.01), (0.01, 0, 0.1)]
    tube_hairpin = kit.create_smooth_tube("tube_hairpin", pts_hairpin, radius=0.002, resolution=16, cap_ends=True)
    top_hairpin = analyze_mesh_topology(tube_hairpin.data)
    p = (top_hairpin["non_manifold_edges"] == 0 and top_hairpin["boundary_edges"] == 0)
    report("1.6 Hairpin turn (Henle loop) capped manifold check", p, f"{top_hairpin}")

    # Case 1.7: Uncapped tube behavior (cap_ends=False)
    kit.reset_scene()
    tube_uncapped = kit.create_smooth_tube("tube_uncapped", [(0, 0, 0), (0, 0, 1)], radius=0.01, resolution=16, cap_ends=False)
    top_uncapped = analyze_mesh_topology(tube_uncapped.data)
    p = (top_uncapped["boundary_edges"] > 0)
    report("1.7 Uncapped tube respects cap_ends=False", p, f"boundary_edges={top_uncapped['boundary_edges']}")

    # Case 1.8: Degenerate input handling (< 2 points raises ValueError)
    try:
        kit.create_smooth_tube("tube_invalid", [(0, 0, 0)], radius=0.01)
        report("1.8 Degenerate single point rejects with ValueError", False, "No error raised")
    except ValueError as e:
        report("1.8 Degenerate single point rejects with ValueError", True, f"Caught expected: {e}")

    # -------------------------------------------------------------
    # Test Suite 2: Shaders — add_tissue_material & Tokens
    # -------------------------------------------------------------
    print("\n--- Test Suite 2: Shaders — add_tissue_material & Tokens ---")

    kit.reset_scene()
    mat_default = kit.add_tissue_material("test_tissue_default")
    nodes = mat_default.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    p_bsdf = (bsdf is not None)
    report("2.1 Principled BSDF node exists in tissue material", p_bsdf)

    # Check sockets via dict(bsdf.inputs.items()) to handle Blender 4.2 bpy_prop_collection quirks
    input_dict = dict(bsdf.inputs.items())
    weight_input = input_dict.get("Subsurface Weight") or input_dict.get("Subsurface")
    radius_input = input_dict.get("Subsurface Radius")
    scale_input = input_dict.get("Subsurface Scale")
    ior_input = input_dict.get("Subsurface IOR")

    p_sockets = (weight_input is not None and radius_input is not None and scale_input is not None and ior_input is not None)
    report("2.2 Blender 4.2 LTS Principled BSDF SSS sockets exist", p_sockets,
           f"Weight: {weight_input.name if weight_input else None}, "
           f"Radius: {radius_input.name if radius_input else None}, "
           f"Scale: {scale_input.name if scale_input else None}, "
           f"IOR: {ior_input.name if ior_input else None}")

    # Check assigned values
    val_weight = weight_input.default_value if weight_input else None
    val_radius = tuple(radius_input.default_value) if radius_input else None
    val_scale = scale_input.default_value if scale_input else None
    val_ior = ior_input.default_value if ior_input else None

    p_vals = (abs(val_weight - 0.3) < 1e-4 and
              val_radius == (1.0, 0.20000000298023224, 0.10000000149011612) and
              abs(val_scale - 0.02) < 1e-4 and
              abs(val_ior - 1.40) < 1e-3)
    report("2.3 SSS socket default values match specification", p_vals,
           f"weight={val_weight}, radius={val_radius}, scale={val_scale}, ior={val_ior}")

    # Case 2.4: Hex color input support
    mat_hex = kit.add_tissue_material("test_hex", base_color="#991b1b")
    bsdf_hex = mat_hex.node_tree.nodes["Principled BSDF"]
    color_hex = tuple(bsdf_hex.inputs["Base Color"].default_value)
    report("2.4 Hex string color support (#991b1b)", len(color_hex) == 4 and color_hex[0] > 0.3, f"color={color_hex}")

    # Case 2.5: 3-tuple RGB float color support
    mat_rgb = kit.add_tissue_material("test_rgb", base_color=(0.9, 0.3, 0.2))
    bsdf_rgb = mat_rgb.node_tree.nodes["Principled BSDF"]
    color_rgb = tuple(bsdf_rgb.inputs["Base Color"].default_value)
    p_rgb = all(abs(a - b) < 1e-4 for a, b in zip(color_rgb, (0.9, 0.3, 0.2, 1.0)))
    report("2.5 3-tuple RGB float color support", p_rgb, f"color={color_rgb}")

    # Case 2.6: Design Tokens biological tissue presets integration
    tokens_to_test = [
        "tissueMuscle", "tissueOrgan", "tissueNerve", "tissueFat",
        "tissueSclera", "tissueRetina", "tissueCortex", "tissueBone", "tissue_myocardium"
    ]
    tokens_passed = True
    token_details = []
    for t_key in tokens_to_test:
        mat_tok = kit.add_material_from_token(f"mat_{t_key}", t_key)
        bsdf_tok = mat_tok.node_tree.nodes["Principled BSDF"]
        sw = bsdf_tok.inputs["Subsurface Weight"].default_value
        sr = tuple(bsdf_tok.inputs["Subsurface Radius"].default_value)
        ss = bsdf_tok.inputs["Subsurface Scale"].default_value
        if sw <= 0.0 or ss <= 0.0 or len(sr) != 3:
            tokens_passed = False
            token_details.append(f"{t_key}: FAIL (w={sw}, r={sr}, s={ss})")
        else:
            token_details.append(f"{t_key}: OK (w={sw})")

    report("2.6 Biological tissue design tokens instantiate with SSS", tokens_passed, "; ".join(token_details))

    # Case 2.7: Blender 4.2 Subsurface IOR collection lookup observation
    # Notice: In Blender 4.2, 'Subsurface IOR' in bsdf.inputs returns False due to RNA collection lookup,
    # but dict(bsdf.inputs.items())['Subsurface IOR'] successfully accesses it and default is 1.40.
    ior_in_col = "Subsurface IOR" in bsdf.inputs
    ior_in_dict = "Subsurface IOR" in input_dict
    report("2.7 Subsurface IOR lookup behavior documented", ior_in_dict,
           f"in_collection={ior_in_col}, in_dict={ior_in_dict}, default={val_ior}")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    total_tests = len(results)
    passed_tests = sum(1 for _, p, _ in results if p)
    failed_tests = total_tests - passed_tests
    print(f"SUMMARY: {passed_tests}/{total_tests} passed ({failed_tests} failed)")
    print("=" * 70)

    if failed_tests > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
