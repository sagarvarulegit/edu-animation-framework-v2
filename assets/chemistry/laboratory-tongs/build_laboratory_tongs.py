"""Build a reusable, animation-ready pair of laboratory crucible tongs."""
import sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "laboratory-tongs"


def rounded_bar(name, material, points, bevel, objects):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions, curve.resolution_u = "3D", 16
    curve.bevel_depth, curve.bevel_resolution = bevel, 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    objects.append(obj)


def build_tongs():
    steel = kit.add_machined_metal_material("tongs-stainless-steel", (0.42, 0.45, 0.49), 0.92, 0.23)
    rubber = kit.add_material("tongs-heat-grip", (0.035, 0.045, 0.055), 0.0, 0.42)
    dark_steel = kit.add_machined_metal_material("tongs-hinge-steel", (0.16, 0.18, 0.20), 0.88, 0.30)
    objects = []
    for side, label in ((-1, "left"), (1, "right")):
        y = side * 0.008
        rounded_bar(f"{ASSET_ID}-{label}-arm", steel,
                    [(0.075, y, 0.006), (0.025, y * 0.55, 0.001), (-0.050, y, 0.004), (-0.100, side * 0.022, 0.018)],
                    0.0032, objects)
        sleeve = kit.primitive_object(f"{ASSET_ID}-{label}-grip", "cylinder", rubber,
                                      size=(0.010, 0.010, 0.058), location=(0.050, y, 0.004), rotation_euler=(0.0, 1.5708, 0.0))
        objects.append(sleeve)
        jaw = kit.primitive_object(f"{ASSET_ID}-{label}-jaw", "cube", steel,
                                   size=(0.026, 0.009, 0.007), location=(-0.104, side * 0.024, 0.018), rotation_euler=(0.0, 0.16 * side, 0.0))
        edge = jaw.modifiers.new("softened forged edge", "BEVEL")
        edge.width, edge.segments = 0.0015, 3
        objects.append(jaw)
    pivot = kit.primitive_object(f"{ASSET_ID}-pivot", "cylinder", dark_steel,
                                 size=(0.014, 0.014, 0.012), location=(0.025, 0.0, 0.002), rotation_euler=(1.5708, 0.0, 0.0))
    washer = kit.primitive_object(f"{ASSET_ID}-pivot-washer", "cylinder", steel,
                                  size=(0.018, 0.018, 0.002), location=(0.025, -0.007, 0.002), rotation_euler=(1.5708, 0.0, 0.0))
    return objects + [pivot, washer]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_tongs()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=58.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
