import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "human-heart"


def build_heart():
    """
    Anatomical human heart — anterior view with cross-section.
    
    Technique: Skin modifier + Subdivision Surface for organic shape.
    This is the standard technique for creating organic anatomical models
    in Blender — create a skeleton of connected vertices, apply Skin modifier
    to generate mesh, then Subdivision Surface to smooth.
    
    Based on real anatomical proportions:
    - Heart is roughly conical, 12cm tall, 8cm wide
    - Apex points down and to the left
    - Right side is more anterior
    - Left ventricle wall is 3x thicker than right
    """

    # === MATERIALS ===
    muscle = kit.add_material("heart-myocardium", (0.65, 0.16, 0.12), metallic=0.0, roughness=0.7)
    inner = kit.add_material("heart-endocardium", (0.80, 0.50, 0.45), metallic=0.0, roughness=0.5)
    oxy = kit.add_material("heart-oxy", (0.82, 0.15, 0.12), metallic=0.0, roughness=0.5)
    deoxy = kit.add_material("heart-deoxy", (0.22, 0.30, 0.70), metallic=0.0, roughness=0.5)
    valve = kit.add_material("heart-valve", (0.88, 0.78, 0.68), metallic=0.0, roughness=0.35)
    aorta = kit.add_material("heart-aorta", (0.72, 0.18, 0.14), metallic=0.0, roughness=0.55)
    pulmonary = kit.add_material("heart-pulmonary", (0.32, 0.38, 0.72), metallic=0.0, roughness=0.50)
    fat = kit.add_material("heart-fat", (0.85, 0.75, 0.42), metallic=0.0, roughness=0.6)
    coronary = kit.add_material("heart-coronary", (0.90, 0.30, 0.25), metallic=0.0, roughness=0.5)

    # === HEART BODY using Skin Modifier technique ===
    # Create a skeleton of vertices that defines the heart's organic shape
    # The Skin modifier will generate mesh around these vertices
    # Subdivision Surface will smooth it into organic form
    
    bm = bmesh.new()
    
    # Heart outline skeleton — anterior view
    # Top (base) → Bottom (apex), Right → Left
    # Key anatomical landmarks as vertex positions
    
    # Main body spine (vertical center line)
    v_top = bm.verts.new((0.0, 0.0, 0.04))      # Top of heart (base)
    v_upper_mid = bm.verts.new((0.0, 0.0, 0.02))  # Upper middle
    v_mid = bm.verts.new((0.0, 0.0, 0.0))          # Center
    v_lower_mid = bm.verts.new((-0.005, 0.0, -0.015))  # Lower middle (tilting left)
    v_apex = bm.verts.new((-0.012, 0.0, -0.03))    # Apex (points down-left)
    
    # Right border (right ventricle/atrium)
    v_right_upper = bm.verts.new((0.025, 0.0, 0.015))   # Right atrium
    v_right_mid = bm.verts.new((0.028, 0.0, 0.0))        # Right ventricle (bulge)
    v_right_lower = bm.verts.new((0.018, 0.0, -0.015))   # Lower right
    
    # Left border (left ventricle)
    v_left_upper = bm.verts.new((-0.018, 0.0, 0.012))    # Left atrium
    v_left_mid = bm.verts.new((-0.022, 0.0, -0.005))     # Left ventricle
    v_left_lower = bm.verts.new((-0.015, 0.0, -0.022))   # Lower left
    
    # Connect skeleton edges
    # Vertical spine
    bm.edges.new([v_top, v_upper_mid])
    bm.edges.new([v_upper_mid, v_mid])
    bm.edges.new([v_mid, v_lower_mid])
    bm.edges.new([v_lower_mid, v_apex])
    
    # Right side connections
    bm.edges.new([v_top, v_right_upper])
    bm.edges.new([v_right_upper, v_right_mid])
    bm.edges.new([v_right_mid, v_right_lower])
    bm.edges.new([v_right_lower, v_apex])
    
    # Left side connections
    bm.edges.new([v_top, v_left_upper])
    bm.edges.new([v_left_upper, v_left_mid])
    bm.edges.new([v_left_mid, v_left_lower])
    bm.edges.new([v_left_lower, v_apex])
    
    # Cross connections for volume
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
    
    # Apply Skin modifier — generates organic mesh around skeleton
    skin = skeleton.modifiers.new(name="Skin", type='SKIN')
    
    # Set skin radius for each vertex (controls thickness)
    sv = skeleton.data.skin_vertices[0].data
    sv[0].radius = (0.020, 0.020)    # Top (base) — wide
    sv[1].radius = (0.022, 0.022)    # Upper mid
    sv[2].radius = (0.025, 0.025)    # Center — widest
    sv[3].radius = (0.018, 0.018)    # Lower mid
    sv[4].radius = (0.008, 0.008)    # Apex — narrow point
    sv[5].radius = (0.018, 0.018)    # Right upper
    sv[6].radius = (0.022, 0.022)    # Right mid — bulge
    sv[7].radius = (0.012, 0.012)    # Right lower
    sv[8].radius = (0.015, 0.015)    # Left upper
    sv[9].radius = (0.020, 0.020)    # Left mid
    sv[10].radius = (0.010, 0.010)   # Left lower
    
    # Apply Subdivision Surface for smooth organic surface
    subdiv = skeleton.modifiers.new(name="Subsurf", type='SUBSURF')
    subdiv.levels = 3
    subdiv.render_levels = 3
    
    # Apply modifiers to get final mesh
    bpy.context.view_layer.objects.active = skeleton
    bpy.ops.object.modifier_apply(modifier="Skin")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    
    # === AORTA (large vessel arching upward) ===
    # Ascending aorta
    kit.primitive_object(f"{ASSET_ID}-aorta-asc", "cylinder", aorta,
                          size=(0.010, 0.010, 0.020),
                          location=(0.005, -0.003, 0.045),
                          rotation_euler=(0.1, 0.0, 0.0))
    
    # Aortic arch (curves posteriorly and to the left)
    kit.primitive_object(f"{ASSET_ID}-aorta-arch", "cylinder", aorta,
                          size=(0.010, 0.010, 0.012),
                          location=(0.002, -0.010, 0.055),
                          rotation_euler=(1.3, 0.0, 0.2))
    
    # Descending aorta
    kit.primitive_object(f"{ASSET_ID}-aorta-desc", "cylinder", aorta,
                          size=(0.009, 0.009, 0.018),
                          location=(-0.002, -0.015, 0.042),
                          rotation_euler=(0.2, 0.0, 0.0))
    
    # Three branches from aortic arch
    kit.primitive_object(f"{ASSET_ID}-brachiocephalic", "cylinder", aorta,
                          size=(0.005, 0.005, 0.010),
                          location=(0.010, -0.005, 0.060))
    kit.primitive_object(f"{ASSET_ID}-left-carotid", "cylinder", aorta,
                          size=(0.004, 0.004, 0.010),
                          location=(0.003, -0.005, 0.062))
    kit.primitive_object(f"{ASSET_ID}-left-subclavian", "cylinder", aorta,
                          size=(0.004, 0.004, 0.008),
                          location=(-0.005, -0.005, 0.060))
    
    # === PULMONARY TRUNK (exits anteriorly from right ventricle) ===
    kit.primitive_object(f"{ASSET_ID}-pulmonary-trunk", "cylinder", pulmonary,
                          size=(0.009, 0.009, 0.018),
                          location=(0.010, 0.005, 0.042),
                          rotation_euler=(-0.15, 0.1, 0.0))
    
    # Left pulmonary artery
    kit.primitive_object(f"{ASSET_ID}-pulmonary-left", "cylinder", pulmonary,
                          size=(0.006, 0.006, 0.012),
                          location=(-0.008, -0.002, 0.055),
                          rotation_euler=(0.0, 0.0, 0.8))
    
    # Right pulmonary artery
    kit.primitive_object(f"{ASSET_ID}-pulmonary-right", "cylinder", pulmonary,
                          size=(0.006, 0.006, 0.012),
                          location=(0.020, -0.002, 0.055),
                          rotation_euler=(0.0, 0.0, -0.8))
    
    # === SUPERIOR VENA CAVA ===
    kit.primitive_object(f"{ASSET_ID}-svc", "cylinder", deoxy,
                          size=(0.008, 0.008, 0.022),
                          location=(0.022, -0.002, 0.040))
    
    # === INFERIOR VENA CAVA ===
    kit.primitive_object(f"{ASSET_ID}-ivc", "cylinder", deoxy,
                          size=(0.008, 0.008, 0.018),
                          location=(0.020, -0.006, -0.025))
    
    # === PULMONARY VEINS (enter left atrium) ===
    kit.primitive_object(f"{ASSET_ID}-pulm-vein-1", "cylinder", oxy,
                          size=(0.005, 0.005, 0.010),
                          location=(-0.020, -0.008, 0.022),
                          rotation_euler=(0.0, 0.0, 0.5))
    kit.primitive_object(f"{ASSET_ID}-pulm-vein-2", "cylinder", oxy,
                          size=(0.005, 0.005, 0.010),
                          location=(-0.020, -0.010, 0.015),
                          rotation_euler=(0.0, 0.0, 0.3))
    
    # === CORONARY ARTERIES (on surface of heart) ===
    # Left anterior descending
    kit.primitive_object(f"{ASSET_ID}-lad", "cylinder", coronary,
                          size=(0.002, 0.002, 0.025),
                          location=(0.005, 0.008, -0.005),
                          rotation_euler=(0.3, 0.0, 0.1))
    
    # Right coronary artery
    kit.primitive_object(f"{ASSET_ID}-rca", "cylinder", coronary,
                          size=(0.002, 0.002, 0.020),
                          location=(0.020, 0.008, 0.01),
                          rotation_euler=(0.0, 0.0, -0.3))
    
    # === ATRIOVENTRICULAR GROOVE (sulcus) ===
    kit.primitive_object(f"{ASSET_ID}-av-groove", "cube", fat,
                          size=(0.040, 0.003, 0.003),
                          location=(0.0, 0.008, 0.008))
    
    # === EPICARDIAL FAT ===
    kit.primitive_object(f"{ASSET_ID}-fat-1", "cylinder", fat,
                          size=(0.008, 0.008, 0.002),
                          location=(0.015, 0.008, 0.015))
    kit.primitive_object(f"{ASSET_ID}-fat-2", "cylinder", fat,
                          size=(0.006, 0.006, 0.002),
                          location=(-0.010, 0.008, -0.018))
    
    return [skeleton]


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
