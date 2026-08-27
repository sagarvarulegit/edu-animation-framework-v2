import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "human-heart"


def build_heart():
    """
    Anatomical human heart — anterior view.
    Technique: Skin modifier + Subdivision Surface for organic shape.
    FIXED: 3D skeleton (Y-depth for anterior/posterior), proper vessel diameters,
    right pulmonary veins, all objects returned for camera framing.
    """

    # === MATERIALS ===
    muscle = kit.add_material("heart-myocardium", (0.65, 0.16, 0.12), metallic=0.0, roughness=0.7)
    oxy = kit.add_material("heart-oxy", (0.82, 0.15, 0.12), metallic=0.0, roughness=0.5)
    deoxy = kit.add_material("heart-deoxy", (0.22, 0.30, 0.70), metallic=0.0, roughness=0.5)
    aorta_mat = kit.add_material("heart-aorta", (0.72, 0.18, 0.14), metallic=0.0, roughness=0.55)
    pulmonary = kit.add_material("heart-pulmonary", (0.32, 0.38, 0.72), metallic=0.0, roughness=0.50)
    fat = kit.add_material("heart-fat", (0.85, 0.75, 0.42), metallic=0.0, roughness=0.6)
    coronary = kit.add_material("heart-coronary", (0.90, 0.30, 0.25), metallic=0.0, roughness=0.5)

    # === HEART BODY — 3D skeleton (Y-depth for anterior/posterior) ===
    # FIXED: Previous version had all Y=0 (flat 2D). Now proper 3D:
    # - RV/LV anterior (Y > 0), atria posterior (Y < 0)
    # - Apex anterior-leftward tilt
    bm = bmesh.new()

    # Skeleton vertices with TRUE 3D coordinates
    # Y-positive = anterior (toward viewer), Y-negative = posterior
    v_top = bm.verts.new((0.0, -0.005, 0.04))         # Top (base, slightly posterior)
    v_upper_mid = bm.verts.new((0.0, 0.0, 0.02))       # Upper middle
    v_mid = bm.verts.new((0.0, 0.005, 0.0))            # Center (anterior bulge)
    v_lower_mid = bm.verts.new((-0.005, 0.003, -0.015))  # Lower mid
    v_apex = bm.verts.new((-0.012, 0.005, -0.03))      # Apex (anterior-left)

    # Right border (RV/RA) — anterior
    v_right_upper = bm.verts.new((0.025, -0.003, 0.015))   # RA (posterior)
    v_right_mid = bm.verts.new((0.028, 0.008, 0.0))        # RV (anterior bulge)
    v_right_lower = bm.verts.new((0.018, 0.005, -0.015))   # Lower RV

    # Left border (LV/LA) — LV anterior, LA posterior
    v_left_upper = bm.verts.new((-0.018, -0.008, 0.012))   # LA (posterior)
    v_left_mid = bm.verts.new((-0.022, 0.004, -0.005))     # LV (anterior)
    v_left_lower = bm.verts.new((-0.015, 0.003, -0.022))   # Lower LV

    # Connect skeleton edges
    bm.edges.new([v_top, v_upper_mid])
    bm.edges.new([v_upper_mid, v_mid])
    bm.edges.new([v_mid, v_lower_mid])
    bm.edges.new([v_lower_mid, v_apex])
    bm.edges.new([v_top, v_right_upper])
    bm.edges.new([v_right_upper, v_right_mid])
    bm.edges.new([v_right_mid, v_right_lower])
    bm.edges.new([v_right_lower, v_apex])
    bm.edges.new([v_top, v_left_upper])
    bm.edges.new([v_left_upper, v_left_mid])
    bm.edges.new([v_left_mid, v_left_lower])
    bm.edges.new([v_left_lower, v_apex])
    bm.edges.new([v_upper_mid, v_right_upper])
    bm.edges.new([v_upper_mid, v_left_upper])
    bm.edges.new([v_mid, v_right_mid])
    bm.edges.new([v_mid, v_left_mid])
    bm.edges.new([v_lower_mid, v_right_lower])
    bm.edges.new([v_lower_mid, v_left_lower])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-skeleton")
    bm.to_mesh(mesh)
    bm.free()

    skeleton = bpy.data.objects.new(f"{ASSET_ID}-skeleton", mesh)
    bpy.context.collection.objects.link(skeleton)
    skeleton.data.materials.append(muscle)

    # Skin modifier
    skin = skeleton.modifiers.new(name="Skin", type='SKIN')
    sv = skeleton.data.skin_vertices[0].data
    sv[0].radius = (0.020, 0.020)    # Top
    sv[1].radius = (0.022, 0.022)    # Upper mid
    sv[2].radius = (0.025, 0.025)    # Center
    sv[3].radius = (0.018, 0.018)    # Lower mid
    sv[4].radius = (0.008, 0.008)    # Apex
    sv[5].radius = (0.018, 0.018)    # Right upper
    sv[6].radius = (0.022, 0.022)    # Right mid
    sv[7].radius = (0.012, 0.012)    # Right lower
    sv[8].radius = (0.015, 0.015)    # Left upper
    sv[9].radius = (0.020, 0.020)    # Left mid
    sv[10].radius = (0.010, 0.010)   # Left lower

    # Subdivision Surface
    subdiv = skeleton.modifiers.new(name="Subsurf", type='SUBSURF')
    subdiv.levels = 3
    subdiv.render_levels = 3

    # Apply modifiers
    bpy.context.view_layer.objects.active = skeleton
    bpy.ops.object.modifier_apply(modifier="Skin")
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    all_objects = [skeleton]

    # === AORTA — proportional diameters ===
    # Real anatomy: ascending aorta ~3cm diameter, arch ~2.5cm
    # Scaled to our model: ascending 0.012, arch 0.010, descending 0.009

    # Ascending aorta (from LV, anterior)
    a1 = kit.primitive_object(f"{ASSET_ID}-aorta-asc", "cylinder", aorta_mat,
                               size=(0.012, 0.012, 0.022),
                               location=(0.005, -0.003, 0.045),
                               rotation_euler=(0.1, 0.0, 0.0))
    all_objects.append(a1)

    # Aortic arch (curves posteriorly)
    a2 = kit.primitive_object(f"{ASSET_ID}-aorta-arch", "cylinder", aorta_mat,
                               size=(0.010, 0.010, 0.014),
                               location=(0.002, -0.012, 0.056),
                               rotation_euler=(1.3, 0.0, 0.2))
    all_objects.append(a2)

    # Descending aorta
    a3 = kit.primitive_object(f"{ASSET_ID}-aorta-desc", "cylinder", aorta_mat,
                               size=(0.009, 0.009, 0.020),
                               location=(-0.002, -0.018, 0.042),
                               rotation_euler=(0.2, 0.0, 0.0))
    all_objects.append(a3)

    # Three branches from aortic arch (correct anatomy)
    a4 = kit.primitive_object(f"{ASSET_ID}-brachiocephalic", "cylinder", aorta_mat,
                               size=(0.005, 0.005, 0.012),
                               location=(0.010, -0.008, 0.062))
    all_objects.append(a4)
    a5 = kit.primitive_object(f"{ASSET_ID}-left-carotid", "cylinder", aorta_mat,
                               size=(0.004, 0.004, 0.012),
                               location=(0.003, -0.008, 0.064))
    all_objects.append(a5)
    a6 = kit.primitive_object(f"{ASSET_ID}-left-subclavian", "cylinder", aorta_mat,
                               size=(0.004, 0.004, 0.010),
                               location=(-0.005, -0.008, 0.062))
    all_objects.append(a6)

    # === PULMONARY TRUNK — from RV, anterior ===
    p1 = kit.primitive_object(f"{ASSET_ID}-pulmonary-trunk", "cylinder", pulmonary,
                               size=(0.010, 0.010, 0.020),
                               location=(0.010, 0.008, 0.042),
                               rotation_euler=(-0.15, 0.1, 0.0))
    all_objects.append(p1)

    # Left pulmonary artery
    p2 = kit.primitive_object(f"{ASSET_ID}-pulmonary-left", "cylinder", pulmonary,
                               size=(0.006, 0.006, 0.014),
                               location=(-0.008, 0.0, 0.056),
                               rotation_euler=(0.0, 0.0, 0.8))
    all_objects.append(p2)

    # Right pulmonary artery
    p3 = kit.primitive_object(f"{ASSET_ID}-pulmonary-right", "cylinder", pulmonary,
                               size=(0.006, 0.006, 0.014),
                               location=(0.022, 0.0, 0.056),
                               rotation_euler=(0.0, 0.0, -0.8))
    all_objects.append(p3)

    # === VENA CAVA — from RA, posterior ===
    # Superior vena cava (from above, enters RA)
    v1 = kit.primitive_object(f"{ASSET_ID}-svc", "cylinder", deoxy,
                               size=(0.009, 0.009, 0.024),
                               location=(0.024, -0.005, 0.040))
    all_objects.append(v1)

    # Inferior vena cava (from below, enters RA)
    v2 = kit.primitive_object(f"{ASSET_ID}-ivc", "cylinder", deoxy,
                               size=(0.009, 0.009, 0.020),
                               location=(0.022, -0.008, -0.025))
    all_objects.append(v2)

    # === PULMONARY VEINS — enter LA (posterior) ===
    # Left pulmonary veins (2)
    pv1 = kit.primitive_object(f"{ASSET_ID}-pulm-vein-l1", "cylinder", oxy,
                                size=(0.005, 0.005, 0.012),
                                location=(-0.022, -0.010, 0.024),
                                rotation_euler=(0.0, 0.0, 0.5))
    all_objects.append(pv1)
    pv2 = kit.primitive_object(f"{ASSET_ID}-pulm-vein-l2", "cylinder", oxy,
                                size=(0.005, 0.005, 0.012),
                                location=(-0.022, -0.012, 0.017),
                                rotation_euler=(0.0, 0.0, 0.3))
    all_objects.append(pv2)

    # Right pulmonary veins (2) — FIXED: added missing right veins
    pv3 = kit.primitive_object(f"{ASSET_ID}-pulm-vein-r1", "cylinder", oxy,
                                size=(0.005, 0.005, 0.012),
                                location=(0.022, -0.012, 0.022),
                                rotation_euler=(0.0, 0.0, -0.5))
    all_objects.append(pv3)
    pv4 = kit.primitive_object(f"{ASSET_ID}-pulm-vein-r2", "cylinder", oxy,
                                size=(0.005, 0.005, 0.012),
                                location=(0.022, -0.014, 0.015),
                                rotation_euler=(0.0, 0.0, -0.3))
    all_objects.append(pv4)

    # === CORONARY ARTERIES ===
    # Left anterior descending (LAD) — runs in anterior interventricular sulcus
    c1 = kit.primitive_object(f"{ASSET_ID}-lad", "cylinder", coronary,
                               size=(0.002, 0.002, 0.028),
                               location=(0.005, 0.010, -0.005),
                               rotation_euler=(0.3, 0.0, 0.1))
    all_objects.append(c1)

    # Right coronary artery (RCA) — runs in right AV groove
    c2 = kit.primitive_object(f"{ASSET_ID}-rca", "cylinder", coronary,
                               size=(0.002, 0.002, 0.022),
                               location=(0.022, 0.010, 0.01),
                               rotation_euler=(0.0, 0.0, -0.3))
    all_objects.append(c2)

    # Circumflex artery — runs in left AV groove
    c3 = kit.primitive_object(f"{ASSET_ID}-circumflex", "cylinder", coronary,
                               size=(0.002, 0.002, 0.018),
                               location=(-0.015, 0.008, 0.008),
                               rotation_euler=(0.0, 0.0, 0.8))
    all_objects.append(c3)

    # === EPICARDIAL FAT ===
    f1 = kit.primitive_object(f"{ASSET_ID}-av-groove", "cube", fat,
                               size=(0.042, 0.003, 0.003),
                               location=(0.0, 0.010, 0.008))
    all_objects.append(f1)
    f2 = kit.primitive_object(f"{ASSET_ID}-fat-1", "cylinder", fat,
                               size=(0.008, 0.008, 0.002),
                               location=(0.015, 0.010, 0.015))
    all_objects.append(f2)
    f3 = kit.primitive_object(f"{ASSET_ID}-fat-2", "cylinder", fat,
                               size=(0.006, 0.006, 0.002),
                               location=(-0.010, 0.010, -0.018))
    all_objects.append(f3)

    return all_objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_heart()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
