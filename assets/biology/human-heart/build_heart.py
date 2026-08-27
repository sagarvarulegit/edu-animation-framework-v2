import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "human-heart"


def build_heart():
    """
    Anatomical human heart — anterior view, sagittal cross-section.
    Based on medical illustration proportions:
    - Conical shape, apex pointing down-left
    - Right side more anterior, left side posterior
    - Left ventricle has thicker wall than right
    - Aorta arches upward and posterior
    - Pulmonary trunk exits anteriorly from right ventricle
    - SVC/IVC enter right atrium from above/below
    """

    # === MATERIALS ===
    muscle = kit.add_material("heart-myocardium", (0.68, 0.18, 0.14), metallic=0.0, roughness=0.65)
    inner_wall = kit.add_material("heart-endocardium", (0.82, 0.55, 0.50), metallic=0.0, roughness=0.5)
    oxy_blood = kit.add_material("heart-oxy-blood", (0.85, 0.12, 0.10), metallic=0.0, roughness=0.45)
    deoxy_blood = kit.add_material("heart-deoxy-blood", (0.20, 0.28, 0.68), metallic=0.0, roughness=0.45)
    valve_mat = kit.add_material("heart-valve", (0.88, 0.78, 0.68), metallic=0.0, roughness=0.35)
    aorta_mat = kit.add_material("heart-aorta", (0.75, 0.20, 0.15), metallic=0.0, roughness=0.55)
    pulmonary_mat = kit.add_material("heart-pulmonary", (0.30, 0.35, 0.70), metallic=0.0, roughness=0.50)
    fat_mat = kit.add_material("heart-fat", (0.85, 0.75, 0.40), metallic=0.0, roughness=0.6)

    # === HEART BODY — Conical shape using bmesh ===
    # Create a proper anatomical heart silhouette (anterior view)
    # The heart is roughly conical: wide at base (top), narrow at apex (bottom-left)
    bm = bmesh.new()

    # Heart outline points — anatomical shape (NOT emoji heart!)
    # Base is wide, apex points down and to the left
    # Right border is convex, left border is more straight
    outline_points = [
        # Start at right atrium (upper right)
        (0.025, 0.0, 0.035),
        (0.030, 0.0, 0.025),
        (0.032, 0.0, 0.015),
        # Right ventricle border (convex right side)
        (0.030, 0.0, 0.005),
        (0.025, 0.0, -0.005),
        (0.018, 0.0, -0.015),
        # Apex (bottom, pointing left)
        (0.008, 0.0, -0.030),
        (-0.002, 0.0, -0.038),
        (-0.010, 0.0, -0.035),
        # Left ventricle border (left side)
        (-0.018, 0.0, -0.025),
        (-0.022, 0.0, -0.015),
        (-0.025, 0.0, -0.005),
        # Left atrium (upper left)
        (-0.023, 0.0, 0.008),
        (-0.018, 0.0, 0.018),
        (-0.010, 0.0, 0.028),
        # Top (base of heart)
        (0.000, 0.0, 0.035),
        (0.010, 0.0, 0.038),
        (0.020, 0.0, 0.037),
    ]

    # Create front face vertices
    front_verts = []
    for x, y, z in outline_points:
        front_verts.append(bm.verts.new((x, y, z)))

    # Create back face vertices (slightly smaller, offset posteriorly)
    back_verts = []
    for x, y, z in outline_points:
        back_verts.append(bm.verts.new((x * 0.85, y - 0.02, z * 0.85)))

    bm.verts.ensure_lookup_table()

    # Create front face
    for i in range(len(front_verts)):
        j = (i + 1) % len(front_verts)
        try:
            bm.faces.new([front_verts[i], front_verts[j], back_verts[j], back_verts[i]])
        except:
            pass

    # Create mesh
    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    heart_body = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(heart_body)
    heart_body.data.materials.append(muscle)

    # === INTERVENTRICULAR SEPTUM ===
    kit.primitive_object(f"{ASSET_ID}-septum", "cube", inner_wall,
                          size=(0.002, 0.018, 0.05),
                          location=(0.0, -0.005, -0.005))

    # === RIGHT ATRIUM (upper right, receives deoxygenated blood) ===
    kit.primitive_object(f"{ASSET_ID}-right-atrium", "cylinder", deoxy_blood,
                          size=(0.018, 0.018, 0.018),
                          location=(0.018, -0.005, 0.02))

    # === LEFT ATRIUM (upper left, receives oxygenated blood) ===
    kit.primitive_object(f"{ASSET_ID}-left-atrium", "cylinder", oxy_blood,
                          size=(0.016, 0.016, 0.016),
                          location=(-0.012, -0.008, 0.02))

    # === RIGHT VENTRICLE (lower right, thinner wall) ===
    kit.primitive_object(f"{ASSET_ID}-right-ventricle", "cylinder", deoxy_blood,
                          size=(0.020, 0.020, 0.022),
                          location=(0.012, -0.006, -0.008))

    # === LEFT VENTRICLE (lower left, THICKER wall — key anatomical feature) ===
    kit.primitive_object(f"{ASSET_ID}-left-ventricle", "cylinder", oxy_blood,
                          size=(0.022, 0.022, 0.028),
                          location=(-0.008, -0.008, -0.012))

    # Left ventricle outer wall (thick myocardium)
    kit.primitive_object(f"{ASSET_ID}-lv-wall", "cylinder", muscle,
                          size=(0.028, 0.028, 0.028),
                          location=(-0.008, -0.006, -0.012))

    # === AORTA (large vessel arching upward from left ventricle) ===
    # Ascending aorta
    kit.primitive_object(f"{ASSET_ID}-aorta-asc", "cylinder", aorta_mat,
                          size=(0.012, 0.012, 0.025),
                          location=(-0.005, -0.005, 0.042),
                          rotation_euler=(0.15, 0.0, 0.0))

    # Aortic arch (curves posteriorly)
    kit.primitive_object(f"{ASSET_ID}-aorta-arch", "cylinder", aorta_mat,
                          size=(0.012, 0.012, 0.015),
                          location=(-0.005, -0.012, 0.055),
                          rotation_euler=(1.2, 0.0, 0.0))

    # Descending aorta
    kit.primitive_object(f"{ASSET_ID}-aorta-desc", "cylinder", aorta_mat,
                          size=(0.010, 0.010, 0.02),
                          location=(-0.005, -0.018, 0.045),
                          rotation_euler=(0.3, 0.0, 0.0))

    # === PULMONARY TRUNK (exits anteriorly from right ventricle) ===
    kit.primitive_object(f"{ASSET_ID}-pulmonary-trunk", "cylinder", pulmonary_mat,
                          size=(0.011, 0.011, 0.02),
                          location=(0.008, 0.005, 0.04),
                          rotation_euler=(-0.2, 0.1, 0.0))

    # Left pulmonary artery
    kit.primitive_object(f"{ASSET_ID}-pulmonary-left", "cylinder", pulmonary_mat,
                          size=(0.007, 0.007, 0.015),
                          location=(-0.008, -0.002, 0.052),
                          rotation_euler=(0.0, 0.0, 0.8))

    # Right pulmonary artery
    kit.primitive_object(f"{ASSET_ID}-pulmonary-right", "cylinder", pulmonary_mat,
                          size=(0.007, 0.007, 0.015),
                          location=(0.020, -0.002, 0.052),
                          rotation_euler=(0.0, 0.0, -0.8))

    # === SUPERIOR VENA CAVA (enters right atrium from above) ===
    kit.primitive_object(f"{ASSET_ID}-svc", "cylinder", deoxy_blood,
                          size=(0.009, 0.009, 0.025),
                          location=(0.022, -0.003, 0.042))

    # === INFERIOR VENA CAVA (enters right atrium from below) ===
    kit.primitive_object(f"{ASSET_ID}-ivc", "cylinder", deoxy_blood,
                          size=(0.009, 0.009, 0.02),
                          location=(0.020, -0.008, -0.025))

    # === PULMONARY VEINS (enter left atrium) ===
    kit.primitive_object(f"{ASSET_ID}-pulm-vein-1", "cylinder", oxy_blood,
                          size=(0.006, 0.006, 0.012),
                          location=(-0.022, -0.010, 0.025),
                          rotation_euler=(0.0, 0.0, 0.5))
    kit.primitive_object(f"{ASSET_ID}-pulm-vein-2", "cylinder", oxy_blood,
                          size=(0.006, 0.006, 0.012),
                          location=(-0.022, -0.012, 0.018),
                          rotation_euler=(0.0, 0.0, 0.3))

    # === ATRIOVENTRICULAR VALVES ===
    # Tricuspid valve (right side)
    kit.primitive_object(f"{ASSET_ID}-tricuspid", "cylinder", valve_mat,
                          size=(0.012, 0.012, 0.002),
                          location=(0.012, -0.005, 0.008))

    # Mitral/Bicuspid valve (left side)
    kit.primitive_object(f"{ASSET_ID}-mitral", "cylinder", valve_mat,
                          size=(0.012, 0.012, 0.002),
                          location=(-0.008, -0.007, 0.008))

    # === SEMILUNAR VALVES ===
    # Aortic valve
    kit.primitive_object(f"{ASSET_ID}-aortic-valve", "cylinder", valve_mat,
                          size=(0.008, 0.008, 0.002),
                          location=(-0.005, -0.005, 0.032))

    # Pulmonary valve
    kit.primitive_object(f"{ASSET_ID}-pulmonary-valve", "cylinder", valve_mat,
                          size=(0.008, 0.008, 0.002),
                          location=(0.008, 0.005, 0.032))

    # === EPICARDIAL FAT (yellow deposits on surface) ===
    kit.primitive_object(f"{ASSET_ID}-fat-1", "cylinder", fat_mat,
                          size=(0.008, 0.008, 0.003),
                          location=(0.015, 0.008, 0.01))
    kit.primitive_object(f"{ASSET_ID}-fat-2", "cylinder", fat_mat,
                          size=(0.006, 0.006, 0.003),
                          location=(-0.010, 0.008, -0.02))

    return [heart_body]


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
