import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "full-circuit"


def build_circuit():
    # Breadboard/base
    board = kit.add_material("circuit-board", (0.90, 0.88, 0.82), metallic=0.0, roughness=0.6)
    # Wire: red
    wire = kit.add_material("circuit-wire", (0.85, 0.15, 0.12), metallic=0.0, roughness=0.65)
    # Battery: copper top
    batt_copper = kit.add_material("circuit-batt-copper", (0.72, 0.45, 0.18), metallic=0.9, roughness=0.25)
    batt_body = kit.add_material("circuit-batt-body", (0.08, 0.08, 0.08), metallic=0.3, roughness=0.5)
    # Bulb: glass
    glass = kit.add_material("circuit-bulb-glass", (0.92, 0.93, 0.88), metallic=0.0, roughness=0.05)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    # Switch: brass
    switch_mat = kit.add_material("circuit-switch", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)
    # Ammeter face
    ammeter_face = kit.add_material("circuit-ammeter", (0.12, 0.12, 0.12), metallic=0.3, roughness=0.6)

    # Base board
    kit.primitive_object(f"{ASSET_ID}-board", "cube", board,
                          size=(0.15, 0.005, 0.10),
                          location=(0.0, 0.0, 0.0))

    # Battery (left side)
    kit.primitive_object(f"{ASSET_ID}-battery-body", "cylinder", batt_body,
                          size=(0.014, 0.014, 0.04),
                          location=(-0.05, 0.01, 0.0))
    kit.primitive_object(f"{ASSET_ID}-battery-top", "cylinder", batt_copper,
                          size=(0.014, 0.014, 0.005),
                          location=(-0.05, 0.01, 0.022))

    # Bulb (right side)
    kit.primitive_object(f"{ASSET_ID}-bulb-globe", "cylinder", glass,
                          size=(0.02, 0.02, 0.02),
                          location=(0.05, 0.01, 0.015))

    # Switch (bottom center)
    kit.primitive_object(f"{ASSET_ID}-switch-base", "cube", switch_mat,
                          size=(0.025, 0.004, 0.015),
                          location=(0.0, 0.008, -0.03))

    # Wires connecting components (4 segments forming rectangle)
    # Top wire: battery to bulb
    kit.primitive_object(f"{ASSET_ID}-wire-top", "cylinder", wire,
                          size=(0.002, 0.002, 0.10),
                          location=(0.0, 0.01, 0.0),
                          rotation_euler=(0.0, 1.57, 0.0))
    # Right wire: bulb down to switch
    kit.primitive_object(f"{ASSET_ID}-wire-right", "cylinder", wire,
                          size=(0.002, 0.002, 0.06),
                          location=(0.05, 0.01, -0.015),
                          rotation_euler=(1.57, 0.0, 0.0))
    # Bottom wire: switch to battery
    kit.primitive_object(f"{ASSET_ID}-wire-bottom", "cylinder", wire,
                          size=(0.002, 0.002, 0.10),
                          location=(0.0, 0.008, -0.03),
                          rotation_euler=(0.0, 1.57, 0.0))
    # Left wire: battery down
    kit.primitive_object(f"{ASSET_ID}-wire-left", "cylinder", wire,
                          size=(0.002, 0.002, 0.06),
                          location=(-0.05, 0.01, -0.015),
                          rotation_euler=(1.57, 0.0, 0.0))

    import bpy
    objects = [o for o in bpy.context.collection.objects if o.name.startswith(ASSET_ID)]
    return objects if objects else []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_circuit()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
