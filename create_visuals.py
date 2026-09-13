from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1920, 1080
img = Image.new("RGBA", (W, H), (10, 6, 22, 255))
draw = ImageDraw.Draw(img)

# 1. Background gradient (deep space to neon horizon)
horizon_y = int(H * 0.58)
for y in range(horizon_y):
    ratio = y / horizon_y
    r = int(12 + ratio * (70 - 12))
    g = int(5 + ratio * (15 - 5))
    b = int(28 + ratio * (85 - 28))
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# 2. Glowing synthwave sun on the horizon
sun_center = (W // 2, horizon_y - 20)
sun_radius = 160
for r in range(sun_radius, 0, -2):
    frac = 1.0 - (r / sun_radius)
    # Pink to bright orange/yellow gradient
    red = 255
    green = int(40 + frac * 200)
    blue = int(140 * (1 - frac))
    alpha = int(220)
    draw.ellipse(
        [sun_center[0] - r, sun_center[1] - r, sun_center[0] + r, sun_center[1] + r],
        fill=(red, green, blue, alpha)
    )

# Sun horizontal blind slits
for sy in range(sun_center[1] - 40, horizon_y, 14):
    slit_h = int(3 + (sy - (sun_center[1] - 40)) * 0.15)
    draw.rectangle([sun_center[0] - sun_radius - 10, sy, sun_center[0] + sun_radius + 10, sy + slit_h], fill=(20, 10, 35, 255))

# 3. Horizon glow line
draw.line([(0, horizon_y), (W, horizon_y)], fill=(255, 0, 128, 255), width=3)
draw.line([(0, horizon_y+1), (W, horizon_y+1)], fill=(0, 240, 255, 220), width=2)

# 4. Synthwave ground perspective grid
for y in range(horizon_y + 1, H):
    dist = (y - horizon_y) / (H - horizon_y)
    r = int(15 + dist * 5)
    g = int(6 + dist * 2)
    b = int(25 + dist * 10)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# Perspective horizontal lines (accelerating towards camera)
num_lines = 16
for i in range(1, num_lines):
    prog = (i / num_lines) ** 2.2
    y_pos = int(horizon_y + prog * (H - horizon_y))
    alpha = int(70 + prog * 180)
    draw.line([(0, y_pos), (W, y_pos)], fill=(0, 230, 255, alpha), width=1 if i < 10 else 2)

# Perspective vertical/diagonal grid lines fanning out from center vanishing point
vp_x, vp_y = W // 2, horizon_y
num_spread = 28
for i in range(-num_spread, num_spread + 1):
    bottom_x = vp_x + int(i * (W / 24))
    draw.line([(vp_x, vp_y), (bottom_x, H)], fill=(255, 0, 140, 160), width=1)

# 5. Cyberpunk Typography / Frame
# Top HUD Header
draw.rectangle([40, 40, W - 40, 44], fill=(0, 240, 255, 180))
draw.text((60, 60), "SYS // PROTOCOL: CYBERPUNK SYNTHWAVE", fill=(0, 255, 240, 255))
draw.text((60, 85), "STATUS: AUTONOMOUS AUDIO PIPELINE ACTIVE", fill=(255, 60, 180, 255))
draw.text((W - 380, 60), "TEMPO: 118 BPM // KEY: D MINOR", fill=(0, 255, 240, 255))
draw.text((W - 380, 85), "OUTPUT: MASTER 24-BIT STEREO", fill=(255, 200, 50, 255))

# Center Title Banner
title_box_top = int(H * 0.22)
draw.text((W // 2 - 290, title_box_top), "N E O N   P R O T O C O L", fill=(255, 255, 255, 255))
draw.text((W // 2 - 180, title_box_top + 35), "[ DARK SYNTHWAVE // DTM-01 ]", fill=(0, 255, 240, 220))

# Bottom HUD
draw.rectangle([40, H - 50, W - 40, H - 46], fill=(255, 0, 128, 180))
draw.text((60, H - 35), "AI AUTONOMOUS FACTORY // READY FOR YOUTUBE MONETIZATION", fill=(200, 200, 255, 200))
draw.text((W - 320, H - 35), "MASTER ENGINE: HEADLESS V1", fill=(0, 255, 240, 200))

img.save("cyberpunk_bg.png")
print("Saved cyberpunk_bg.png successfully!")
