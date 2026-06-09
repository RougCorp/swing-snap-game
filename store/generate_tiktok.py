#!/usr/bin/env python3
"""
TikTok beta recruitment video — v4 (dynamic + prominent text)

Improvements vs v3:
  - Faster pacing (3s sections)
  - Bigger zoom range (1.0 → 1.15)
  - Text: outline stroke + stronger glow + colored accent bar
  - Slam transition: black + white flash
  - Vignette on screenshots for depth
  - Text slides in from side (alternates L/R)
  - CTA: more energetic with pulsing border
"""

import math
import subprocess
import shutil
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR    = Path(__file__).parent
VIDEO_DIR  = OUT_DIR / "video"
ALL_FRAMES = VIDEO_DIR / "tiktok_frames"
FFMPEG     = "/opt/homebrew/bin/ffmpeg"
SHOTS_DIR  = OUT_DIR / "appstore" / "iphone-6.7" / "fr"

FONT_PATH      = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX  = 2

VW, VH = 1080, 1920
FPS    = 24
frame_counter = 0


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def next_frame_path():
    global frame_counter
    p = ALL_FRAMES / f"frame_{frame_counter:05d}.png"
    frame_counter += 1
    return p

def save_frame(img):
    img.convert("RGB").save(str(next_frame_path()), "PNG")

def load_font(size, weight="heavy"):
    try:
        idx = FONT_HEAVY_IDX if weight == "heavy" else FONT_DEMI_IDX
        return ImageFont.truetype(FONT_PATH, size, index=idx)
    except Exception:
        return ImageFont.load_default()

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)


# ─── SCREENSHOT PREP ──────────────────────────────────────────────────────────
def load_screenshot(path):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    target_ratio = VW / VH
    img_ratio    = iw / ih
    if img_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        x0 = (iw - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        y0 = (ih - new_h) // 2
        img = img.crop((0, y0, iw, y0 + new_h))
    return img.resize((VW, VH), Image.LANCZOS)


# ─── VIGNETTE ─────────────────────────────────────────────────────────────────
def add_vignette(img, strength=160):
    """Circular dark vignette around edges for depth."""
    vig = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)
    cx, cy = VW // 2, VH // 2
    max_r = math.sqrt(cx**2 + cy**2)
    steps = 30
    for i in range(steps, 0, -1):
        r_x = int(cx * i / steps)
        r_y = int(cy * i / steps)
        a = int(strength * (1 - i / steps) ** 1.8)
        draw.ellipse([cx - r_x, cy - r_y, cx + r_x, cy + r_y],
                     fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")


# ─── GRADIENT BARS ────────────────────────────────────────────────────────────
def add_gradient(img, top_h=220, bottom_h=300, top_alpha=160, bottom_alpha=180,
                 center_dark=True):
    overlay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(top_h):
        a = int(top_alpha * ease_in_out(1 - y / top_h))
        draw.line([(0, y), (VW, y)], fill=(0, 0, 0, a))
    for y in range(bottom_h):
        a = int(bottom_alpha * ease_in_out(y / bottom_h))
        draw.line([(0, VH - bottom_h + y), (VW, VH - bottom_h + y)], fill=(0, 0, 0, a))
    # Center horizontal darkening band for centered text readability
    if center_dark:
        band_h = 700
        band_y0 = (VH - band_h) // 2
        for y in range(band_h):
            t = 1 - abs(y - band_h // 2) / (band_h // 2)
            a = int(140 * ease_in_out(t))
            draw.line([(0, band_y0 + y), (VW, band_y0 + y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


# ─── KEN BURNS ────────────────────────────────────────────────────────────────
def ken_burns_frame(base, progress, zoom_start=1.0, zoom_end=1.15,
                    pan_x=(0.0, 0.0), pan_y=(0.0, 0.0)):
    t = ease_in_out(progress)
    scale = lerp(zoom_start, zoom_end, t)
    px = lerp(pan_x[0], pan_x[1], t) * VW
    py = lerp(pan_y[0], pan_y[1], t) * VH

    new_w = int(VW * scale)
    new_h = int(VH * scale)
    zoomed = base.resize((new_w, new_h), Image.LANCZOS)

    cx = max(0, min((new_w - VW) // 2 + int(px), new_w - VW))
    cy = max(0, min((new_h - VH) // 2 + int(py), new_h - VH))
    return zoomed.crop((cx, cy, cx + VW, cy + VH))


# ─── STROKE TEXT HELPER ───────────────────────────────────────────────────────
def draw_stroked_text(draw, pos, text, font, fill, stroke_fill, stroke_w=3, anchor="mt"):
    x, y = pos
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx*dx + dy*dy <= stroke_w*stroke_w + 1:
                draw.text((x + dx, y + dy), text, fill=stroke_fill, font=font, anchor=anchor)
    draw.text((x, y), text, fill=fill, font=font, anchor=anchor)


# ─── TEXT BLOCK ───────────────────────────────────────────────────────────────
def draw_text_block(img, lines, position, progress, accent=(160, 100, 255),
                    slide_dir="up"):
    """
    lines: list of (text, size, weight, color_rgb)
    slide_dir: "up" | "left" | "right"
    """
    # Animate: fast ease-out in, fade out at end
    if progress < 0.18:
        alpha = ease_out(progress / 0.18)
        if slide_dir == "up":
            slide_x, slide_y = 0, int(60 * (1 - alpha))
        elif slide_dir == "left":
            slide_x, slide_y = int(-80 * (1 - alpha)), 0
        else:
            slide_x, slide_y = int(80 * (1 - alpha)), 0
    elif progress > 0.82:
        alpha = ease_in_out((1.0 - progress) / 0.18)
        slide_x, slide_y = 0, 0
    else:
        alpha = 1.0
        slide_x, slide_y = 0, 0

    if alpha <= 0.02:
        return img

    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Measure
    fonts, heights, widths = [], [], []
    for text, size, weight, color in lines:
        font = load_font(size, weight)
        bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
        fonts.append(font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    gap = 16
    total_h = sum(heights) + gap * (len(lines) - 1)
    max_w = max(widths) if widths else 1
    pad_x, pad_y = 56, 36

    if position == "bottom":
        block_y = VH - total_h - 130 + slide_y
    elif position == "top":
        block_y = 110 + slide_y
    else:  # center
        block_y = (VH - total_h) // 2 + slide_y

    bx = slide_x
    x0 = (VW - max_w) // 2 - pad_x + bx
    x1 = (VW + max_w) // 2 + pad_x + bx
    y0 = block_y - pad_y
    y1 = block_y + total_h + pad_y

    # Pill with colored border
    pill = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    # Glow border
    for expand in range(8, 0, -1):
        bd_a = int(60 * (1 - expand / 8) * alpha)
        pd.rounded_rectangle(
            [x0 - expand, y0 - expand, x1 + expand, y1 + expand],
            radius=30 + expand, fill=(*accent, bd_a))
    # Dark fill
    pd.rounded_rectangle([x0, y0, x1, y1], radius=28,
                         fill=(0, 0, 0, int(210 * alpha)))
    # Accent top bar
    bar_h = 6
    pd.rounded_rectangle([x0, y0, x1, y0 + bar_h], radius=4,
                         fill=(*accent, int(255 * alpha)))
    img = Image.alpha_composite(img, pill)

    # Strong glow behind text block
    glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([x0 - 20, y0 - 20, x1 + 20, y1 + 20], radius=40,
                         fill=(*accent, int(35 * alpha)))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img, glow)

    # Text
    draw = ImageDraw.Draw(img)
    cy = block_y
    for i, (text, size, weight, color) in enumerate(lines):
        font = fonts[i]
        x = VW // 2 + bx
        a_int = int(255 * alpha)
        stroke_c = (0, 0, 0, int(180 * alpha))
        draw_stroked_text(draw, (x, cy), text, font,
                          fill=(*color, a_int),
                          stroke_fill=stroke_c,
                          stroke_w=3 if i == 0 else 2,
                          anchor="mt")
        cy += heights[i] + gap

    return img.convert("RGB")


# ─── SECTION ──────────────────────────────────────────────────────────────────
def render_section(shot_path, n_frames, lines, position="bottom",
                   accent=(160, 100, 255),
                   zoom_start=1.0, zoom_end=1.15,
                   pan_x=(0.0, 0.0), pan_y=(0.0, 0.0),
                   slide_dir="up"):
    base = load_screenshot(shot_path)
    for f in range(n_frames):
        progress = f / max(n_frames - 1, 1)
        frame = ken_burns_frame(base, progress,
                                zoom_start=zoom_start, zoom_end=zoom_end,
                                pan_x=pan_x, pan_y=pan_y)
        frame = add_vignette(frame, strength=140)
        frame = add_gradient(frame)
        frame = draw_text_block(frame, lines, position, progress, accent, slide_dir)
        save_frame(frame)


# ─── SLAM TRANSITION ──────────────────────────────────────────────────────────
def render_slam(n_black=3, n_white=4):
    """Punchy slam cut: quick black then white flash."""
    black = Image.new("RGB", (VW, VH), (0, 0, 0))
    white = Image.new("RGB", (VW, VH), (255, 255, 255))
    for _ in range(n_black):
        save_frame(black)
    for _ in range(n_white):
        save_frame(white)


# ─── CTA CARD ─────────────────────────────────────────────────────────────────
def render_cta(duration_s, accent=(60, 220, 120)):
    n = int(duration_s * FPS)
    bg = (4, 18, 10)
    icon_path = OUT_DIR.parent / "www" / "web-app-manifest-512x512.png"
    icon = None
    if icon_path.exists():
        icon = Image.open(icon_path).convert("RGBA").resize((170, 170), Image.LANCZOS)
        mask = Image.new("L", (170, 170), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 170, 170), radius=38, fill=255)
        icon.putalpha(mask)

    rng = random.Random(7)
    particles = [(rng.randint(0, VW), rng.randint(0, VH),
                  rng.randint(1, 5), rng.randint(1, 6), rng.randint(30, 160))
                 for _ in range(60)]

    text_blocks = [
        ("BESOIN DE",                54, "demi",  (170, 230, 200)),
        ("20 TESTEURS",             104, "heavy", (80, 255, 140)),
        ("Android",                  54, "demi",  (170, 230, 200)),
        ("",                         20, "demi",  (0, 0, 0)),
        ("Envoie-moi un DM",         50, "heavy", (255, 255, 255)),
        ("ou clique le lien en bio", 38, "demi",  (150, 210, 170)),
        ("100% gratuit",             36, "demi",  (100, 180, 130)),
    ]

    for f in range(n):
        progress = f / max(n - 1, 1)
        pulse = 0.82 + 0.18 * math.sin(progress * math.pi * 4)

        img = Image.new("RGBA", (VW, VH), (*bg, 255))
        draw = ImageDraw.Draw(img)

        # Gradient bg
        for y in range(0, VH, 2):
            t = y / VH
            c = tuple(int(bg[i] * (1 + 0.3 * t)) for i in range(3))
            draw.line([(0, y), (VW, y)], fill=c)

        # Big glow
        glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for i in range(22, 0, -1):
            r = int(VW * 0.6 * pulse * i / 22)
            a = int(45 * (1 - i / 22) * pulse)
            gd.ellipse([VW//2 - r, VH//2 - r, VW//2 + r, VH//2 + r],
                       fill=(*accent, a))
        img = Image.alpha_composite(img, glow)

        # Pulsing border ring
        ring = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        ring_r = int(VW * 0.42 * (1 + 0.04 * math.sin(progress * math.pi * 6)))
        for thick in range(6, 0, -1):
            ra = int(80 * (thick / 6) * pulse)
            rd.ellipse([VW//2 - ring_r - thick, VH//2 - ring_r - thick,
                        VW//2 + ring_r + thick, VH//2 + ring_r + thick],
                       outline=(*accent, ra), width=2)
        img = Image.alpha_composite(img, ring)

        # Particles
        pov = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pov)
        for px, py, pr, speed, palpha in particles:
            apy = (py - int(f * speed * 2.5)) % VH
            pd.ellipse([px - pr, apy - pr, px + pr, apy + pr],
                       fill=(*accent, int(palpha * 0.6)))
        img = Image.alpha_composite(img, pov)

        # Fade in
        alpha = ease_out(min(1.0, progress / 0.15))

        # Icon
        content_y = VH // 2 - 60
        if icon:
            ic = icon.copy()
            ic.putalpha(Image.eval(ic.getchannel("A"), lambda a: int(a * alpha)))
            img.paste(ic, (VW // 2 - 85, VH // 2 - 380), ic)

        # Text
        draw = ImageDraw.Draw(img)
        cy = content_y
        for i, (text, size, weight, color) in enumerate(text_blocks):
            if not text:
                cy += size
                continue
            font = load_font(size, weight)
            delay = max(0.0, (progress - i * 0.04)) / 0.15
            lo = min(1.0, delay) * alpha
            offset = int(22 * (1 - min(1.0, ease_out(delay))))
            if lo > 0:
                # Glow
                gl = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                gld = ImageDraw.Draw(gl)
                for dx in range(-5, 6, 3):
                    for dy in range(-5, 6, 3):
                        if dx*dx + dy*dy <= 25:
                            gld.text((VW//2 + dx, cy + offset + dy), text,
                                     fill=(*accent, int(35 * lo * pulse)),
                                     font=font, anchor="mt")
                gl = gl.filter(ImageFilter.GaussianBlur(radius=5))
                img = Image.alpha_composite(img, gl)
                draw = ImageDraw.Draw(img)
                # Stroke + text
                for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                    draw.text((VW//2 + dx, cy + offset + dy), text,
                              fill=(0, 0, 0, int(200 * lo)), font=font, anchor="mt")
                draw.text((VW//2, cy + offset), text,
                          fill=(*color, int(255 * lo)), font=font, anchor="mt")
            try:
                bbox = ImageDraw.Draw(img).textbbox((0,0), text, font=font, anchor="lt")
                cy += (bbox[3] - bbox[1]) + 18
            except Exception:
                cy += size + 18

        save_frame(img)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    global frame_counter
    frame_counter = 0

    print("=== Swing & Snap — TikTok v4 ===")
    print(f"    {VW}x{VH} — {FPS}fps\n")

    if ALL_FRAMES.exists():
        shutil.rmtree(ALL_FRAMES)
    ALL_FRAMES.mkdir(parents=True)

    S = lambda name: SHOTS_DIR / f"swing_snap_fr_{name}.png"
    SEC = FPS  # 24 frames

    # ── [0:00] GAMEPLAY 1 — hook ────────────────────
    print("  [0:00] Hook")
    render_section(S("06_gameplay1"), 3 * SEC,
        lines=[
            ("J'AI FAIT UN JEU",        88, "heavy", (220, 160, 255)),
            ("et j'ai besoin de vous",  48, "demi",  (200, 200, 200)),
        ],
        position="center", accent=(142, 99, 180),
        zoom_start=1.0, zoom_end=1.16,
        pan_x=(0.0, 0.03), pan_y=(0.0, -0.02),
        slide_dir="up")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:03] GAMEPLAY 2 — un doigt ────────────────
    print("  [0:03] Un doigt")
    render_section(S("07_gameplay2"), 3 * SEC,
        lines=[
            ("UN DOIGT.",  90, "heavy", (255, 255, 255)),
            ("UN SWING.",  90, "heavy", (180, 130, 255)),
        ],
        position="center", accent=(142, 99, 180),
        zoom_start=1.14, zoom_end=1.0,
        pan_x=(0.03, -0.02), pan_y=(0.0, 0.02),
        slide_dir="left")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:06] GAMEPLAY 3 — facile/impossible ────────
    print("  [0:06] Facile/impossible")
    render_section(S("08_gameplay3"), 3 * SEC,
        lines=[
            ("FACILE A APPRENDRE...", 72, "heavy", (255, 220, 80)),
            ("impossible a maitriser",54, "demi",  (255, 130, 60)),
        ],
        position="center", accent=(255, 120, 40),
        zoom_start=1.0, zoom_end=1.14,
        pan_x=(-0.02, 0.02), pan_y=(0.01, -0.01),
        slide_dir="right")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:09] BALLS ─────────────────────────────────
    print("  [0:09] Balls")
    render_section(S("02_balls"), 3 * SEC,
        lines=[
            ("20+ BALLES",            90, "heavy", (255, 220, 60)),
            ("A DEBLOQUER",           90, "heavy", (255, 180, 30)),
            ("en jouant, pas en payant", 40, "demi", (200, 200, 200)),
        ],
        position="center", accent=(255, 180, 40),
        zoom_start=1.12, zoom_end=1.0,
        pan_x=(0.0, 0.0), pan_y=(0.02, -0.02),
        slide_dir="up")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:12] TRAILS ────────────────────────────────
    print("  [0:12] Trails")
    render_section(S("03_trails"), 3 * SEC,
        lines=[
            ("TRAILS & FONDS",          80, "heavy", (160, 210, 255)),
            ("PERSONNALISABLES",         80, "heavy", (100, 180, 255)),
        ],
        position="center", accent=(80, 160, 255),
        zoom_start=1.0, zoom_end=1.15,
        pan_x=(-0.03, 0.03), pan_y=(0.0, 0.0),
        slide_dir="left")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:15] MISSIONS ──────────────────────────────
    print("  [0:15] Missions")
    render_section(S("04_missions"), 3 * SEC,
        lines=[
            ("MISSIONS QUOTIDIENNES", 66, "heavy", (255, 130, 150)),
            ("+ SUCCES A DEBLOQUER",  66, "heavy", (255, 90, 110)),
        ],
        position="center", accent=(255, 80, 100),
        zoom_start=1.14, zoom_end=1.0,
        pan_x=(0.02, -0.02), pan_y=(-0.01, 0.01),
        slide_dir="right")
    render_slam()
    print(f"      [{frame_counter}]")

    # ── [0:18] CTA ───────────────────────────────────
    print("  [0:18] CTA")
    render_cta(duration_s=5.0, accent=(60, 220, 120))
    print(f"      [{frame_counter} total]")

    # ── ENCODE ───────────────────────────────────────
    print(f"\n  Encoding {frame_counter} frames...")
    output = VIDEO_DIR / "swing_snap_tiktok.mp4"
    r = subprocess.run([
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", str(ALL_FRAMES / "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "15", "-preset", "medium",
        "-movflags", "+faststart",
        str(output)
    ], capture_output=True, text=True)

    if r.returncode != 0:
        print(f"  Error: {r.stderr[-500:]}")
    else:
        info = subprocess.run([FFMPEG, "-i", str(output)], capture_output=True, text=True)
        dur  = [l for l in info.stderr.split('\n') if 'Duration' in l]
        dur  = dur[0].split('Duration:')[1].split(',')[0].strip() if dur else "?"
        mb   = os.path.getsize(output) / 1024 / 1024
        print(f"\n{'='*50}")
        print(f"  DONE — {mb:.1f} MB — {dur}")
        print(f"  {output}")
        print(f"{'='*50}")

    shutil.rmtree(ALL_FRAMES, ignore_errors=True)


if __name__ == "__main__":
    main()
