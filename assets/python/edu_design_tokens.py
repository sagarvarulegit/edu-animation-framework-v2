"""
Educational Animation Framework — Design Tokens Python Adapter for Blender.
Provides deterministic color conversions (sRGB hex -> Linear sRGB float tuples)
and standardized material/lighting/camera parameters loaded from visual/design-tokens.json.
"""

import json
from pathlib import Path
from typing import Any, Dict, Tuple


def _find_tokens_file() -> Path:
    # Look in ../../visual/design-tokens.json relative to this file
    current = Path(__file__).resolve().parent
    candidates = [
        current.parent.parent / "visual" / "design-tokens.json",
        current.parent / "visual" / "design-tokens.json",
        Path.cwd() / "visual" / "design-tokens.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Could not find visual/design-tokens.json in candidate locations.")


def _load_tokens() -> Dict[str, Any]:
    tokens_path = _find_tokens_file()
    with open(tokens_path, "r", encoding="utf-8") as f:
        return json.load(f)


TOKENS = _load_tokens()


def srgb_to_linear(c: float) -> float:
    """Converts an sRGB color component [0.0, 1.0] to Linear sRGB for Blender rendering."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def hex_to_srgb(hex_str: str) -> Tuple[float, float, float, float]:
    """Converts #RRGGBB to sRGB float tuple (r, g, b, 1.0) in [0.0, 1.0]."""
    clean = hex_str.lstrip("#")
    r = int(clean[0:2], 16) / 255.0
    g = int(clean[2:4], 16) / 255.0
    b = int(clean[4:6], 16) / 255.0
    return (r, g, b, 1.0)


def hex_to_linear(hex_str: str) -> Tuple[float, float, float, float]:
    """Converts #RRGGBB to linear sRGB float tuple (r, g, b, 1.0) for Blender shaders."""
    sr, sg, sb, a = hex_to_srgb(hex_str)
    return (srgb_to_linear(sr), srgb_to_linear(sg), srgb_to_linear(sb), a)


def color_linear(token_path: str) -> Tuple[float, float, float, float]:
    """
    Looks up a color by dot-path (e.g. 'reagents.magnesiumRibbon', 'ui.background')
    and returns a Linear sRGB tuple (r, g, b, 1.0).
    """
    parts = token_path.split(".")
    curr = TOKENS["colors"]
    for p in parts:
        curr = curr[p]
    return hex_to_linear(curr)


def color_srgb(token_path: str) -> Tuple[float, float, float, float]:
    """Looks up a color by dot-path and returns an sRGB tuple (r, g, b, 1.0)."""
    parts = token_path.split(".")
    curr = TOKENS["colors"]
    for p in parts:
        curr = curr[p]
    return hex_to_srgb(curr)


def get_material_config(mat_name: str) -> Dict[str, Any]:
    """
    Returns material configuration from tokens with baseColor converted to linear tuple.
    """
    raw = TOKENS["materials"].get(mat_name)
    if not raw:
        raise KeyError(f"Material '{mat_name}' not defined in design-tokens.json")
    
    cfg = {
        "base_color": hex_to_linear(raw["baseColor"]),
        "metallic": raw.get("metallic", 0.0),
        "roughness": raw.get("roughness", 0.5),
        "transmission": raw.get("transmission", 0.0),
        "ior": raw.get("ior", 1.45),
    }
    if "emissionColor" in raw:
        cfg["emission_color"] = hex_to_linear(raw["emissionColor"])
        cfg["emission_strength"] = raw.get("emissionStrength", 1.0)
    return cfg


COLORS = TOKENS["colors"]
MATERIALS = TOKENS["materials"]
CAMERA = TOKENS["camera"]
LIGHTING = TOKENS["lighting"]
LABELS = TOKENS["labels"]
ARROWS = TOKENS["arrows"]
EQUATIONS = TOKENS["equations"]
PARTICLES = TOKENS["particles"]
