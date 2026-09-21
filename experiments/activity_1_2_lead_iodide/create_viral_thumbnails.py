#!/usr/bin/env python3
"""
Creates viral, high-CTR thumbnails (both 9:16 and 16:9) for
CBSE Class 10 Science Activity 1.2 (Precipitation of Lead Iodide).
Uses Google Material 3 Expressive palette, high-contrast typography,
and the dramatic canary-yellow precipitation cloud.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_BOLD, size)
    except Exception:
        return ImageFont.load_default()

def draw_pill(draw, xy, text, font, bg_color, text_color, padding=(28, 14), border_color=None, border_width=3):
    x, y = xy
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = padding
    box = [x - tw//2 - px, y - th//2 - py, x + tw//2 + px, y + th//2 + py]
    radius = (box[3] - box[1]) // 2
    draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=border_width)
    draw.text((x - tw//2, y - th//2 - 2), text, font=font, fill=text_color)
    return box

def create_thumbnail_916():
    hook_img_path = IMG_DIR / "01_hook_bloom.jpg"
    im = Image.open(hook_img_path).convert("RGBA")
    if im.size != (1080, 1920):
        im = im.resize((1080, 1920), Image.Resampling.LANCZOS)
        
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Dark gradients at top and bottom
    for y in range(400):
        alpha = int(190 * (1.0 - y / 400.0))
        draw.line([(0, y), (1080, y)], fill=(15, 10, 5, alpha))
        
    for y in range(1250, 1920):
        alpha = int(230 * ((y - 1250) / 670.0))
        draw.line([(0, y), (1080, y)], fill=(12, 8, 4, alpha))
        
    # Top Tag
    draw_pill(draw, (540, 220), "CBSE CLASS 10 • ACTIVITY 1.2", get_font(34),
              bg_color=(35, 25, 15, 240), text_color=(255, 179, 0),
              border_color=(255, 179, 0, 180), border_width=3)
              
    # Bottom Card
    draw.rounded_rectangle([60, 1340, 1020, 1720], radius=36,
                           fill=(22, 16, 10, 230), outline=(255, 179, 0, 180), width=4)
                           
    draw_pill(draw, (230, 1400), "SHOCK REACTION", get_font(28),
              bg_color=(255, 111, 0), text_color=(255, 255, 255), padding=(22, 10))
              
    draw.text((90, 1450), "CLEAR LIQUIDS...", font=get_font(76), fill=(255, 255, 255))
    draw.text((90, 1540), "YELLOW EXPLOSION?!", font=get_font(74), fill=(255, 234, 0))
    draw.text((95, 1640), "Lead Iodide Precipitation Explained", font=get_font(36), fill=(255, 222, 175))
    
    final_im = Image.alpha_composite(im, overlay).convert("RGB")
    out_path = OUT_DIR / "thumbnail_shorts_916.jpg"
    final_im.save(out_path, quality=95)
    print(f"Saved 9:16 thumbnail: {out_path.name}")
    return out_path

def create_thumbnail_169():
    hook_img_path = IMG_DIR / "01_hook_bloom.jpg"
    im_vert = Image.open(hook_img_path).convert("RGBA")
    
    # Create 1920x1080 horizontal canvas
    canvas = Image.new("RGBA", (1920, 1080), (16, 12, 8, 255))
    
    # Crop / position the test tube reaction on the right half
    target_w = 820
    crop_vert = im_vert.resize((target_w, int(target_w * 1920 / 1080)), Image.Resampling.LANCZOS)
    canvas.paste(crop_vert, (1920 - target_w, -180))
    
    # Left side dark gradient
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for x in range(1920):
        if x < 1000:
            alpha = 250
        elif x < 1400:
            alpha = int(250 * (1.0 - (x - 1000) / 400.0))
        else:
            alpha = 0
        draw.line([(x, 0), (x, 1080)], fill=(16, 12, 8, alpha))
        
    # Text and badges on the left half
    draw_pill(draw, (380, 160), "CBSE CLASS 10 • ACTIVITY 1.2", get_font(36),
              bg_color=(35, 25, 15, 240), text_color=(255, 179, 0),
              border_color=(255, 179, 0, 180), border_width=3)
              
    draw_pill(draw, (230, 260), "CHEMISTRY SHOCK", get_font(28),
              bg_color=(255, 111, 0), text_color=(255, 255, 255), padding=(24, 10))
              
    draw.text((100, 330), "CLEAR LIQUIDS...", font=get_font(84), fill=(255, 255, 255))
    draw.text((100, 435), "YELLOW EXPLOSION?!", font=get_font(82), fill=(255, 234, 0))
    
    # Equation Pill
    draw_pill(draw, (470, 580), "Pb(NO3)2 + 2KI  ->  PbI2 (v) + 2KNO3", get_font(42),
              bg_color=(38, 28, 16), text_color=(255, 234, 0), padding=(32, 18),
              border_color=(255, 179, 0), border_width=3)
              
    draw.text((100, 680), "Precipitation & Double Displacement Reaction", font=get_font(38), fill=(255, 222, 175))
    draw.text((100, 750), "Real Lab Apparatus • 100% NCERT Verified", font=get_font(32), fill=(200, 185, 170))
    
    # High-yield exam badge
    draw_pill(draw, (260, 860), "BOARD EXAM FAVORITE", get_font(30),
              bg_color=(255, 179, 0), text_color=(30, 18, 5), padding=(26, 12))
              
    final_im = Image.alpha_composite(canvas, overlay).convert("RGB")
    out_path = OUT_DIR / "thumbnail_landscape_169.jpg"
    final_im.save(out_path, quality=95)
    print(f"Saved 16:9 thumbnail: {out_path.name}")
    return out_path

def main():
    print("Generating High-CTR Thumbnails for Activity 1.2...")
    create_thumbnail_916()
    create_thumbnail_169()
    print("Thumbnails generated successfully!")

if __name__ == "__main__":
    main()
