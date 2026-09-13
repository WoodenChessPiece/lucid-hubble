"""
src/visualizer/video.py - Headless Video Engine with Audio Spectrum Visualizer
"""

import os
import subprocess
from PIL import Image, ImageDraw

def generate_background_graphic(
    title: str,
    subtitle: str,
    bpm: int,
    key: str,
    output_png: str = "storage/renders/background.png"
) -> str:
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (10, 6, 22, 255))
    draw = ImageDraw.Draw(img)

    horizon_y = int(H * 0.58)

    # 1. Sky Gradient
    for y in range(horizon_y):
        ratio = y / horizon_y
        r = int(12 + ratio * 58)
        g = int(5 + ratio * 12)
        b = int(28 + ratio * 60)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Glowing Horizon Sun
    sun_center = (W // 2, horizon_y - 20)
    sun_radius = 160
    for r in range(sun_radius, 0, -2):
        frac = 1.0 - (r / sun_radius)
        red = 255
        green = int(40 + frac * 200)
        blue = int(140 * (1 - frac))
        draw.ellipse(
            [sun_center[0] - r, sun_center[1] - r, sun_center[0] + r, sun_center[1] + r],
            fill=(red, green, blue, 220)
        )

    # Sun horizontal blinds
    for sy in range(sun_center[1] - 40, horizon_y, 14):
        slit_h = int(3 + (sy - (sun_center[1] - 40)) * 0.15)
        draw.rectangle([sun_center[0] - sun_radius - 10, sy, sun_center[0] + sun_radius + 10, sy + slit_h], fill=(20, 10, 35, 255))

    # Horizon glow
    draw.line([(0, horizon_y), (W, horizon_y)], fill=(255, 0, 128, 255), width=3)
    draw.line([(0, horizon_y+1), (W, horizon_y+1)], fill=(0, 240, 255, 220), width=2)

    # 3. Ground Perspective Grid
    for y in range(horizon_y + 1, H):
        dist = (y - horizon_y) / (H - horizon_y)
        draw.line([(0, y), (W, y)], fill=(int(15 + dist * 5), int(6 + dist * 2), int(25 + dist * 10), 255))

    num_lines = 16
    for i in range(1, num_lines):
        prog = (i / num_lines) ** 2.2
        y_pos = int(horizon_y + prog * (H - horizon_y))
        alpha = int(70 + prog * 180)
        draw.line([(0, y_pos), (W, y_pos)], fill=(0, 230, 255, alpha), width=1 if i < 10 else 2)

    vp_x, vp_y = W // 2, horizon_y
    for i in range(-28, 29):
        bottom_x = vp_x + int(i * (W / 24))
        draw.line([(vp_x, vp_y), (bottom_x, H)], fill=(255, 0, 140, 160), width=1)

    # 4. HUD Typography
    draw.rectangle([40, 40, W - 40, 44], fill=(0, 240, 255, 180))
    draw.text((60, 60), f"SYS // {title.upper()}", fill=(0, 255, 240, 255))
    draw.text((60, 85), f"ENGINE: AUTONOMOUS STUDIO // {subtitle.upper()}", fill=(255, 60, 180, 255))
    draw.text((W - 380, 60), f"TEMPO: {bpm} BPM // KEY: {key.upper()}", fill=(0, 255, 240, 255))
    draw.text((W - 380, 85), "MASTER: -14.0 LUFS EBU R128", fill=(255, 200, 50, 255))

    # Center Title
    draw.text((W // 2 - 260, int(H * 0.22)), title.upper(), fill=(255, 255, 255, 255))
    draw.text((W // 2 - 190, int(H * 0.22) + 35), f"[ {subtitle.upper()} ]", fill=(0, 255, 240, 220))

    # Bottom HUD
    draw.rectangle([40, H - 50, W - 40, H - 46], fill=(255, 0, 128, 180))
    draw.text((60, H - 35), "AI HEADLESS STUDIO // BUILT FOR YOUTUBE MONETIZATION", fill=(200, 200, 255, 200))
    draw.text((W - 320, H - 35), "GOOGLE DRIVE CLOUD STORAGE", fill=(0, 255, 240, 200))

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    img.save(output_png)
    return output_png

def render_video_with_visualizer(
    bg_image_path: str,
    audio_wav_path: str,
    output_mp4_path: str,
    fps: int = 30,
    use_hardware_accel: bool = True
) -> str:
    """
    Renders 1080p MP4 with real-time frequency spectrum visualizer overlaid.
    Uses Apple Silicon VideoToolbox acceleration (h264_videotoolbox) when available.
    """
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)

    filter_complex = (
        "[1:a]showfreqs=s=1840x280:mode=bar:ascale=log:fscale=log:colors=0x00f0ff|0xff0080[spec];"
        "[0:v][spec]overlay=40:720:shortest=1[outv]"
    )

    # Choose hardware encoder on Apple Silicon if requested
    vcodec = ["-c:v", "h264_videotoolbox", "-b:v", "4M"] if use_hardware_accel else ["-c:v", "libx264", "-preset", "fast", "-crf", "19"]

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", bg_image_path,
        "-i", audio_wav_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a",
        *vcodec,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        output_mp4_path
    ]

    print(f"[FFmpeg] Rendering video (Hardware Accel: {use_hardware_accel}): {output_mp4_path}...")
    subprocess.run(cmd, check=True)
    print(f"[FFmpeg] Video rendering complete: {output_mp4_path}")
    return output_mp4_path
