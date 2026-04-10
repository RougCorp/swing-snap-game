#!/usr/bin/env python3
"""Generate store preview video — ALL frames as PNG at 1080x1920, single encode.

No Playwright record_video. Everything captured as screenshots.
All frames at exact 1080x1920. Single ffmpeg encode = perfect video.
"""

import asyncio
import math
import random
import subprocess
import shutil
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = Path(__file__).parent
VIDEO_DIR = OUT_DIR / "video"
ALL_FRAMES = VIDEO_DIR / "all_frames"
GAME_URL = "http://localhost:8765"
FFMPEG = "/tmp/ffmpeg_arm/ffmpeg"

FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

# Final video size (9:16 standard store format)
VW, VH = 1080, 1920
FPS = 24  # Smooth enough, fewer frames = faster generation

# Global frame counter
frame_counter = 0


def next_frame_path():
    global frame_counter
    p = ALL_FRAMES / f"frame_{frame_counter:05d}.png"
    frame_counter += 1
    return p


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def save_frame(img):
    """Save a PIL image as next frame."""
    path = next_frame_path()
    img.convert("RGB").save(str(path), "PNG")


def save_screenshot_as_frame(screenshot_path):
    """Load a Playwright screenshot, resize to VW x VH, save as frame."""
    img = Image.open(screenshot_path).convert("RGB")
    img = img.resize((VW, VH), Image.LANCZOS)
    save_frame(img)


# ────────────────────────────────────────
# TITLE CARDS
# ────────────────────────────────────────
def generate_title_frames(lines, duration_s=2.5, bg=(12, 5, 25),
                          neon=(160, 80, 255), text_color=(220, 170, 255),
                          show_icon=False):
    """Generate title card frames directly into the global sequence."""
    n_frames = int(duration_s * FPS)

    try:
        font_big = ImageFont.truetype(FONT_PATH, 72, index=FONT_HEAVY_IDX)
        font_med = ImageFont.truetype(FONT_PATH, 46, index=FONT_DEMI_IDX)
    except:
        font_big = ImageFont.load_default()
        font_med = font_big

    icon = None
    if show_icon:
        icon_path = OUT_DIR.parent / "www" / "web-app-manifest-512x512.png"
        if icon_path.exists():
            icon = Image.open(icon_path).convert("RGBA").resize((160, 160), Image.LANCZOS)
            mask = Image.new("L", (160, 160), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 160, 160), radius=36, fill=255)
            icon.putalpha(mask)

    rng = random.Random(hash(str(lines)))
    particles = [(rng.randint(0, VW), rng.randint(0, VH),
                  rng.randint(1, 3), rng.randint(1, 4), rng.randint(50, 150))
                 for _ in range(30)]

    for f in range(n_frames):
        progress = f / n_frames
        img = Image.new("RGBA", (VW, VH), (*bg, 255))
        draw = ImageDraw.Draw(img)

        # Gradient
        bg_light = tuple(min(255, c + 20) for c in bg)
        for y in range(0, VH, 2):  # Step 2 for speed
            t = y / VH
            c = lerp_color(bg, bg_light, t * 0.4 + 0.1)
            draw.rectangle([(0, y), (VW, y + 1)], fill=c)

        # Pulsing glow
        pulse = 0.85 + 0.15 * math.sin(progress * math.pi * 2)
        glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        glow_r = int(VW * 0.6 * pulse)
        for i in range(15, 0, -1):
            r = int(glow_r * i / 15)
            a = int(40 * (1 - i / 15) * pulse)
            gd.ellipse([VW//2 - r, VH//2 - r, VW//2 + r, VH//2 + r], fill=(*neon, a))
        img = Image.alpha_composite(img, glow)

        # Particles
        p_overlay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        pd = ImageDraw.Draw(p_overlay)
        for px, py, pr, speed, alpha in particles:
            apy = (py - int(f * speed * 2)) % VH
            pd.ellipse([px - pr, apy - pr, px + pr, apy + pr], fill=(255, 255, 255, alpha))
        img = Image.alpha_composite(img, p_overlay)

        # Fade in/out
        if progress < 0.15:
            opacity = progress / 0.15
        elif progress > 0.85:
            opacity = (1.0 - progress) / 0.15
        else:
            opacity = 1.0

        # Icon
        content_y = VH // 2
        if icon and show_icon:
            content_y = VH // 2 + 25
            icon_y = VH // 2 - 180
            icon_copy = icon.copy()
            a_ch = icon_copy.getchannel('A')
            icon_copy.putalpha(Image.eval(a_ch, lambda a: int(a * opacity)))
            img.paste(icon_copy, (VW // 2 - 80, icon_y), icon_copy)

        # Text
        draw = ImageDraw.Draw(img)
        for i, line in enumerate(lines):
            if not line:
                continue
            font = font_big if i == 0 else font_med
            color = text_color if i == 0 else (255, 255, 255)
            line_y = content_y + i * 75

            line_delay = max(0, (progress - i * 0.05)) / 0.15
            line_opacity = min(1.0, line_delay) * opacity
            line_offset = int(20 * (1 - min(1.0, line_delay)))

            if line_opacity > 0:
                # Glow
                glow_txt = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                gt = ImageDraw.Draw(glow_txt)
                g_alpha = int(30 * line_opacity * pulse)
                for dx in range(-3, 4, 2):
                    for dy in range(-3, 4, 2):
                        if dx*dx + dy*dy <= 9:
                            gt.text((VW//2 + dx, line_y + line_offset + dy), line,
                                    fill=(*neon, g_alpha), font=font, anchor="mt")
                glow_txt = glow_txt.filter(ImageFilter.GaussianBlur(radius=2))
                img = Image.alpha_composite(img, glow_txt)

                draw = ImageDraw.Draw(img)
                draw.text((VW // 2, line_y + line_offset), line,
                          fill=(*color, int(255 * line_opacity)), font=font, anchor="mt")

        save_frame(img)


# ────────────────────────────────────────
# GAMEPLAY CAPTURE (screenshots → frames)
# ────────────────────────────────────────
async def capture_gameplay_frames(page, actions, duration_hint_s=3.0):
    """Execute actions while capturing screenshots as frames.
    Each screenshot becomes exactly one video frame at VW x VH.
    Captures at ~12fps for smooth-enough motion, each frame saved twice for 24fps output.
    """
    capture_interval = 55  # ms between captures (~18 raw fps → smoother)
    action_idx = 0
    elapsed = 0

    # Pre-execute setup actions (goto, clicks before gameplay)
    for action in actions:
        cmd = action["do"]
        if cmd == "goto":
            await page.goto(GAME_URL, wait_until="networkidle")
            await page.add_style_tag(content='.screen{max-width:92vw!important;width:92vw!important}.ui-layer{padding:0!important}')
            await page.wait_for_timeout(action.get("wait", 1500))
        elif cmd == "click":
            await page.click(action["sel"])
            await page.wait_for_timeout(action.get("wait", 400))
        elif cmd == "wait_setup":
            await page.wait_for_timeout(action["ms"])
        elif cmd == "capture_start":
            break
        action_idx += 1

    # Now capture frames while executing remaining actions
    remaining = actions[action_idx:]
    tap_schedule = []
    total_ms = 0

    for action in remaining:
        cmd = action["do"]
        if cmd == "capture_start":
            continue
        elif cmd == "tap":
            tap_schedule.append((total_ms, action["x"], action["y"]))
            total_ms += action.get("wait", 200)
        elif cmd == "wait":
            total_ms += action["ms"]
        elif cmd == "scroll":
            tap_schedule.append((total_ms, "scroll", action.get("dy", 200)))
            total_ms += action.get("wait", 300)
        elif cmd == "click":
            tap_schedule.append((total_ms, "click", action["sel"]))
            total_ms += action.get("wait", 400)

    if total_ms == 0:
        total_ms = int(duration_hint_s * 1000)

    tap_idx = 0
    elapsed = 0

    while elapsed <= total_ms:
        # Execute scheduled taps
        while tap_idx < len(tap_schedule) and elapsed >= tap_schedule[tap_idx][0]:
            t = tap_schedule[tap_idx]
            if t[1] == "scroll":
                await page.mouse.wheel(0, t[2])
            elif t[1] == "click":
                await page.click(t[2])
            else:
                await page.mouse.click(t[1], t[2])
            tap_idx += 1

        # Capture screenshot
        tmp_path = f"/tmp/game_frame_{elapsed}.png"
        await page.screenshot(path=tmp_path)
        save_screenshot_as_frame(tmp_path)
        # Save twice for 24fps from ~12fps capture
        save_screenshot_as_frame(tmp_path)
        os.unlink(tmp_path)

        await page.wait_for_timeout(capture_interval)
        elapsed += capture_interval


async def capture_static_screen(page, actions, hold_s=2.0):
    """Capture a static screen (menu, shop, etc) and hold it as frames."""
    for action in actions:
        cmd = action["do"]
        if cmd == "goto":
            await page.goto(GAME_URL, wait_until="networkidle")
            await page.add_style_tag(content='.screen{max-width:92vw!important;width:92vw!important}.ui-layer{padding:0!important}')
            await page.wait_for_timeout(action.get("wait", 1500))
        elif cmd == "click":
            await page.click(action["sel"])
            await page.wait_for_timeout(action.get("wait", 400))
        elif cmd == "wait":
            await page.wait_for_timeout(action["ms"])
        elif cmd == "scroll":
            await page.mouse.wheel(0, action.get("dy", 200))
            await page.wait_for_timeout(action.get("wait", 300))

    # Capture one screenshot and hold it
    tmp_path = "/tmp/game_static.png"
    await page.screenshot(path=tmp_path)
    n_frames = int(hold_s * FPS)
    for _ in range(n_frames):
        save_screenshot_as_frame(tmp_path)
    os.unlink(tmp_path)


async def capture_animated_screen(page, actions, duration_s=3.0):
    """Capture an animated sequence (scrolling, navigating) as frames."""
    capture_interval = 55
    total_ms = int(duration_s * 1000)

    # Execute each action with captures in between
    for action in actions:
        cmd = action["do"]
        if cmd == "goto":
            await page.goto(GAME_URL, wait_until="networkidle")
            await page.add_style_tag(content='.screen{max-width:92vw!important;width:92vw!important}.ui-layer{padding:0!important}')
            await page.wait_for_timeout(800)
        elif cmd == "click":
            await page.click(action["sel"])
        elif cmd == "scroll":
            await page.mouse.wheel(0, action.get("dy", 200))

        # Capture frames during wait
        wait_ms = action.get("wait", 400)
        elapsed = 0
        while elapsed < wait_ms:
            tmp = f"/tmp/game_anim_{elapsed}.png"
            await page.screenshot(path=tmp)
            save_screenshot_as_frame(tmp)
            os.unlink(tmp)
            await page.wait_for_timeout(capture_interval)
            elapsed += capture_interval


# ────────────────────────────────────────
# MAIN
# ────────────────────────────────────────
async def main():
    global frame_counter
    frame_counter = 0

    print(f"=== Swing & Snap — Store Video v3 ===")
    print(f"    All frames: {VW}x{VH} PNG → single ffmpeg encode")
    print(f"    FPS: {FPS}\n")

    if ALL_FRAMES.exists():
        shutil.rmtree(ALL_FRAMES)
    ALL_FRAMES.mkdir(parents=True)

    from playwright.async_api import async_playwright

    # ── ACT 1: INTRO ──
    print("  🎬 Act 1: Intro")
    print("    → Title card")
    generate_title_frames(
        ["SWING & SNAP", "Le jeu qui rend accro !"],
        duration_s=3.0, bg=(12, 5, 25),
        neon=(142, 99, 180), text_color=(200, 160, 255),
        show_icon=True
    )
    print(f"      [{frame_counter} frames]")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 430, "height": 932},
            device_scale_factor=3,  # 1290x2796 → resized to 1080x1920
            locale="fr-FR",
        )

        # ── Menu (2s) ──
        print("    → Menu")
        await capture_static_screen(page, [
            {"do": "goto", "wait": 2000},
        ], hold_s=2.0)
        print(f"      [{frame_counter} frames]")

        # ── ACT 2: GAMEPLAY ──
        print("\n  🎬 Act 2: Gameplay")
        print("    → Title: Un seul doigt")
        generate_title_frames(
            ["Un seul doigt suffit", "pour des heures de jeu"],
            duration_s=2.5, bg=(5, 10, 30),
            neon=(40, 200, 255), text_color=(120, 220, 255)
        )
        print(f"      [{frame_counter} frames]")

        # Gameplay (5s)
        print("    → Gameplay")
        await page.goto(GAME_URL, wait_until="networkidle")
        await page.add_style_tag(content='.screen{max-width:92vw!important;width:92vw!important}.ui-layer{padding:0!important}')
        await page.wait_for_timeout(1500)
        await page.click("#btnPlay")
        await page.wait_for_timeout(1000)

        await capture_gameplay_frames(page, [
            {"do": "capture_start"},
            {"do": "tap", "x": 215, "y": 600, "wait": 450},
            {"do": "tap", "x": 250, "y": 450, "wait": 450},
            {"do": "tap", "x": 180, "y": 380, "wait": 400},
            {"do": "tap", "x": 300, "y": 420, "wait": 400},
            {"do": "tap", "x": 200, "y": 350, "wait": 400},
            {"do": "tap", "x": 280, "y": 500, "wait": 400},
            {"do": "tap", "x": 170, "y": 400, "wait": 400},
            {"do": "tap", "x": 310, "y": 380, "wait": 500},
            {"do": "wait", "ms": 600},
        ], duration_hint_s=5.0)
        print(f"      [{frame_counter} frames]")

        # ── ACT 3: COLLECTION ──
        print("\n  🎬 Act 3: Collection")
        print("    → Title: 33 balles")
        generate_title_frames(
            ["33 balles uniques", "à collectionner"],
            duration_s=2.2, bg=(15, 12, 5),
            neon=(255, 180, 40), text_color=(255, 210, 80)
        )
        print(f"      [{frame_counter} frames]")

        # Shop animated (3.5s)
        print("    → Boutique")
        await capture_animated_screen(page, [
            {"do": "goto", "wait": 1200},
            {"do": "click", "sel": "#btnShop", "wait": 1000},
            {"do": "scroll", "dy": 150, "wait": 800},
            {"do": "click", "sel": "#tabTrails", "wait": 1000},
            {"do": "click", "sel": "#btnCloseShop", "wait": 300},
        ], duration_s=3.5)
        print(f"      [{frame_counter} frames]")

        # ── ACT 4: CHALLENGE ──
        print("\n  🎬 Act 4: Défis")
        print("    → Title: Défis")
        generate_title_frames(
            ["Relève les défis", "chaque jour"],
            duration_s=2.2, bg=(25, 5, 10),
            neon=(255, 60, 80), text_color=(255, 130, 150)
        )
        print(f"      [{frame_counter} frames]")

        # Missions animated (3s)
        print("    → Missions")
        await capture_animated_screen(page, [
            {"do": "goto", "wait": 800},
            {"do": "click", "sel": "#btnMissions", "wait": 1000},
            {"do": "scroll", "dy": 200, "wait": 800},
            {"do": "click", "sel": "#btnCloseMissions", "wait": 400},
        ], duration_s=3.0)
        print(f"      [{frame_counter} frames]")

        # ── ACT 5: INTENSITY ──
        print("\n  🎬 Act 5: Intensité")
        print("    → Title: Jusqu'où")
        generate_title_frames(
            ["Jusqu'où iras-tu ?", ""],
            duration_s=2.0, bg=(8, 8, 28),
            neon=(60, 120, 255), text_color=(130, 180, 255)
        )
        print(f"      [{frame_counter} frames]")

        # Intense gameplay (5s)
        print("    → Gameplay intense")
        await page.goto(GAME_URL, wait_until="networkidle")
        await page.add_style_tag(content='.screen{max-width:92vw!important;width:92vw!important}.ui-layer{padding:0!important}')
        await page.wait_for_timeout(1200)
        await page.click("#btnPlay")
        await page.wait_for_timeout(800)

        await capture_gameplay_frames(page, [
            {"do": "capture_start"},
            {"do": "tap", "x": 215, "y": 600, "wait": 350},
            {"do": "tap", "x": 260, "y": 430, "wait": 300},
            {"do": "tap", "x": 190, "y": 360, "wait": 300},
            {"do": "tap", "x": 310, "y": 400, "wait": 280},
            {"do": "tap", "x": 175, "y": 460, "wait": 280},
            {"do": "tap", "x": 290, "y": 350, "wait": 280},
            {"do": "tap", "x": 210, "y": 420, "wait": 280},
            {"do": "tap", "x": 300, "y": 380, "wait": 280},
            {"do": "tap", "x": 180, "y": 440, "wait": 280},
            {"do": "tap", "x": 270, "y": 370, "wait": 300},
            {"do": "tap", "x": 220, "y": 500, "wait": 350},
            {"do": "wait", "ms": 800},
        ], duration_hint_s=5.0)
        print(f"      [{frame_counter} frames]")

        # ── OUTRO ──
        print("\n  🎬 Outro")
        print("    → Title: Télécharge")
        generate_title_frames(
            ["Télécharge", "gratuitement !"],
            duration_s=3.0, bg=(5, 18, 15),
            neon=(80, 255, 140), text_color=(130, 255, 180),
            show_icon=True
        )
        print(f"      [{frame_counter} frames total]")

        await page.close()
        await browser.close()

    # ────────────────────────────────────
    # ENCODE WITH FFMPEG (single pass)
    # ────────────────────────────────────
    print(f"\n  🔧 Encoding {frame_counter} frames → MP4...")

    output_mp4 = VIDEO_DIR / "swing_snap_preview.mp4"
    result = subprocess.run([
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", str(ALL_FRAMES / "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "medium",
        "-movflags", "+faststart",
        str(output_mp4)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ⚠ Error: {result.stderr[-300:]}")
    else:
        # WebM
        output_webm = VIDEO_DIR / "swing_snap_preview.webm"
        subprocess.run([
            FFMPEG, "-y", "-i", str(output_mp4),
            "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
            str(output_webm)
        ], capture_output=True)

        # Info
        r = subprocess.run([FFMPEG, "-i", str(output_mp4)], capture_output=True, text=True)
        dur = [l for l in r.stderr.split('\n') if 'Duration' in l]
        duration = dur[0].split('Duration:')[1].split(',')[0].strip() if dur else "?"
        size_mb = os.path.getsize(output_mp4) / (1024 * 1024)

        print(f"\n{'='*50}")
        print(f"  ✅ VIDÉO FINALE")
        print(f"  📹 {output_mp4}")
        print(f"  📐 {VW}x{VH} — {FPS}fps — {size_mb:.1f} MB")
        print(f"  ⏱  {duration}")
        print(f"  🎞  {frame_counter} frames (100% identique taille)")
        print(f"{'='*50}")

    # Cleanup
    shutil.rmtree(ALL_FRAMES, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
