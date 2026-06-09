#!/usr/bin/env python3
"""Generate Google Ads video — portrait 9:16 (1080x1920) + landscape 16:9 (1920x1080).

v7 — ~22s pivot-chain cut (max 30s):
  1. Hook gameplay    5s   — shows mechanic from first swing
  2. Title card       2s   — SWING & SNAP branding
  3. Pivot chain      10s  — fresh run, records after first snap → 4-5 pivots visible
  4. Shop             2.5s — 100+ items feature
  5. CTA outro        2.5s — Download free
  Total: ~22s @ 24fps

- raf_scale = (cap_fps/24) × 1.5 → game 1.5× faster in video (more snaps/sec visible)
- bot reads Game.player.vel + pivots, jumps at dot>0.82, never dies
- screenshots → raw bytes, no PIL resize (viewport 540×960 × scale=2 = 1080×1920 exact)
"""

import asyncio
import io
import math
import random
import time
import subprocess
import shutil
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).parent.parent
OUT_DIR = Path(__file__).parent
VIDEO_DIR = OUT_DIR / "video"
ALL_FRAMES = VIDEO_DIR / "ad_frames"

GAME_URL = "http://localhost:9876"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
MUSIC = str(BASE / "www/assets/music/cosmique.mp3")

FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

VP_W, VP_H   = 540, 960          # CSS viewport
DEVICE_SCALE = 2
VW, VH       = VP_W*DEVICE_SCALE, VP_H*DEVICE_SCALE  # 1080 × 1920
FPS          = 24

# ── RAF override: game speed = window.__rafScale × real speed ─────────────────
# __rafScale is set dynamically after calibration: capture_fps / 24
# → each captured frame advances exactly 1/24s of game time
RAF_FIX_SCRIPT = """
(function() {
    const _origRAF = window.requestAnimationFrame.bind(window);
    window.__rafScale = 1.0;   // overridden from Python after calibration
    let _sim = 0, _started = false;
    window.requestAnimationFrame = function(cb) {
        return _origRAF(function(real) {
            if (!_started) { _sim = real; _started = true; }
            _sim += 16.667 * window.__rafScale;
            cb(_sim);
        });
    };
})();
"""

# ── Auto-play bot v8 — geometrically correct ──────────────────────────────────
# Game physics (from source):
#   on rope : vel.x = -sin(angle)*spd*ropeLen,  vel.y = cos(angle)*spd*ropeLen
#   in flight: pos += vel*dt  (NO gravity — pure linear trajectory)
#   snap fires when dist(player, pivot) < snapRadius (90)
#   handleJump: shifts pivots[], releases rope, vel *= 1.25
#
# Old bot used dot>0.82 which requires dist<157 to guarantee snap — but minimum
# pivot distance is 220, so it almost always missed. Fix: check perpendicular
# distance from the straight-line trajectory to the target pivot directly.
#   perp = dist * sqrt(1 - dot²)   (closest approach distance)
# Jump when perp < snapRadius AND moving toward target (dot > 0).
BOT_SCRIPT = """
(function() {
    if (window._swingBot) clearInterval(window._swingBot);
    let jumpCooldown = 0;
    let restartAt    = 0;
    const SNAP_R     = 82;   // slightly under snapRadius=90 for safety margin

    window._swingBot = setInterval(function() {
        if (typeof Game === 'undefined') return;
        const G = Game, now = Date.now();

        if (G.state === 'GAMEOVER') {
            if (now >= restartAt) {
                G.mode = 'arcade';
                G.startRun();
                restartAt    = now + 1200;
                jumpCooldown = now + 1500;
            }
            return;
        }
        if (G.state === 'TUTORIAL') {
            const el = document.getElementById('tutorialOverlay');
            if (el) el.click();
            jumpCooldown = now + 1000;
            return;
        }
        if (G.state !== 'PLAYING') return;

        const pl = G.player;
        if (!pl || !pl.rope) return;      // in flight — wait to land
        if (now < jumpCooldown)  return;

        const target = G.pivots.find(function(p) { return p.isTarget; });
        if (!target) return;

        const vel  = pl.vel;
        const vLen = Math.sqrt(vel.x*vel.x + vel.y*vel.y);
        if (vLen < 0.01) return;

        const dx   = target.pos.x - pl.pos.x;
        const dy   = target.pos.y - pl.pos.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 5) return;

        // dot: cosine of angle between velocity and direction-to-target
        const dot  = (vel.x/vLen)*(dx/dist) + (vel.y/vLen)*(dy/dist);

        // perp: closest approach of straight-line trajectory to target
        //   perp = dist * sin(angle) = dist * sqrt(1 - dot²)
        const perp = dist * Math.sqrt(Math.max(0, 1 - dot*dot));

        if (dot > 0.1 && perp < SNAP_R) {
            G.handleJump();
            jumpCooldown = now + 350;
        }
    }, 16);

    console.log('[SwingBot v8] active — perp-distance check');
})();
"""

frame_counter = 0


# ── Frame helpers ──────────────────────────────────────────────────────────────

def next_frame_path():
    global frame_counter
    p = ALL_FRAMES / f"frame_{frame_counter:05d}.png"
    frame_counter += 1
    return p


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def save_frame(img):
    img.convert("RGB").save(str(next_frame_path()), "PNG")


# ── Title card ─────────────────────────────────────────────────────────────────

def generate_title_card(lines, duration_s=2.5, bg=(12, 5, 25),
                        neon=(160, 80, 255), text_color=(220, 170, 255),
                        show_icon=False, subtitle_size=44):
    n_frames = int(duration_s * FPS)
    try:
        font_big = ImageFont.truetype(FONT_PATH, 78, index=FONT_HEAVY_IDX)
        font_med = ImageFont.truetype(FONT_PATH, subtitle_size, index=FONT_DEMI_IDX)
    except Exception:
        font_big = ImageFont.load_default(); font_med = font_big

    icon = None
    if show_icon:
        ip = BASE / "www/web-app-manifest-512x512.png"
        if ip.exists():
            icon = Image.open(ip).convert("RGBA").resize((180, 180), Image.LANCZOS)
            mask = Image.new("L", (180, 180), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 180, 180), radius=40, fill=255)
            icon.putalpha(mask)

    rng = random.Random(hash(str(lines)))
    particles = [(rng.randint(0, VW), rng.randint(0, VH),
                  rng.randint(1, 3), rng.randint(1, 5), rng.randint(40, 130))
                 for _ in range(35)]

    for f in range(n_frames):
        progress = f / n_frames
        img = Image.new("RGBA", (VW, VH), (*bg, 255))
        draw = ImageDraw.Draw(img)
        bg_light = tuple(min(255, c + 25) for c in bg)
        for y in range(0, VH, 2):
            c = lerp_color(bg, bg_light, (y / VH) * 0.5)
            draw.rectangle([(0, y), (VW, y + 1)], fill=c)

        pulse = 0.85 + 0.15 * math.sin(progress * math.pi * 3)
        glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        glow_r = int(VW * 0.65 * pulse)
        for i in range(18, 0, -1):
            r = int(glow_r * i / 18)
            a = int(45 * (1 - i / 18) * pulse)
            gd.ellipse([VW//2-r, VH//2-r, VW//2+r, VH//2+r], fill=(*neon, a))
        img = Image.alpha_composite(img, glow)

        p_ov = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        pd = ImageDraw.Draw(p_ov)
        for px, py, pr, speed, alpha in particles:
            apy = (py - int(f * speed * 1.8)) % VH
            pd.ellipse([px-pr, apy-pr, px+pr, apy+pr], fill=(255, 255, 255, alpha))
        img = Image.alpha_composite(img, p_ov)

        opacity = (progress / 0.12 if progress < 0.12 else
                   (1.0 - progress) / 0.12 if progress > 0.88 else 1.0)

        content_y = VH // 2 - 60
        if icon and show_icon:
            content_y = VH // 2
            ic = icon.copy()
            ic.putalpha(Image.eval(ic.getchannel('A'), lambda a: int(a * opacity)))
            img.paste(ic, (VW//2 - 90, VH//2 - 220), ic)

        for i, line in enumerate(lines):
            if not line: continue
            font = font_big if i == 0 else font_med
            color = text_color if i == 0 else (255, 255, 255)
            line_y = content_y + i * 95
            delay = max(0, (progress - i * 0.06)) / 0.15
            line_op = min(1.0, delay) * opacity
            line_off = int(25 * (1 - min(1.0, delay)))
            if line_op > 0:
                glow_txt = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                gt = ImageDraw.Draw(glow_txt)
                for dx in range(-4, 5, 2):
                    for dy in range(-4, 5, 2):
                        if dx*dx + dy*dy <= 16:
                            gt.text((VW//2+dx, line_y+line_off+dy), line,
                                    fill=(*neon, int(25*line_op*pulse)),
                                    font=font, anchor="mt")
                glow_txt = glow_txt.filter(ImageFilter.GaussianBlur(radius=3))
                img = Image.alpha_composite(img, glow_txt)
                ImageDraw.Draw(img).text((VW//2, line_y+line_off), line,
                    fill=(*color, int(255*line_op)), font=font, anchor="mt")
        save_frame(img)


# ── Game helpers ───────────────────────────────────────────────────────────────

async def go_to_game(page):
    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(1500)


async def set_raf_scale(page, scale):
    """Set the RAF time-scale so game speed matches capture rate."""
    await page.evaluate(f"window.__rafScale = {scale:.5f}")


async def inject_bot(page):
    await page.evaluate(BOT_SCRIPT)


async def calibrate_fps(page, n=15):
    """Measure actual screenshot fps using raw bytes (no PIL, no disk I/O)."""
    t0 = time.time()
    for _ in range(n):
        await page.screenshot()   # returns bytes, we discard them
    fps = n / (time.time() - t0)
    ms  = 1000 / fps
    print(f"    [calibrate] {fps:.1f} fps  ({ms:.0f}ms/shot)")
    return fps


async def launch_game(page):
    """Call Game.startRun() directly — skips menu, no button click needed."""
    await page.evaluate("if(typeof Game!=='undefined'){Game.mode='arcade';Game.startRun();}")
    await page.wait_for_timeout(200)


async def start_fresh_run(page, raf_scale):
    """Navigate, set RAF scale, inject bot, start game.
    Wait only ~1.5s — just enough for the bot to dismiss the tutorial.
    Recording starts from the very first swing so we see the full mechanic.
    """
    await go_to_game(page)
    await set_raf_scale(page, raf_scale)
    await inject_bot(page)
    await launch_game(page)
    await page.wait_for_timeout(1500)   # tutorial dismiss only — record from first swing


async def capture_gameplay(page, n_frames):
    """
    Capture exactly n_frames screenshots → saved directly as PNG frames.
    No PIL involved → fastest possible path.
    """
    t0 = time.time()
    for _ in range(n_frames):
        raw = await page.screenshot()   # bytes of a valid 1080×1920 PNG
        with open(str(next_frame_path()), 'wb') as fh:
            fh.write(raw)
    elapsed = time.time() - t0
    print(f"    {n_frames} frames in {elapsed:.1f}s  ({n_frames/elapsed:.1f}fps capture)")


async def wait_until_scoring(page, min_score=1, timeout_s=10):
    """Block until Game.score >= min_score (first snap done) → recording starts in-rhythm."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        score = await page.evaluate(
            "(typeof Game!=='undefined' && typeof Game.score!=='undefined') ? Game.score : -1"
        )
        if score >= min_score:
            return
        await page.wait_for_timeout(150)


async def capture_static(page, hold_s):
    """Single screenshot held for hold_s seconds."""
    raw = await page.screenshot()
    n   = int(hold_s * FPS)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if img.size != (VW, VH):
        img = img.resize((VW, VH), Image.BILINEAR)
    for _ in range(n):
        save_frame(img.copy())


def frames(seconds):
    """Convert video seconds → integer frame count."""
    return int(seconds * FPS)


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    global frame_counter
    frame_counter = 0

    print("=== Swing & Snap — Google Ads Video (v7 — 20s pivot chain) ===")
    print(f"    Output: {VW}×{VH} @ {FPS}fps\n")

    if ALL_FRAMES.exists():
        shutil.rmtree(ALL_FRAMES)
    ALL_FRAMES.mkdir(parents=True)

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": VP_W, "height": VP_H},
            device_scale_factor=DEVICE_SCALE,
            locale="en-US",
        )
        await page.add_init_script(RAF_FIX_SCRIPT)

        # ── Calibrate screenshot fps ──────────────────────────────────────────
        await go_to_game(page)
        cap_fps   = await calibrate_fps(page)
        raf_scale = cap_fps / FPS   # real-time: each captured frame = exactly 1/24s game time
        print(f"    RAF scale → {raf_scale:.3f}  (real-time game speed)\n")

        # ─────────────────────────────────────────────────────────────────────
        # (1) HOOK — 5s gameplay from first swing  [120 frames]
        # ─────────────────────────────────────────────────────────────────────
        print("🎬 1. Hook gameplay (5s)")
        await set_raf_scale(page, raf_scale)
        await inject_bot(page)
        await launch_game(page)
        await page.wait_for_timeout(1500)   # let bot dismiss tutorial + start first swing
        await capture_gameplay(page, frames(5.0))
        print(f"    → {frame_counter} frames")

        # ─────────────────────────────────────────────────────────────────────
        # (2) TITLE CARD — 2s  [48 frames]
        # ─────────────────────────────────────────────────────────────────────
        print("🎬 2. Title: SWING & SNAP (2s)")
        generate_title_card(
            ["SWING & SNAP", "The one-finger swing game"],
            duration_s=2.0, bg=(10, 4, 22),
            neon=(142, 99, 180), text_color=(210, 165, 255),
            show_icon=True, subtitle_size=40,
        )
        print(f"    → {frame_counter} frames")

        # ─────────────────────────────────────────────────────────────────────
        # (3) PIVOT CHAIN — 12s continuous gameplay  [288 frames]
        # Start recording only AFTER bot lands first snap (score>=1) so we
        # always start mid-chain: 4-5 clean pivot snaps visible.
        # ─────────────────────────────────────────────────────────────────────
        print("🎬 3. Pivot chain: 12s continuous gameplay")
        await start_fresh_run(page, raf_scale)
        await wait_until_scoring(page, min_score=1)   # guarantees chain is underway
        await capture_gameplay(page, frames(12.0))
        print(f"    → {frame_counter} frames")

        # ─────────────────────────────────────────────────────────────────────
        # (4) SHOP — 1s card + 1.5s screen  [60 frames]
        # ─────────────────────────────────────────────────────────────────────
        print("🎬 4. Shop: 100+ Items (2.5s)")
        generate_title_card(
            ["100+ ITEMS", "Unlock balls, trails & more"],
            duration_s=1.0, bg=(18, 14, 5),
            neon=(255, 180, 40), text_color=(255, 215, 90),
            subtitle_size=40,
        )
        await go_to_game(page)
        try:
            await page.click("#btnShop")
            await page.wait_for_timeout(700)
            await capture_static(page, hold_s=1.5)
        except Exception as e:
            print(f"    (shop fallback: {e})")
            await capture_static(page, hold_s=1.5)
        print(f"    → {frame_counter} frames")

        # ─────────────────────────────────────────────────────────────────────
        # (5) OUTRO CTA — 2.5s  [60 frames]
        # ─────────────────────────────────────────────────────────────────────
        print("🎬 5. Outro: Download free (2.5s)")
        generate_title_card(
            ["SWING & SNAP", "Free — Download now!"],
            duration_s=2.5, bg=(5, 18, 14),
            neon=(80, 255, 140), text_color=(130, 255, 185),
            show_icon=True, subtitle_size=40,
        )
        print(f"\n    Grand total: {frame_counter} frames  ({frame_counter/FPS:.1f}s)")
        await browser.close()

    total_dur = frame_counter / FPS
    print(f"\n📹 {frame_counter} frames = {total_dur:.1f}s")

    # ── Encode portrait 1080×1920 ──────────────────────────────────────────────
    print("\n🔧 Encoding portrait 9:16 …")
    out_p = VIDEO_DIR / "swing_snap_ads_portrait.mp4"
    r = subprocess.run([
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", str(ALL_FRAMES / "frame_%05d.png"),
        "-i", MUSIC,
        "-filter_complex",
        f"[1:a]afade=t=in:st=0:d=1.5,afade=t=out:st={total_dur-2}:d=2[outa]",
        "-map", "0:v", "-map", "[outa]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        str(out_p),
    ], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  ✅ {out_p.name}  ({os.path.getsize(out_p)/1024/1024:.1f} MB)")
    else:
        print(f"  ❌ {r.stderr[-600:]}")

    # ── Encode landscape 1920×1080 ─────────────────────────────────────────────
    print("🔧 Encoding landscape 16:9 …")
    out_l = VIDEO_DIR / "swing_snap_ads_landscape.mp4"
    r = subprocess.run([
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", str(ALL_FRAMES / "frame_%05d.png"),
        "-i", MUSIC,
        "-filter_complex",
        (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,boxblur=25:8[bg];"
            f"[0:v]scale=-2:1080[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[outv];"
            f"[1:a]afade=t=in:st=0:d=1.5,afade=t=out:st={total_dur-2}:d=2[outa]"
        ),
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        str(out_l),
    ], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  ✅ {out_l.name}  ({os.path.getsize(out_l)/1024/1024:.1f} MB)")
    else:
        print(f"  ❌ {r.stderr[-600:]}")

    shutil.rmtree(ALL_FRAMES, ignore_errors=True)
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
