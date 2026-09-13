"""
src/visualizer/thumbnail.py - High-CTR Automated YouTube Thumbnail Generator
1280x720 standard with neon bloom, HUD tags, and safe-zone compliance.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1280, 720

CYBERPUNK = {
    "bg_dark": (11, 7, 24),
    "neon_cyan": (0, 240, 255),
    "neon_magenta": (255, 0, 128),
    "neon_amber": (255, 184, 0),
    "white": (255, 255, 255),
}

def draw_neon_text(draw, base_img, pos, text, font, core_color, glow_color, glow_radius=15):
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text(pos, text, font=font, fill=glow_color + (255,))

    blur_large = glow_layer.filter(ImageFilter.GaussianBlur(glow_radius))
    blur_small = glow_layer.filter(ImageFilter.GaussianBlur(glow_radius // 3))

    base_img.alpha_composite(blur_large)
    base_img.alpha_composite(blur_small)
    draw.text(pos, text, font=font, fill=core_color, stroke_width=2, stroke_fill=(10, 5, 20))

def create_youtube_thumbnail(
    bg_image_path: str,
    main_title: str,
    subtitle: str,
    badge_text: str,
    output_path: str = "storage/videos/thumbnail.png"
) -> str:
    if os.path.exists(bg_image_path):
        bg = Image.open(bg_image_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), CYBERPUNK["bg_dark"])

    dim_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 70))
    bg.alpha_composite(dim_overlay)

    draw = ImageDraw.Draw(bg)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 90)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
        font_hud = ImageFont.truetype("/System/Library/Fonts/Courier.dfont", 20)
    except Exception:
        font_title = ImageFont.load_default(size=72)
        font_sub = ImageFont.load_default(size=32)
        font_hud = ImageFont.load_default(size=18)

    # 1. Top HUD Ribbon
    draw.line([(50, 40), (WIDTH - 50, 40)], fill=CYBERPUNK["neon_cyan"], width=2)
    draw.text((60, 50), "[ AI HEADLESS STUDIO // SYSTEM 01 ]", font=font_hud, fill=CYBERPUNK["neon_cyan"])
    draw.text((WIDTH - 360, 50), "AUTONOMOUS PRODUCTION", font=font_hud, fill=CYBERPUNK["neon_amber"])

    # 2. Main Title with Glow
    draw_neon_text(
        draw, bg, (60, 160), main_title, font_title,
        core_color=CYBERPUNK["white"],
        glow_color=CYBERPUNK["neon_magenta"],
        glow_radius=20
    )

    # 3. Subtitle with Cyan Glow
    draw_neon_text(
        draw, bg, (64, 280), subtitle, font_sub,
        core_color=CYBERPUNK["neon_cyan"],
        glow_color=CYBERPUNK["neon_cyan"],
        glow_radius=12
    )

    # 4. Badge Ribbon
    badge_x, badge_y = 60, 390
    bbox = draw.textbbox((badge_x + 20, badge_y + 10), badge_text, font=font_sub)
    badge_w = (bbox[2] - bbox[0]) + 40
    badge_h = 56

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=10,
        fill=(255, 0, 128, 220),
        outline=CYBERPUNK["neon_cyan"],
        width=2
    )
    draw.text((badge_x + 20, badge_y + 8), badge_text, font=font_sub, fill=CYBERPUNK["white"])

    # 5. Corner Brackets
    bracket_len = 35
    draw.line([(30, 30), (30 + bracket_len, 30)], fill=CYBERPUNK["neon_cyan"], width=3)
    draw.line([(30, 30), (30, 30 + bracket_len)], fill=CYBERPUNK["neon_cyan"], width=3)
    draw.line([(30, HEIGHT - 30), (30 + bracket_len, HEIGHT - 30)], fill=CYBERPUNK["neon_cyan"], width=3)
    draw.line([(30, HEIGHT - 30), (30, HEIGHT - 30 - bracket_len)], fill=CYBERPUNK["neon_cyan"], width=3)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bg.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"[Thumbnail] Generated YouTube thumbnail: {output_path}")
    return output_path
