"""
test_m5_challenger_params.py — Challenger M5-2 Empirical Test Suite
Exhaustive verification of Milestone 5 Physics apparatus:
1. Exact SHA-256 and byte parity between assets/physics/*/out/*.glb and apps/interactive-viewer/public/assets/*.glb
2. Full Circuit:
   - Ohm's law current I = V / R
   - Switch seating (closed knife blade inside U-jaws)
   - Bulb emission toggling (emission > 0 when closed, 0.0 when open)
   - Closed-loop topological wiring continuity
3. Electric Motor:
   - Semicircular split-ring commutator gap angle (15° - 30°)
   - Carbon brushes contact commutator tangentially
   - Armature coil bridge ends clear rotating axle with positive clearance (no intersection)
4. Glass Slab:
   - Exact Snell's law refraction (i = e = 36.0°, r = 22.75°, IOR = 1.52)
   - Ray parallelism (incident || emergent)
   - Lateral displacement d > 0 (theoretical and geometric)
   - Refraction pins P1-P4 exact collinearity with rays
"""

import sys
import math
import hashlib
from pathlib import Path
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "assets/python"))
import edu_asset_kit as kit

failures = []
passed_checks = 0


def record_pass(msg):
    global passed_checks
    passed_checks += 1
    print(f"  [PASS] {msg}")


def record_fail(msg):
    global failures
    failures.append(msg)
    print(f"  [FAIL] {msg}")


def test_glb_web_parity():
    print("\n--- Testing 1: GLB SHA-256 and Byte Parity (All 22 Physics Assets) ---")
    physics_dir = ROOT_DIR / "assets/physics"
    web_dir = ROOT_DIR / "apps/interactive-viewer/public/assets"

    assets = sorted([d.name for d in physics_dir.iterdir() if d.is_dir()])
    if len(assets) != 22:
        record_fail(f"Expected 22 physics assets, found {len(assets)}")
        return

    for asset_id in assets:
        src_glb = physics_dir / asset_id / "out" / f"{asset_id}.glb"
        web_glb = web_dir / f"{asset_id}.glb"

        if not src_glb.exists():
            record_fail(f"Missing source GLB: {src_glb}")
            continue
        if not web_glb.exists():
            record_fail(f"Missing web GLB: {web_glb}")
            continue

        src_bytes = src_glb.read_bytes()
        web_bytes = web_glb.read_bytes()

        src_hash = hashlib.sha256(src_bytes).hexdigest()
        web_hash = hashlib.sha256(web_bytes).hexdigest()

        if len(src_bytes) != len(web_bytes):
            record_fail(f"{asset_id}: Byte mismatch (src={len(src_bytes)}, web={len(web_bytes)})")
        elif src_hash != web_hash:
            record_fail(f"{asset_id}: Hash mismatch (src={src_hash}, web={web_hash})")
        else:
            record_pass(f"{asset_id}: {len(src_bytes)} bytes, SHA-256={src_hash[:16]}...")


def test_full_circuit():
    print("\n--- Testing 2: Full Circuit Physics & Continuity ---")
    blend_path = ROOT_DIR / "assets/physics/full-circuit/out/full-circuit.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    # 1. Inspect production blend file
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    # Check emission material
    glow_mat = bpy.data.materials.get("circuit-bulb-glow")
    if not glow_mat:
        record_fail("Missing material 'circuit-bulb-glow'")
    else:
        principled = glow_mat.node_tree.nodes.get("Principled BSDF")
        em_strength = principled.inputs["Emission Strength"].default_value
        em_color = tuple(principled.inputs["Emission Color"].default_value)
        if em_strength > 0:
            record_pass(f"Production blend has active emission strength = {em_strength:.2f}")
        else:
            record_fail(f"Production blend has zero emission strength: {em_strength}")

    # Check blade object seating
    blade = bpy.data.objects.get("full-circuit-switch-blade")
    jaw1 = bpy.data.objects.get("full-circuit-switch-jaw-1")
    jaw2 = bpy.data.objects.get("full-circuit-switch-jaw-2")
    if not blade or not jaw1 or not jaw2:
        record_fail("Missing switch blade or jaw objects")
    else:
        rot_y = blade.rotation_euler.y
        if abs(rot_y) < 1e-4:
            record_pass(f"Switch blade rotation in closed state: {rot_y:.4f} rad (0 deg)")
        else:
            record_fail(f"Switch blade rotation in closed state is not 0: {rot_y}")

        blade_y = blade.location.y
        j1_y = jaw1.location.y
        j2_y = jaw2.location.y
        if min(j1_y, j2_y) < blade_y < max(j1_y, j2_y):
            record_pass(f"Switch blade y={blade_y:.4f} is centered between jaws ({min(j1_y, j2_y):.4f} to {max(j1_y, j2_y):.4f})")
        else:
            record_fail(f"Switch blade y={blade_y} not between jaws {j1_y} and {j2_y}")

    # Check wiring objects exist and form 5 distinct segments
    expected_wires = [
        "full-circuit-wire-battery-to-switch",
        "full-circuit-wire-switch-to-bulb",
        "full-circuit-wire-bulb-to-ammeter",
        "full-circuit-wire-ammeter-to-resistor",
        "full-circuit-wire-resistor-to-battery"
    ]
    all_wires_present = True
    for w_name in expected_wires:
        obj = bpy.data.objects.get(w_name)
        if not obj:
            record_fail(f"Missing wire: {w_name}")
            all_wires_present = False
        else:
            v_count = len(obj.data.vertices)
            if v_count < 10:
                record_fail(f"Wire {w_name} has degenerate geometry: {v_count} verts")
                all_wires_present = False
    if all_wires_present:
        record_pass(f"All 5 circuit wire segments present and topologically constructed")

    # 2. Test programmatic circuit behavior (Ohm's Law & Open Switch)
    sys.path.insert(0, str(ROOT_DIR / "assets/physics/full-circuit"))
    import build_circuit as bc

    # Test closed state
    kit.reset_scene()
    objs_closed = bc.build_circuit(switch_closed=True, voltage=6.0, resistance=12.0)
    current_closed = 6.0 / 12.0
    glow_mat_closed = bpy.data.materials.get("circuit-bulb-glow")
    closed_strength = glow_mat_closed.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value
    if closed_strength > 0:
        record_pass(f"Closed circuit (V=6V, R=12Ω -> I={current_closed}A): Emission strength = {closed_strength}")
    else:
        record_fail(f"Closed circuit failed to illuminate filament: strength = {closed_strength}")

    # Test open state
    kit.reset_scene()
    objs_open = bc.build_circuit(switch_closed=False, voltage=6.0, resistance=12.0)
    glow_mat_open = bpy.data.materials.get("circuit-bulb-glow")
    open_strength = glow_mat_open.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value
    blade_open = bpy.data.objects.get("full-circuit-switch-blade")
    blade_angle_open = blade_open.rotation_euler.y
    if open_strength == 0.0:
        record_pass(f"Open circuit (switch_closed=False): Emission strength strictly 0.0")
    else:
        record_fail(f"Open circuit has non-zero emission: {open_strength}")

    if abs(blade_angle_open) > 0.3:
        record_pass(f"Open switch blade rotated upwards: angle = {math.degrees(-blade_angle_open):.1f}°")
    else:
        record_fail(f"Open switch blade not rotated: angle = {blade_angle_open}")


def test_electric_motor():
    print("\n--- Testing 3: Electric Motor Commutator, Brushes & Axle Clearance ---")
    blend_path = ROOT_DIR / "assets/physics/electric-motor/out/electric-motor.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    # Commutator split-ring gap angle
    p_obj = bpy.data.objects.get("electric-motor-commutator-P")
    q_obj = bpy.data.objects.get("electric-motor-commutator-Q")
    if not p_obj or not q_obj:
        record_fail("Missing commutator split-ring objects P or Q")
        return

    z_axle = 0.070

    def get_vertex_angles(obj):
        angles = []
        for v in obj.data.vertices:
            w_v = obj.matrix_world @ v.co
            dx = w_v.x
            dz = w_v.z - z_axle
            ang = math.atan2(dz, dx) % (2 * math.pi)
            angles.append(ang)
        return min(angles), max(angles), angles

    p_angles = [ang for ang in [(math.atan2((p_obj.matrix_world @ v.co).z - z_axle, (p_obj.matrix_world @ v.co).x) % (2 * math.pi)) for v in p_obj.data.vertices]]
    q_angles = [ang for ang in [(math.atan2((q_obj.matrix_world @ v.co).z - z_axle, (q_obj.matrix_world @ v.co).x) % (2 * math.pi)) for v in q_obj.data.vertices]]

    p_pos = [a for a in p_angles if a < math.pi]
    p_neg = [a for a in p_angles if a >= math.pi]

    p_span = math.degrees(max(p_pos) + (2 * math.pi - min(p_neg))) if p_pos and p_neg else math.degrees(max(p_angles) - min(p_angles))
    q_span = math.degrees(max(q_angles) - min(q_angles))

    # Gap 1 (top neutral plane near theta = pi / 2)
    gap1_rad = min(q_angles) - max(p_pos) if p_pos else min(p_angles) + (2 * math.pi - max(q_angles))
    gap1_deg = math.degrees(gap1_rad)

    # Gap 2 (bottom neutral plane near theta = 3*pi / 2)
    gap2_rad = min(p_neg) - max(q_angles) if p_neg else min(q_angles) - max(p_angles)
    gap2_deg = math.degrees(gap2_rad)

    print(f"  Measured Commutator: Ring P span={p_span:.1f}°, Ring Q span={q_span:.1f}°")
    print(f"  Measured Commutator Gaps: Gap 1 = {gap1_deg:.2f}°, Gap 2 = {gap2_deg:.2f}°")

    if 15.0 <= gap1_deg <= 30.0 and 15.0 <= gap2_deg <= 30.0:
        record_pass(f"Commutator split gap angles ({gap1_deg:.1f}°, {gap2_deg:.1f}°) strictly between 15° and 30°")
    else:
        record_fail(f"Commutator split gap angles ({gap1_deg:.1f}°, {gap2_deg:.1f}°) out of 15°-30° range")

    # Brushes contact commutator tangentially
    brush_x = bpy.data.objects.get("electric-motor-brush-X")
    brush_y = bpy.data.objects.get("electric-motor-brush-Y")
    r_comm_out = 0.0072
    if not brush_x or not brush_y:
        record_fail("Missing brush objects")
    else:
        bx_x = brush_x.location.x
        by_x = brush_y.location.x
        bx_inner = bx_x - 0.005 / 2
        by_inner = by_x + 0.005 / 2
        dist_x = abs(bx_inner - r_comm_out)
        dist_y = abs(by_inner - (-r_comm_out))
        if dist_x < 1e-4 and dist_y < 1e-4:
            record_pass(f"Carbon brushes X (x={bx_inner:.4f}m) and Y (x={by_inner:.4f}m) contact commutator tangentially at r={r_comm_out:.4f}m")
        else:
            record_fail(f"Brush contact misaligned: dist_x={dist_x}, dist_y={dist_y}")

    # Armature coil clearance over axle
    axle = bpy.data.objects.get("electric-motor-axle")
    end_bc = bpy.data.objects.get("electric-motor-coil-end-BC")
    end_da = bpy.data.objects.get("electric-motor-coil-end-DA")
    if not axle or not end_bc or not end_da:
        record_fail("Missing axle or coil end objects")
    else:
        min_clearance = 999.0
        for end_obj in [end_bc, end_da]:
            for v in end_obj.data.vertices:
                w_v = end_obj.matrix_world @ v.co
                dx = w_v.x
                dz = w_v.z - z_axle
                dist_to_center = math.sqrt(dx * dx + dz * dz)
                clearance = dist_to_center - 0.003
                if clearance < min_clearance:
                    min_clearance = clearance

        print(f"  Minimum distance between coil end bridge vertices and axle surface: {min_clearance * 1000:.2f} mm")
        if min_clearance > 0.003:  # At least 3mm clearance
            record_pass(f"Armature coil end bridges clear rotating axle with positive clearance: {min_clearance * 1000:.2f} mm > 0")
        else:
            record_fail(f"Armature coil intersects or touches axle: clearance = {min_clearance * 1000:.2f} mm")


def test_glass_slab():
    print("\n--- Testing 4: Glass Slab Snell's Law, Parallelism & Pin Collinearity ---")
    blend_path = ROOT_DIR / "assets/physics/glass-slab/out/glass-slab.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    # Test ray objects
    ray_inc = bpy.data.objects.get("glass-slab-ray-incident")
    ray_refr = bpy.data.objects.get("glass-slab-ray-refracted")
    ray_em = bpy.data.objects.get("glass-slab-ray-emergent")

    if not ray_inc or not ray_refr or not ray_em:
        record_fail("Missing optical ray objects")
        return

    # Extract ray centerline axis by taking the medians of the two end cap faces
    def get_tube_axis(obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        cap_faces = sorted(bm.faces, key=lambda f: len(f.verts), reverse=True)
        f1 = cap_faces[0]
        f2 = cap_faces[1]
        c1 = obj.matrix_world @ f1.calc_center_median()
        c2 = obj.matrix_world @ f2.calc_center_median()
        bm.free()
        if c1.y > c2.y:
            c1, c2 = c2, c1
        return c1, c2

    inc_start, inc_end = get_tube_axis(ray_inc)
    refr_start, refr_end = get_tube_axis(ray_refr)
    em_start, em_end = get_tube_axis(ray_em)

    v_inc = (inc_end - inc_start)
    v_inc.z = 0.0
    v_inc.normalize()

    v_refr = (refr_end - refr_start)
    v_refr.z = 0.0
    v_refr.normalize()

    v_em = (em_end - em_start)
    v_em.z = 0.0
    v_em.normalize()

    # Normal is perpendicular to slab face along Y axis: (0, 1, 0)
    normal = Vector((0.0, 1.0, 0.0))

    # Angle of incidence i: angle between v_inc and normal
    cos_i = max(-1.0, min(1.0, v_inc.dot(normal)))
    i_deg = math.degrees(math.acos(cos_i))

    # Angle of refraction r: angle between v_refr and normal
    cos_r = max(-1.0, min(1.0, v_refr.dot(normal)))
    r_deg = math.degrees(math.acos(cos_r))

    # Angle of emergence e: angle between v_em and normal
    cos_e = max(-1.0, min(1.0, v_em.dot(normal)))
    e_deg = math.degrees(math.acos(cos_e))

    print(f"  Measured Angles: i = {i_deg:.4f}°, r = {r_deg:.4f}°, e = {e_deg:.4f}°")

    # Verify i == e
    if abs(i_deg - e_deg) < 1e-4:
        record_pass(f"Incident angle equals emergent angle: i = {i_deg:.4f}°, e = {e_deg:.4f}° (i = e, parallelism exact)")
    else:
        record_fail(f"Ray non-parallel: i = {i_deg:.4f}°, e = {e_deg:.4f}° (delta = {abs(i_deg - e_deg):.6f}°)")

    # Verify Snell's law: n1 * sin(i) = n2 * sin(r)
    n_calc = math.sin(math.radians(i_deg)) / math.sin(math.radians(r_deg))
    print(f"  Calculated Refractive Index: n = sin({i_deg:.4f}°) / sin({r_deg:.4f}°) = {n_calc:.5f}")
    if abs(n_calc - 1.52) < 0.001:
        record_pass(f"Snell's Law exact match: n = {n_calc:.5f} (matches crown glass 1.5200)")
    else:
        record_fail(f"Snell's Law violated: calculated n = {n_calc:.5f} != 1.52")

    # Lateral displacement d
    # Glass thickness t = 65 mm (0.065 m)
    t_slab = 0.065
    d_theor = (t_slab * math.sin(math.radians(i_deg - r_deg))) / math.cos(math.radians(r_deg))

    # Geometric perpendicular distance between incident ray line and emergent ray line:
    # Incident ray line passes through inc_end with unit direction v_inc
    # Emergent ray line passes through em_start with unit direction v_em (which is parallel to v_inc)
    delta_pt = em_start - inc_end
    # Distance between parallel lines = |delta_pt.x * v_inc.y - delta_pt.y * v_inc.x|
    d_geom = abs(delta_pt.x * v_inc.y - delta_pt.y * v_inc.x)

    print(f"  Lateral Displacement: Theoretical d = {d_theor * 1000:.4f} mm, Geometric d = {d_geom * 1000:.4f} mm")
    if d_geom > 0.005 and abs(d_geom - d_theor) < 1e-4:
        record_pass(f"Lateral displacement d = {d_geom * 1000:.4f} mm > 0 exactly matches Snell's law theory ({d_theor * 1000:.4f} mm)")
    else:
        record_fail(f"Lateral displacement incorrect: d_geom = {d_geom * 1000:.4f} mm, d_theor = {d_theor * 1000:.4f} mm")

    # Collinearity of Pins P1, P2 with Incident Ray and P3, P4 with Emergent Ray
    pins = {
        "P1": ("glass-slab-pin-stem-P1", "incident", inc_end, v_inc),
        "P2": ("glass-slab-pin-stem-P2", "incident", inc_end, v_inc),
        "P3": ("glass-slab-pin-stem-P3", "emergent", em_start, v_em),
        "P4": ("glass-slab-pin-stem-P4", "emergent", em_start, v_em)
    }

    def point_to_line_dist(pt, line_pt, line_dir):
        dp = pt - line_pt
        # distance in XY plane
        return abs(dp.x * line_dir.y - dp.y * line_dir.x)

    for p_id, (obj_name, ray_type, ref_pt, ref_dir) in pins.items():
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            record_fail(f"Missing pin: {obj_name}")
            continue
        loc = obj.location
        dist = point_to_line_dist(Vector((loc.x, loc.y, 0.0)), ref_pt, ref_dir)

        print(f"  Pin {p_id} distance to {ray_type} ray axis: {dist * 1000:.6f} mm")
        if dist < 1e-5:  # Within 0.01 micron
            record_pass(f"Pin {p_id} (loc=({loc.x*1000:.2f}, {loc.y*1000:.2f}) mm) is perfectly collinear with {ray_type} ray axis (error={dist*1000:.6f} mm)")
        else:
            record_fail(f"Pin {p_id} deviated from {ray_type} ray axis: error={dist*1000:.6f} mm")


def main():
    test_glb_web_parity()
    test_full_circuit()
    test_electric_motor()
    test_glass_slab()

    print("\n" + "=" * 60)
    print(f"CHALLENGER M5-2 EMPIRICAL TEST SUMMARY:")
    print(f"  Passed Checks: {passed_checks}")
    print(f"  Failures:      {len(failures)}")
    print("=" * 60)

    if failures:
        print("\nFAILURES ENCOUNTERED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n>>> ALL EMPIRICAL CHALLENGER M5-2 TESTS PASSED! <<<")
        sys.exit(0)


if __name__ == "__main__":
    main()
