import json

with open("/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/geometry_audit.json") as f:
    data = json.load(f)

print("| Asset ID | Objects | Vertices | Faces | Non-Manifold | GLB Size | Materials Count |")
print("|---|---|---|---|---|---|---|")
for k, v in sorted(data.items()):
    nobjs = v["total_objects"]
    nverts = v["total_verts"]
    nfaces = v["total_faces"]
    nm = v["total_non_manifold"]
    size_kb = round(v["glb_size_bytes"] / 1024, 1)
    nmats = len(v["materials"])
    print(f"| {k} | {nobjs} | {nverts} | {nfaces} | {nm} | {size_kb} KB | {nmats} |")

print("\nDetailed Material Analysis & Anomalies:")
for k, v in sorted(data.items()):
    print(f"\n### {k}")
    print(f"Materials ({len(v['materials'])}): {', '.join(v['materials'])}")
    anomalies = []
    for obj in v["objects"]:
        if obj["non_manifold_edges"] > 0 or obj["non_manifold_verts"] > 0:
            anomalies.append(f"Object {obj['name']}: {obj['non_manifold_edges']} non-manifold edges, {obj['non_manifold_verts']} non-manifold verts")
        if any(d == 0 for d in obj["dimensions"]):
            anomalies.append(f"Object {obj['name']}: zero thickness dimension {obj['dimensions']}")
    if anomalies:
        for a in anomalies:
            print(f"  - WARNING: {a}")
    else:
        print("  - Topology: 0 non-manifold edges/vertices detected at top level mesh data")
