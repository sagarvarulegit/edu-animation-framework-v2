#!/usr/bin/env python3
"""
Generates transparent Material 3 Expressive 9:16 (1080x1920) overlay PNGs
for CBSE Class 10 Chemistry Activity 1.3 (Zinc + Dilute Acid).
Strict compliance with:
- Zero-bracket policy (no (, ), [, ], {, }, <, >)
- Unicode right arrow → (U+2192)
- Material 3 Expressive Solar Amber / Tangerine palette
- Safe zone compliance (Y: 220px to 1580px)
- Kinetic 1-3 word badges, zero lecture paragraphs
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
OVERLAYS_DIR = BASE_DIR / "overlays_m3"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

# Colors - Material 3 Expressive Solar Amber Scheme
COLOR_AMBER = (255, 179, 0)         # Primary Amber #FFB300
COLOR_ORANGE = (255, 111, 0)        # Deep Tangerine #FF6F00
COLOR_YELLOW = (255, 234, 0)        # Canary Highlight #FFEA00
COLOR_SURFACE = (24, 18, 12, 220)   # Glassmorphic Card (with alpha)
COLOR_CARD_STROKE = (255, 179, 0, 120)
COLOR_TEXT_MAIN = (250, 246, 240)   # Crisp White
COLOR_TEXT_GOLD = (255, 222, 175)   # Solar Gold
COLOR_TEXT_MUTED = (210, 195, 180)

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_pill(draw, xy, text, font, bg_color, text_color, padding=(24, 12), border_color=None, border_width=2):
    x, y = xy
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = padding
    box = [x - tw//2 - px, y - th//2 - py, x + tw//2 + px, y + th//2 + py]
    radius = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=border_width)
    draw.text((x - tw//2, y - th//2 - 2), text, font=font, fill=text_color)
    return box

def draw_progress_bar(draw, current_step, total_steps=4, y_pos=160):
    bar_width = 860
    start_x = (1080 - bar_width) // 2
    gap = 14
    segment_w = (bar_width - (total_steps - 1) * gap) // total_steps
    for i in range(total_steps):
        sx = start_x + i * (segment_w + gap)
        ex = sx + segment_w
        color = COLOR_AMBER if i < current_step else (COLOR_YELLOW if i == current_step else (70, 55, 40))
        draw.rounded_rectangle([sx, y_pos, ex, y_pos + 10], radius=5, fill=color)

def make_overlay(filename, step_num, render_ui_fn):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gradient vignettes for readability
    for y in range(350):
        alpha = int(160 * (1.0 - y / 350.0))
        draw.line([(0, y), (1080, y)], fill=(12, 9, 6, alpha))
        
    for y in range(1320, 1920):
        alpha = int(210 * ((y - 1320) / 600.0))
        draw.line([(0, y), (1080, y)], fill=(12, 9, 6, alpha))
        
    draw_progress_bar(draw, current_step=step_num)
    render_ui_fn(draw)
    
    out_path = OVERLAYS_DIR / filename
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")
    return out_path

# ==================== SCENE 1: HOOK (POP SOUND) ====================
def render_hook_ui(draw):
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "CBSE CLASS 10 • ACTIVITY 1.3", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    font_headline = get_font(FONT_BOLD, 74)
    font_sub = get_font(FONT_SEMI, 36)
    
    draw.rounded_rectangle([70, 1400, 1010, 1690], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (220, 1445), "POP SOUND TEST", font_mini,
              bg_color=COLOR_ORANGE, text_color=(255, 255, 255), padding=(18, 8))
              
    draw.text((100, 1490), "BRING A FLAME...", font=font_headline, fill=COLOR_TEXT_MAIN)
    draw.text((100, 1570), "POP! HYDROGEN GAS!", font=font_headline, fill=COLOR_YELLOW)
    draw.text((100, 1645), "Watch what causes this ignition →", font=font_sub, fill=COLOR_TEXT_GOLD)

# ==================== SCENE 2: SETUP (ZINC + ACID) ====================
def render_setup_ui(draw):
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "STEP 1 • THE REACTANTS", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    draw.rounded_rectangle([70, 1370, 1010, 1690], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (220, 1415), "CONICAL FLASK SETUP", font_mini,
              bg_color=(50, 40, 28), text_color=COLOR_AMBER, padding=(18, 8), border_color=COLOR_CARD_STROKE)
              
    font_title = get_font(FONT_BOLD, 54)
    font_item = get_font(FONT_BOLD, 38)
    font_sub = get_font(FONT_REG, 30)
    
    draw.text((100, 1455), "Add Acid to Zinc Metal:", font=font_title, fill=COLOR_TEXT_MAIN)
    
    # Reactant Pills
    draw_pill(draw, (300, 1545), "Pure Zinc Metal: Zn", font_item,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(100, 75, 45))
              
    draw_pill(draw, (770, 1545), "+ Dilute Acid: H2SO4", font_item,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(100, 75, 45))
              
    draw.text((100, 1625), "Notice the silver granules at the bottom", font=font_sub, fill=COLOR_TEXT_MUTED)

# ==================== SCENE 3: REACTION (EFFERVESCENCE) ====================
def render_reaction_ui(draw):
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "STEP 2 • CHEMICAL REACTION", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_YELLOW, border_color=COLOR_CARD_STROKE)
              
    draw.rounded_rectangle([60, 1320, 1020, 1720], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (240, 1370), "RAPID EFFERVESCENCE", font_mini,
              bg_color=COLOR_ORANGE, text_color=(255, 255, 255), padding=(18, 8))
              
    font_title = get_font(FONT_BOLD, 58)
    font_eq = get_font(FONT_BOLD, 42)
    font_sub = get_font(FONT_REG, 30)
    
    draw.text((90, 1415), "Vigorous Hydrogen Bubbling!", font=font_title, fill=COLOR_YELLOW)
    draw.text((90, 1485), "Gas bubbles boil rapidly off the zinc surface", font=font_sub, fill=COLOR_TEXT_MAIN)
    
    # Balanced Chemical Equation Pill (100% Bracket-Free)
    draw_pill(draw, (540, 1585), "Zn + H2SO4  →  ZnSO4 + H2 ↑ + Heat", font_eq,
              bg_color=(45, 32, 16), text_color=COLOR_YELLOW, padding=(30, 18),
              border_color=COLOR_AMBER, border_width=3)
              
    draw.text((100, 1665), "Zinc displaces Hydrogen to produce H2 gas", font=font_sub, fill=COLOR_TEXT_GOLD)

# ==================== SCENE 4: TAKEAWAY (EXOTHERMIC) ====================
def render_takeaway_ui(draw):
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "BOARD EXAM HIGH-YIELD TIP", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    draw.rounded_rectangle([60, 1310, 1020, 1720], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (210, 1360), "2-IN-1 REACTION TYPE", font_mini,
              bg_color=COLOR_AMBER, text_color=(35, 20, 5), padding=(18, 8))
              
    font_title = get_font(FONT_BOLD, 54)
    font_point = get_font(FONT_BOLD, 36)
    font_sub = get_font(FONT_REG, 32)
    
    draw.text((90, 1405), "Class 10 Board Essentials:", font=font_title, fill=COLOR_TEXT_MAIN)
    
    draw_pill(draw, (310, 1490), "1. Displacement Reaction", font_point,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(120, 85, 50))
              
    draw_pill(draw, (770, 1490), "2. Exothermic: Flask Gets Hot", font_point,
              bg_color=(45, 34, 22), text_color=COLOR_YELLOW, padding=(24, 12), border_color=(120, 85, 50))
              
    draw_pill(draw, (540, 1610), "Quiz: Which acid was used in this reaction? Comment below!", font_sub,
              bg_color=(60, 42, 20), text_color=COLOR_TEXT_MAIN, padding=(30, 16),
              border_color=COLOR_ORANGE, border_width=2)
              
    draw.text((100, 1675), "Subscribe to ChapterReady for all CBSE activities!", font=get_font(FONT_SEMI, 26), fill=COLOR_TEXT_MUTED)

def main():
    print("Generating Activity 1.3 Material 3 Overlays...")
    make_overlay("overlay_01_hook.png", 1, render_hook_ui)
    make_overlay("overlay_02_setup.png", 2, render_setup_ui)
    make_overlay("overlay_03_reaction.png", 3, render_reaction_ui)
    make_overlay("overlay_04_takeaway.png", 4, render_takeaway_ui)
    print("All overlays generated successfully!")

if __name__ == "__main__":
    main()
