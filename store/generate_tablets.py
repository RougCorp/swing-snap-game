#!/usr/bin/env python3
"""Generate tablet screenshots with realistic iPad-style frame.

- 7" tablet: 1200x1920 output, iPad mini style frame
- 10" tablet: 2560x1600 output (LANDSCAPE 16:10), iPad style frame
Game captured at phone viewport where it looks best, shown in tablet frame.
"""

import asyncio
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = Path(__file__).parent
GAME_URL = "http://localhost:8765"

FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

LANG_LOCALES = {
    "fr": "fr-FR", "en": "en-US", "es": "es-ES",
    "de": "de-DE", "it": "it-IT", "pt": "pt-PT",
}

CAPTIONS = {
    "fr": [
        ("Accroche-toi", "et balance-toi !"),
        ("33 balles uniques", "à collectionner"),
        ("33 traînées", "spectaculaires"),
        ("Défis quotidiens", "et progression"),
        ("Gameplay intuitif", "en un seul doigt"),
        ("Enchaîne", "les pivots !"),
        ("Packs et récompenses", "exclusifs"),
        ("Statistiques", "et 12 succès"),
        ("Vise le point vert", "et lâche la corde !"),
        ("Jusqu'où iras-tu ?", ""),
    ],
    "en": [
        ("Hold on", "and swing!"),
        ("33 unique balls", "to collect"),
        ("33 spectacular", "trail effects"),
        ("Daily challenges", "and progression"),
        ("Intuitive gameplay", "one finger only"),
        ("Chain", "the pivots!"),
        ("Exclusive packs", "and rewards"),
        ("Statistics", "and 12 achievements"),
        ("Aim for the green dot", "and release the rope!"),
        ("How far", "will you go?"),
    ],
    "es": [
        ("Agárrate", "¡y balancéate!"),
        ("33 bolas únicas", "por coleccionar"),
        ("33 estelas", "espectaculares"),
        ("Desafíos diarios", "y progresión"),
        ("Jugabilidad intuitiva", "con un solo dedo"),
        ("¡Encadena", "los pivotes!"),
        ("Packs y recompensas", "exclusivos"),
        ("Estadísticas", "y 12 logros"),
        ("Apunta al punto verde", "¡y suelta la cuerda!"),
        ("¿Hasta dónde", "llegarás?"),
    ],
    "de": [
        ("Halte fest", "und schwing dich!"),
        ("33 einzigartige Bälle", "zum Sammeln"),
        ("33 spektakuläre", "Schweif-Effekte"),
        ("Tägliche Herausforderungen", "und Fortschritt"),
        ("Intuitives Gameplay", "mit einem Finger"),
        ("Reihe die Pivots", "aneinander!"),
        ("Exklusive Pakete", "und Belohnungen"),
        ("Statistiken", "und 12 Erfolge"),
        ("Ziele auf den grünen Punkt", "und lass das Seil los!"),
        ("Wie weit", "kommst du?"),
    ],
    "it": [
        ("Aggrappati", "e dondolati!"),
        ("33 palle uniche", "da collezionare"),
        ("33 effetti scia", "spettacolari"),
        ("Sfide giornaliere", "e progressione"),
        ("Gameplay intuitivo", "con un dito"),
        ("Concatena", "i pivot!"),
        ("Pacchetti esclusivi", "e ricompense"),
        ("Statistiche", "e 12 obiettivi"),
        ("Punta al punto verde", "e rilascia la corda!"),
        ("Fin dove", "arriverai?"),
    ],
    "pt": [
        ("Segura firme", "e balança!"),
        ("33 bolas únicas", "para colecionar"),
        ("33 efeitos de rasto", "espetaculares"),
        ("Desafios diários", "e progressão"),
        ("Jogabilidade intuitiva", "com um dedo"),
        ("Encadeia", "os pivots!"),
        ("Packs e recompensas", "exclusivos"),
        ("Estatísticas", "e 12 conquistas"),
        ("Aponta ao ponto verde", "e larga a corda!"),
        ("Até onde", "vais chegar?"),
    ],
}

SCREENS = [
    "menu", "balls", "trails", "missions", "tutorial",
    "gameplay1", "packs", "stats", "gameplay2", "gameplay3",
]

SCREEN_STYLES = [
    ((15, 5, 30), (160, 80, 255), (200, 140, 255)),
    ((10, 10, 25), (255, 180, 40), (255, 210, 80)),
    ((5, 18, 15), (80, 255, 140), (130, 255, 180)),
    ((25, 5, 10), (255, 60, 80), (255, 120, 140)),
    ((5, 10, 30), (40, 200, 255), (100, 220, 255)),
    ((25, 12, 5), (255, 140, 30), (255, 180, 80)),
    ((5, 18, 18), (40, 255, 220), (100, 255, 230)),
    ((20, 5, 25), (255, 60, 200), (255, 130, 220)),
    ((8, 8, 28), (60, 120, 255), (120, 170, 255)),
    ((25, 8, 15), (255, 80, 100), (255, 150, 120)),
]


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed):
    """Arcade neon background."""
    bg_light = tuple(min(255, c + 20) for c in bg_dark)
    for y in range(0, H, 2):
        t = y / H
        c = lerp_color(bg_dark, bg_light, t * 0.5 + 0.1)
        draw.rectangle([(0, y), (W, y + 1)], fill=c)

    # Glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2, H // 2
    glow_r = int(max(W, H) * 0.5)
    for i in range(20, 0, -1):
        r = int(glow_r * i / 20)
        a = int(35 * (1 - i / 20))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*neon_glow, a))
    img_out = Image.alpha_composite(img, glow)

    # Particles
    rng = random.Random(seed)
    for _ in range(25):
        px, py = rng.randint(0, W), rng.randint(0, H)
        pr = rng.randint(1, 3)
        pa = rng.randint(50, 130)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse([px-pr, py-pr, px+pr, py+pr], fill=(255, 255, 255, pa))
        img_out = Image.alpha_composite(img_out, ov)

    return img_out


def draw_neon_text(img, x, y, text, font, text_color, glow_color):
    """Draw text with neon glow."""
    W, H = img.size
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gt = ImageDraw.Draw(glow)
    for dx in range(-3, 4, 2):
        for dy in range(-3, 4, 2):
            if dx*dx + dy*dy <= 9:
                gt.text((x + dx, y + dy), text, fill=(*glow_color, 25), font=font, anchor="mt")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, glow)
    ImageDraw.Draw(img).text((x, y), text, fill=(*text_color, 255), font=font, anchor="mt")
    return img


def draw_tablet_frame(img, raw_screenshot, frame_rect, corner_r, bezel):
    """Draw a realistic iPad-style tablet frame with screenshot inside.

    Thick bezels, prominent aluminum edges, visible camera and home bar
    so it's immediately recognizable as a tablet/iPad.
    """
    draw = ImageDraw.Draw(img)
    fx, fy, fw, fh = frame_rect

    # --- Deep shadow for 3D pop ---
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(30, 0, -1):
        a = int(2 + i * 2.5)
        sd.rounded_rectangle(
            (fx - i + 5, fy + i + 2, fx + fw + i + 5, fy + fh + i + 8),
            radius=corner_r + i, fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # --- Aluminum body (3-layer edge like real iPad) ---
    edge = max(6, int(fw * 0.012))
    # Outer edge (dark aluminum)
    draw.rounded_rectangle(
        (fx - edge, fy - edge, fx + fw + edge, fy + fh + edge),
        radius=corner_r + edge, fill=(145, 145, 150))
    # Mid edge (brushed aluminum highlight)
    draw.rounded_rectangle(
        (fx - edge + 2, fy - edge + 2, fx + fw + edge - 2, fy + fh + edge - 2),
        radius=corner_r + edge - 2, fill=(190, 190, 195))
    # Inner edge (lighter)
    draw.rounded_rectangle(
        (fx - 2, fy - 2, fx + fw + 2, fy + fh + 2),
        radius=corner_r + 2, fill=(210, 210, 215))
    # Body (black face)
    draw.rounded_rectangle(
        (fx, fy, fx + fw, fy + fh),
        radius=corner_r, fill=(20, 20, 22))

    # --- Thick bezels (iPad-like proportions) ---
    sx = fx + bezel
    sy = fy + bezel
    sw = fw - bezel * 2
    sh = fh - bezel * 2
    sr = max(2, corner_r - bezel)

    # Fill screen with game background color first, then fit screenshot centered
    GAME_BG = (245, 240, 232)  # #F5F0E8
    screen_bg = Image.new("RGBA", (sw, sh), (*GAME_BG, 255))

    # Fit screenshot: scale to fill WIDTH, then center vertically
    scale_factor = sw / raw_screenshot.width
    new_w = sw
    new_h = int(raw_screenshot.height * scale_factor)
    resized = raw_screenshot.resize((new_w, new_h), Image.LANCZOS)

    paste_y = (sh - new_h) // 2
    screen_bg.paste(resized, (0, paste_y))

    # Rounded mask for screen
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=sr, fill=255)
    img.paste(screen_bg, (sx, sy), mask)

    draw = ImageDraw.Draw(img)

    # --- Camera (top center, prominent) ---
    cam_r = max(4, int(fw * 0.008))
    cam_x = fx + fw // 2
    cam_y = fy + bezel // 2
    # Camera housing (dark ring)
    draw.ellipse([cam_x - cam_r - 2, cam_y - cam_r - 2,
                  cam_x + cam_r + 2, cam_y + cam_r + 2], fill=(40, 40, 44))
    # Camera lens
    draw.ellipse([cam_x - cam_r, cam_y - cam_r,
                  cam_x + cam_r, cam_y + cam_r], fill=(25, 25, 30))
    # Lens highlight
    hr = max(1, cam_r // 3)
    draw.ellipse([cam_x - hr - 1, cam_y - hr - 1,
                  cam_x + hr, cam_y + hr], fill=(55, 55, 65))

    # --- Home bar (bottom, iPad-style indicator) ---
    bar_w = int(sw * 0.32)
    bar_h = max(4, int(fh * 0.004))
    bar_x = fx + (fw - bar_w) // 2
    bar_y = fy + fh - bezel // 2 - bar_h // 2
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=bar_h // 2, fill=(90, 90, 95))

    # --- Side buttons (right edge: volume up/down + power) ---
    btn_w = max(3, int(edge * 0.6))
    btn_color = (160, 160, 165)
    # Power button (right side, near top)
    pwr_h = int(fh * 0.035)
    pwr_y = fy + int(fh * 0.08)
    draw.rounded_rectangle(
        (fx + fw + edge - 1, pwr_y, fx + fw + edge - 1 + btn_w, pwr_y + pwr_h),
        radius=btn_w // 2, fill=btn_color)
    # Volume up
    vol_h = int(fh * 0.04)
    vol_y1 = fy + int(fh * 0.18)
    draw.rounded_rectangle(
        (fx - edge + 1 - btn_w, vol_y1, fx - edge + 1, vol_y1 + vol_h),
        radius=btn_w // 2, fill=btn_color)
    # Volume down
    vol_y2 = vol_y1 + vol_h + int(fh * 0.015)
    draw.rounded_rectangle(
        (fx - edge + 1 - btn_w, vol_y2, fx - edge + 1, vol_y2 + vol_h),
        radius=btn_w // 2, fill=btn_color)

    return img


def compose_tablet_7(raw_img, caption, style, idx):
    """7-inch tablet: 1200x1920 PORTRAIT (9:16)."""
    W, H = 1200, 1920
    bg_dark, neon_glow, neon_text = style

    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    draw = ImageDraw.Draw(img)
    img = draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed=idx * 17 + 3)

    # Text
    try:
        ft = ImageFont.truetype(FONT_PATH, 56, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 38, index=FONT_DEMI_IDX)
    except:
        ft = fs = ImageFont.load_default()

    top, bottom = caption
    img = draw_neon_text(img, W // 2, int(H * 0.025), top, ft, neon_text, neon_glow)
    if bottom:
        img = draw_neon_text(img, W // 2, int(H * 0.07), bottom, fs, (255, 255, 255), neon_glow)

    # Tablet frame — iPad mini proportions (compact, clearly tablet-shaped)
    fw = int(W * 0.55)
    fh = int(H * 0.60)
    fx = (W - fw) // 2
    fy = int(H * 0.18)
    corner_r = int(fw * 0.055)
    bezel = int(fw * 0.045)

    img = draw_tablet_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)

    return img


def compose_tablet_10(raw_img, caption, style, idx):
    """10-inch tablet: 1600x2560 PORTRAIT (10:16)."""
    W, H = 1600, 2560
    bg_dark, neon_glow, neon_text = style

    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    draw = ImageDraw.Draw(img)
    img = draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed=idx * 23 + 7)

    # Text
    try:
        ft = ImageFont.truetype(FONT_PATH, 72, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 48, index=FONT_DEMI_IDX)
    except:
        ft = fs = ImageFont.load_default()

    top, bottom = caption
    img = draw_neon_text(img, W // 2, int(H * 0.022), top, ft, neon_text, neon_glow)
    if bottom:
        img = draw_neon_text(img, W // 2, int(H * 0.06), bottom, fs, (255, 255, 255), neon_glow)

    # Tablet frame — iPad 10" proportions (bigger than 7" to show difference)
    fw = int(W * 0.65)
    fh = int(H * 0.68)
    fx = (W - fw) // 2
    fy = int(H * 0.13)
    corner_r = int(fw * 0.05)
    bezel = int(fw * 0.04)

    img = draw_tablet_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)

    return img


FULLSCREEN_CSS = """
    .screen { max-width: 92vw !important; width: 92vw !important; }
    .ui-layer { padding: 0 !important; }
    #scoreDisplay { font-size: 3rem !important; }
"""

async def goto_and_inject(page, url):
    await page.goto(url, wait_until="networkidle")
    await page.add_style_tag(content=FULLSCREEN_CSS)
    await page.wait_for_timeout(500)

async def capture_phone_screens(browser, lang, locale):
    """Capture raw phone screens (where game looks best)."""
    raw_dir = OUT_DIR / "raw" / lang
    existing = sorted(raw_dir.glob("*.png")) if raw_dir.exists() else []
    if len(existing) >= 10:
        print(f"    → Reusing {len(existing)} raw captures")
        return [str(f) for f in existing[:10]]

    raw_dir.mkdir(parents=True, exist_ok=True)
    page = await browser.new_page(
        viewport={"width": 430, "height": 932},
        device_scale_factor=3, locale=locale)
    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    raw = []
    steps = [
        (None, "01_menu"),
        ("#btnShop", "02_balls"),
        ("#tabTrails", "03_trails"),
        ("#btnCloseShop|#btnMissions", "04_missions"),
        ("#btnCloseMissions|#btnPlay", "05_tutorial"),
    ]
    for sel, name in steps:
        if sel:
            for s in sel.split("|"):
                await page.click(s)
                await page.wait_for_timeout(300)
        await page.wait_for_timeout(500)
        p = str(raw_dir / f"{name}.png")
        await page.screenshot(path=p)
        raw.append(p)

    # Gameplay 1
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(400)
    p = str(raw_dir / "06_gameplay1.png")
    await page.screenshot(path=p)
    raw.append(p)

    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    await page.click("#btnIAP")
    await page.wait_for_timeout(500)
    p = str(raw_dir / "07_packs.png")
    await page.screenshot(path=p)
    raw.append(p)

    await page.click("#btnCloseIAP")
    await page.wait_for_timeout(300)
    await page.click("#btnStats")
    await page.wait_for_timeout(500)
    p = str(raw_dir / "08_stats.png")
    await page.screenshot(path=p)
    raw.append(p)

    await page.click("#btnCloseStats")
    await page.wait_for_timeout(300)
    await page.click("#btnPlay")
    await page.wait_for_timeout(600)
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(600)
    await page.mouse.click(300, 400)
    await page.wait_for_timeout(400)
    p = str(raw_dir / "09_gameplay2.png")
    await page.screenshot(path=p)
    raw.append(p)

    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(1500)
    await page.click("#btnPlay")
    await page.wait_for_timeout(600)
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(300)
    await page.mouse.click(200, 500)
    await page.wait_for_timeout(300)
    await page.mouse.click(250, 400)
    await page.wait_for_timeout(500)
    p = str(raw_dir / "10_gameplay3.png")
    await page.screenshot(path=p)
    raw.append(p)

    await page.close()
    return raw


async def main():
    print("=== Swing & Snap — Tablet Screenshots v2 ===\n")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for lang, locale in LANG_LOCALES.items():
            print(f"━━━ {lang.upper()} ━━━")
            raw_files = await capture_phone_screens(browser, lang, locale)
            captions = CAPTIONS[lang]

            # 7" tablet
            dir7 = OUT_DIR / "tablet-7" / lang
            dir7.mkdir(parents=True, exist_ok=True)
            print(f"  7-inch (1200x1920):")
            for i, (raw_path, caption) in enumerate(zip(raw_files, captions)):
                raw_img = Image.open(raw_path).convert("RGBA")
                out = compose_tablet_7(raw_img, caption, SCREEN_STYLES[i], i)
                name = SCREENS[i]
                path = dir7 / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
                out.save(str(path), "PNG", optimize=True)
                print(f"    ✓ {path.name}")

            # 10" tablet
            dir10 = OUT_DIR / "tablet-10" / lang
            dir10.mkdir(parents=True, exist_ok=True)
            print(f"  10-inch (1600x2560):")
            for i, (raw_path, caption) in enumerate(zip(raw_files, captions)):
                raw_img = Image.open(raw_path).convert("RGBA")
                out = compose_tablet_10(raw_img, caption, SCREEN_STYLES[i], i)
                name = SCREENS[i]
                path = dir10 / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
                out.save(str(path), "PNG", optimize=True)
                print(f"    ✓ {path.name}")

        await browser.close()

    print(f"\n✅ Tablet screenshots generated!")
    print(f"  📁 tablet-7/  → 1200x1920 (iPad mini style)")
    print(f"  📁 tablet-10/ → 1600x2560 (iPad 10\" style)")


if __name__ == "__main__":
    asyncio.run(main())
