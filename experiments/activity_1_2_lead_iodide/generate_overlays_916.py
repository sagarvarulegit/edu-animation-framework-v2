#!/usr/bin/env python3
"""
Generates Material 3 Expressive 9:16 (1080x1920) full-frame composite frames
for CBSE Class 10 Chemistry Activity 1.2 (Precipitation of Lead Iodide).
Strict compliance with:
- .agents/rules/youtube_shorts_retention.md
- Climax Inversion (Instant visual shock in Frame 0)
- Material 3 Expressive Amber-Orange color palette
- Safe zone compliance (Y: 220px to 1580px)
- Kinetic 1-3 word badges, zero lecture paragraphs
- YouTube-safe formulas (->, no angle brackets)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OVERLAYS_DIR = BASE_DIR / "overlays_m3"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

# Colors - Material 3 Expressive Solar Amber Scheme
COLOR_BG_DARK = (18, 14, 10)
COLOR_AMBER = (255, 179, 0)         # Primary Amber #FFB300
COLOR_ORANGE = (255, 111, 0)        # Deep Tangerine #FF6F00
COLOR_YELLOW = (255, 234, 0)        # Canary Highlight #FFEA00
COLOR_SURFACE = (28, 22, 16, 215)   # Glassmorphic Card (with alpha)
COLOR_CARD_STROKE = (255, 179, 0, 110)
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
    """Draws an M3 pill/chip badge centered at given (x, y)."""
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
    """Draws an M3 segmented linear progress indicator."""
    bar_width = 860
    start_x = (1080 - bar_width) // 2
    gap = 14
    segment_w = (bar_width - (total_steps - 1) * gap) // total_steps
    
    for i in range(total_steps):
        sx = start_x + i * (segment_w + gap)
        ex = sx + segment_w
        if i < current_step:
            color = COLOR_AMBER
        elif i == current_step:
            color = COLOR_YELLOW
        else:
            color = (70, 55, 40)
        draw.rounded_rectangle([sx, y_pos, ex, y_pos + 10], radius=5, fill=color)

def compose_scene(image_name, overlay_generator_fn, out_name):
    """Loads a 9:16 background image and composites the M3 glass overlay onto it."""
    bg_path = IMG_DIR / image_name
    bg = Image.open(bg_path).convert("RGBA")
    if bg.size != (1080, 1920):
        bg = bg.resize((1080, 1920), Image.Resampling.LANCZOS)
        
    # Top & bottom subtle gradient vignette for text legibility
    vignette = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    
    # Top dark gradient (0 to 450px)
    for y in range(450):
        alpha = int(180 * (1.0 - y / 450.0))
        v_draw.line([(0, y), (1080, y)], fill=(12, 9, 6, alpha))
        
    # Bottom dark gradient (1300 to 1920px)
    for y in range(1300, 1920):
        alpha = int(220 * ((y - 1300) / 620.0))
        v_draw.line([(0, y), (1080, y)], fill=(12, 9, 6, alpha))
        
    base = Image.alpha_composite(bg, vignette)
    
    # Render overlay UI
    ui_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_layer)
    overlay_generator_fn(draw)
    
    final_frame = Image.alpha_composite(base, ui_layer).convert("RGB")
    final_path = OVERLAYS_DIR / out_name
    final_frame.save(final_path, quality=95)
    print(f"Saved overlay: {final_path.name}")
    return final_path

# ==================== SCENE 1: HOOK (CLIMAX INVERSION) ====================
def render_hook_ui(draw):
    draw_progress_bar(draw, current_step=1)
    
    # Top Tag
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "CBSE CLASS 10 • ACTIVITY 1.2", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    # Big Shock Hook Headline
    font_headline = get_font(FONT_BOLD, 74)
    font_sub = get_font(FONT_SEMI, 36)
    
    # Glass card container
    draw.rounded_rectangle([70, 1380, 1010, 1680], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    # Accent mini-badge inside card
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (240, 1430), "INSTANT REACTION", font_mini,
              bg_color=COLOR_ORANGE, text_color=(255, 255, 255), padding=(18, 8))
              
    # Punchy lines
    draw.text((100, 1475), "TWO CLEAR LIQUIDS...", font=font_headline, fill=COLOR_TEXT_MAIN)
    draw.text((100, 1555), "BOOM! YELLOW CLOUD?!", font=font_headline, fill=COLOR_YELLOW)
    draw.text((100, 1635), "Watch what happens when they touch ->", font=font_sub, fill=COLOR_TEXT_GOLD)

# ==================== SCENE 2: SETUP (TWO CLEAR LIQUIDS) ====================
def render_setup_ui(draw):
    draw_progress_bar(draw, current_step=2)
    
    # Top Tag
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "STEP 1 • THE REACTANTS", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    # Glass card container
    draw.rounded_rectangle([70, 1360, 1010, 1690], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (210, 1410), "COLORLESS SOLUTIONS", font_mini,
              bg_color=(50, 40, 28), text_color=COLOR_AMBER, padding=(18, 8), border_color=COLOR_CARD_STROKE)
              
    font_title = get_font(FONT_BOLD, 54)
    font_item = get_font(FONT_BOLD, 38)
    font_sub = get_font(FONT_REG, 30)
    
    draw.text((100, 1450), "Mix Two Clear Solutions:", font=font_title, fill=COLOR_TEXT_MAIN)
    
    # Reactant 1 Pill
    draw_pill(draw, (320, 1545), "Lead Nitrate: Pb(NO3)2", font_item,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(100, 75, 45))
              
    # Reactant 2 Pill
    draw_pill(draw, (770, 1545), "+ Potassium Iodide: KI", font_item,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(100, 75, 45))
              
    draw.text((100, 1625), "Both look exactly like pure water!", font=font_sub, fill=COLOR_TEXT_MUTED)

# ==================== SCENE 3: REACTION & SCIENCE ====================
def render_reaction_ui(draw):
    draw_progress_bar(draw, current_step=3)
    
    # Top Tag
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "STEP 2 • CHEMICAL PRECIPITATION", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_YELLOW, border_color=COLOR_CARD_STROKE)
              
    # Glass card container
    draw.rounded_rectangle([60, 1320, 1020, 1720], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (230, 1370), "PRECIPITATION REACTION", font_mini,
              bg_color=COLOR_ORANGE, text_color=(255, 255, 255), padding=(18, 8))
              
    font_title = get_font(FONT_BOLD, 60)
    font_eq = get_font(FONT_BOLD, 42)
    font_sub = get_font(FONT_REG, 30)
    
    draw.text((90, 1415), "Bright Yellow Solid Forms!", font=font_title, fill=COLOR_YELLOW)
    draw.text((90, 1485), "Lead Iodide (PbI2) is completely insoluble.", font=font_sub, fill=COLOR_TEXT_MAIN)
    
    # Balanced Chemical Equation Pill (High contrast)
    draw_pill(draw, (540, 1585), "Pb(NO3)2 + 2KI  ->  PbI2 (v) + 2KNO3", font_eq,
              bg_color=(45, 32, 16), text_color=COLOR_YELLOW, padding=(30, 18),
              border_color=COLOR_AMBER, border_width=3)
              
    draw.text((100, 1665), "Yellow precipitate: PbI2  |  Colorless solution: KNO3", font=font_sub, fill=COLOR_TEXT_GOLD)

# ==================== SCENE 4: EXAM TAKEAWAY & LOOP ====================
def render_takeaway_ui(draw):
    draw_progress_bar(draw, current_step=4)
    
    # Top Tag
    font_tag = get_font(FONT_BOLD, 28)
    draw_pill(draw, (540, 230), "BOARD EXAM HIGH-YIELD TIP", font_tag,
              bg_color=(38, 28, 18, 230), text_color=COLOR_AMBER, border_color=COLOR_CARD_STROKE)
              
    # Glass card container
    draw.rounded_rectangle([60, 1310, 1020, 1720], radius=32, fill=COLOR_SURFACE, outline=COLOR_CARD_STROKE, width=3)
    
    font_mini = get_font(FONT_BOLD, 26)
    draw_pill(draw, (210, 1360), "2-IN-1 REACTION TYPE", font_mini,
              bg_color=COLOR_AMBER, text_color=(35, 20, 5), padding=(18, 8))
              
    font_title = get_font(FONT_BOLD, 54)
    font_point = get_font(FONT_BOLD, 36)
    font_sub = get_font(FONT_REG, 32)
    
    draw.text((90, 1405), "Class 10 Board Essentials:", font=font_title, fill=COLOR_TEXT_MAIN)
    
    # Two takeaways
    draw_pill(draw, (320, 1490), "1. Double Displacement", font_point,
              bg_color=(45, 34, 22), text_color=COLOR_TEXT_GOLD, padding=(24, 12), border_color=(120, 85, 50))
              
    draw_pill(draw, (760, 1490), "2. Precipitation Reaction", font_point,
              bg_color=(45, 34, 22), text_color=COLOR_YELLOW, padding=(24, 12), border_color=(120, 85, 50))
              
    # Question pill for comments loop
    draw_pill(draw, (540, 1610), "Quiz: What happened to Potassium (K)? Tell us below!", font_sub,
              bg_color=(60, 42, 20), text_color=COLOR_TEXT_MAIN, padding=(30, 16),
              border_color=COLOR_ORANGE, border_width=2)
              
    draw.text((100, 1675), "Subscribe to ChapterReady for all CBSE activities!", font=get_font(FONT_SEMI, 26), fill=COLOR_TEXT_MUTED)

def main():
    print("Generating 4 Material 3 Expressive 9:16 Composite Frames...")
    compose_scene("01_hook_bloom.jpg", render_hook_ui, "frame_01_hook.jpg")
    compose_scene("02_setup_clear.jpg", render_setup_ui, "frame_02_setup.jpg")
    compose_scene("03_reaction_swirl.jpg", render_reaction_ui, "frame_03_reaction.jpg")
    compose_scene("04_result_settled.jpg", render_takeaway_ui, "frame_04_takeaway.jpg")
    print("All 4 composite frames generated successfully!")

if __name__ == "__main__":
    main()
