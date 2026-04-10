#!/usr/bin/env python3
"""Generate store screenshots for Swing & Snap — Arcade Design + iPhone 15 Pro."""

import asyncio
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- CONFIG ---
W, H = 1290, 2796
OUT_DIR = Path(__file__).parent
GAME_URL = "http://localhost:8765"

FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

# --- CAPTIONS ---
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

# Arcade style: dark backgrounds with neon accent colors
# (bg_dark, bg_mid, neon_glow, neon_text)
SCREEN_STYLES = [
    # 01 Menu — Dark purple + neon violet
    ((15, 5, 30), (40, 15, 70), (160, 80, 255), (200, 140, 255)),
    # 02 Balls — Dark blue + neon gold
    ((10, 10, 25), (25, 25, 55), (255, 180, 40), (255, 210, 80)),
    # 03 Trails — Dark teal + neon green
    ((5, 18, 15), (15, 40, 35), (80, 255, 140), (130, 255, 180)),
    # 04 Missions — Dark red + neon red/pink
    ((25, 5, 10), (55, 12, 20), (255, 60, 80), (255, 120, 140)),
    # 05 Tutorial — Dark navy + neon cyan
    ((5, 10, 30), (15, 25, 60), (40, 200, 255), (100, 220, 255)),
    # 06 Gameplay 1 — Dark orange + neon orange
    ((25, 10, 5), (55, 25, 10), (255, 140, 30), (255, 180, 80)),
    # 07 Packs — Dark emerald + neon teal
    ((5, 18, 18), (12, 40, 40), (40, 255, 220), (100, 255, 230)),
    # 08 Stats — Dark magenta + neon pink
    ((20, 5, 25), (45, 12, 55), (255, 60, 200), (255, 130, 220)),
    # 09 Gameplay 2 — Dark blue + neon blue
    ((8, 8, 28), (20, 20, 60), (60, 120, 255), (120, 170, 255)),
    # 10 Gameplay 3 — Dark sunset + neon warm
    ((25, 8, 15), (55, 18, 30), (255, 80, 100), (255, 150, 120)),
]

SCREENS = [
    "menu", "balls", "trails", "missions", "tutorial",
    "gameplay1", "packs", "stats", "gameplay2", "gameplay3",
]

LANG_LOCALES = {
    "fr": "fr-FR", "en": "en-US", "es": "es-ES",
    "de": "de-DE", "it": "it-IT", "pt": "pt-PT",
}


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * max(0, min(1, t))) for i in range(len(c1)))


def draw_radial_gradient(img, cx, cy, radius, center_color, edge_color):
    """Draw a radial gradient on the image."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    steps = 60
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        c = lerp_color(edge_color, center_color, 1 - t)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_arcade_bg(img, bg_dark, bg_mid, neon_glow, seed):
    """Dark arcade background with neon glow, particles, speed lines."""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed)

    # Base: vertical dark gradient
    for y in range(h):
        t = y / h
        c = lerp_color(bg_dark, bg_mid, t * 0.6 + 0.2)
        draw.line([(0, y), (w, y)], fill=c)

    # Large neon glow in center (behind phone area)
    img = draw_radial_gradient(img, w // 2, int(h * 0.50), int(w * 1.1),
                               (*neon_glow, 50), (*bg_dark, 0))

    # Secondary glow top
    img = draw_radial_gradient(img, w // 2, int(h * 0.08), int(w * 0.6),
                               (*neon_glow, 30), (*bg_dark, 0))

    draw = ImageDraw.Draw(img)

    # Tiny stars / particles
    for _ in range(60):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        r = rng.randint(1, 4)
        a = rng.randint(60, 180)
        star_c = lerp_color((255, 255, 255), neon_glow, rng.random() * 0.4)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([x - r, y - r, x + r, y + r], fill=(*star_c, a))
        img = Image.alpha_composite(img, overlay)

    # Speed lines (diagonal, subtle)
    draw = ImageDraw.Draw(img)
    for _ in range(8):
        x1 = rng.randint(-100, w + 100)
        y1 = rng.randint(0, h)
        length = rng.randint(100, 350)
        angle = rng.uniform(-0.3, 0.3)  # Near-vertical
        x2 = x1 + int(length * math.sin(angle))
        y2 = y1 - int(length * math.cos(angle))
        a = rng.randint(15, 40)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.line([(x1, y1), (x2, y2)], fill=(*neon_glow, a), width=rng.randint(2, 5))
        img = Image.alpha_composite(img, overlay)

    # Neon rings (arcade energy)
    for _ in range(4):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(50, h - 50)
        r = rng.randint(30, 120)
        a = rng.randint(20, 50)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*neon_glow, a), width=2)
        img = Image.alpha_composite(img, overlay)

    return img


def get_fonts():
    try:
        title = ImageFont.truetype(FONT_PATH, 96, index=FONT_HEAVY_IDX)
        sub = ImageFont.truetype(FONT_PATH, 70, index=FONT_DEMI_IDX)
        return title, sub
    except Exception:
        title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 96)
        sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 70)
        return title, sub


def draw_neon_text(img, pos, text, font, color, glow_color):
    """Draw text with neon glow effect."""
    # Create glow layer
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    # Draw glow text (multiple passes, blurred)
    for spread in [6, 4, 2]:
        for dx in range(-spread, spread + 1, 2):
            for dy in range(-spread, spread + 1, 2):
                if dx * dx + dy * dy <= spread * spread:
                    gd.text((pos[0] + dx, pos[1] + dy), text,
                            fill=(*glow_color, 30), font=font, anchor="mt")

    # Blur the glow
    glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, glow)

    # Main text (bright white/color)
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, fill=(*color, 255), font=font, anchor="mt")

    return img


def draw_iphone_frame(img, raw_screenshot, px, py, pw, ph):
    """Draw a realistic iPhone 15 Pro frame and paste the screenshot."""
    draw = ImageDraw.Draw(img)

    # iPhone 15 Pro proportions
    corner_r = int(pw * 0.13)  # Large corner radius like real iPhone
    bezel = int(pw * 0.018)    # Ultra-thin bezels

    # --- Outer frame shadow (soft, deep) ---
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(25, 0, -1):
        a = int(3 + i * 2.5)
        sd.rounded_rectangle(
            (px - i + 4, py + i, px + pw + i + 4, py + ph + i + 8),
            radius=corner_r + i, fill=(0, 0, 0, a)
        )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # --- Titanium frame (3 layers for realism) ---
    # Outer titanium
    draw.rounded_rectangle(
        (px - 5, py - 5, px + pw + 5, py + ph + 5),
        radius=corner_r + 5, fill=(120, 120, 125)
    )
    # Mid titanium (slightly lighter for bevel)
    draw.rounded_rectangle(
        (px - 3, py - 3, px + pw + 3, py + ph + 3),
        radius=corner_r + 3, fill=(145, 145, 150)
    )
    # Inner titanium edge
    draw.rounded_rectangle(
        (px - 1, py - 1, px + pw + 1, py + ph + 1),
        radius=corner_r + 1, fill=(130, 130, 135)
    )

    # --- Phone body (jet black) ---
    draw.rounded_rectangle(
        (px, py, px + pw, py + ph),
        radius=corner_r, fill=(10, 10, 10)
    )

    # --- Screen area ---
    scr_x = px + bezel
    scr_y = py + bezel
    scr_w = pw - bezel * 2
    scr_h = ph - bezel * 2
    scr_r = corner_r - bezel

    # Resize & paste screenshot with rounded corners
    screen = raw_screenshot.resize((scr_w, scr_h), Image.LANCZOS)
    mask = Image.new("L", (scr_w, scr_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, scr_w, scr_h), radius=scr_r, fill=255)
    img.paste(screen, (scr_x, scr_y), mask)

    # --- Dynamic Island ---
    di_w = int(pw * 0.27)
    di_h = int(pw * 0.058)
    di_x = px + (pw - di_w) // 2
    di_y = py + bezel + int(pw * 0.025)
    di_r = di_h // 2

    # Dynamic Island with subtle inner shadow
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (di_x, di_y, di_x + di_w, di_y + di_h),
        radius=di_r, fill=(0, 0, 0)
    )
    # Camera lens dot (left side of island)
    lens_r = int(di_h * 0.22)
    lens_x = di_x + int(di_w * 0.28)
    lens_y = di_y + di_h // 2
    draw.ellipse([lens_x - lens_r, lens_y - lens_r, lens_x + lens_r, lens_y + lens_r],
                 fill=(15, 15, 20))

    # --- Side buttons ---
    btn_color = (110, 110, 115)

    # Power button (right)
    pb_w = 4
    pb_h = int(ph * 0.065)
    pb_y = py + int(ph * 0.23)
    draw.rounded_rectangle(
        (px + pw + 2, pb_y, px + pw + 2 + pb_w, pb_y + pb_h),
        radius=2, fill=btn_color
    )

    # Volume buttons (left)
    for vy in [int(ph * 0.20), int(ph * 0.27)]:
        draw.rounded_rectangle(
            (px - 2 - pb_w, py + vy, px - 2, py + vy + int(ph * 0.048)),
            radius=2, fill=btn_color
        )

    # Silent switch (left, higher, smaller)
    draw.rounded_rectangle(
        (px - 2 - pb_w, py + int(ph * 0.14), px - 2, py + int(ph * 0.165)),
        radius=2, fill=btn_color
    )

    return img


def compose_store_screenshot(raw_img, caption, style, screen_idx):
    """Compose arcade-style store screenshot with iPhone 15 Pro frame."""
    bg_dark, bg_mid, neon_glow, neon_text = style

    img = Image.new("RGBA", (W, H), (*bg_dark, 255))

    # 1) Arcade background
    img = draw_arcade_bg(img, bg_dark, bg_mid, neon_glow, seed=screen_idx * 31 + 13)

    # 2) Text
    font_title, font_sub = get_fonts()
    top_text, bottom_text = caption

    text_y = int(H * 0.032)
    img = draw_neon_text(img, (W // 2, text_y), top_text, font_title, neon_text, neon_glow)

    if bottom_text:
        sub_y = text_y + 105
        # Subtitle in white with same glow
        img = draw_neon_text(img, (W // 2, sub_y), bottom_text, font_sub,
                             (255, 255, 255), neon_glow)

    # 3) iPhone 15 Pro frame
    pw = int(W * 0.82)
    ph = int(pw * 2.165)
    px = (W - pw) // 2
    py = int(H * 0.15)

    # Ensure phone doesn't go past bottom
    if py + ph > H - 20:
        ph = H - 20 - py

    img = draw_iphone_frame(img, raw_img, px, py, pw, ph)

    return img


FULLSCREEN_CSS = """
    .screen { max-width: 92vw !important; width: 92vw !important; }
    .ui-layer { padding: 0 !important; }
    #scoreDisplay { font-size: 3rem !important; }
"""

async def goto_and_inject(page, url):
    """Navigate and inject fullscreen CSS."""
    await page.goto(url, wait_until="networkidle")
    await page.add_style_tag(content=FULLSCREEN_CSS)
    await page.wait_for_timeout(500)

# --- Capture logic ---
async def capture_screens_for_lang(browser, lang, locale):
    raw_dir = OUT_DIR / "raw" / lang
    raw_dir.mkdir(parents=True, exist_ok=True)

    page = await browser.new_page(
        viewport={"width": 430, "height": 932},
        device_scale_factor=3,
        locale=locale,
    )
    await goto_and_inject(page, GAME_URL)
    await page.wait_for_timeout(1500)

    raw_files = []

    print("  01 Menu...")
    await page.screenshot(path=str(raw_dir / "01_menu.png"))
    raw_files.append(str(raw_dir / "01_menu.png"))

    print("  02 Boutique Balles...")
    await page.click("#btnShop")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "02_balls.png"))
    raw_files.append(str(raw_dir / "02_balls.png"))

    print("  03 Boutique Traînées...")
    await page.click("#tabTrails")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "03_trails.png"))
    raw_files.append(str(raw_dir / "03_trails.png"))

    print("  04 Missions...")
    await page.click("#btnCloseShop")
    await page.wait_for_timeout(300)
    await page.click("#btnMissions")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "04_missions.png"))
    raw_files.append(str(raw_dir / "04_missions.png"))

    print("  05 Tutoriel...")
    await page.click("#btnCloseMissions")
    await page.wait_for_timeout(300)
    await page.click("#btnPlay")
    await page.wait_for_timeout(1000)
    await page.screenshot(path=str(raw_dir / "05_tutorial.png"))
    raw_files.append(str(raw_dir / "05_tutorial.png"))

    print("  06 Gameplay 1...")
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(400)
    await page.screenshot(path=str(raw_dir / "06_gameplay1.png"))
    raw_files.append(str(raw_dir / "06_gameplay1.png"))

    await goto_and_inject(page, GAME_URL)
    await page.wait_for_timeout(1500)

    print("  07 Packs...")
    await page.click("#btnIAP")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "07_packs.png"))
    raw_files.append(str(raw_dir / "07_packs.png"))

    print("  08 Stats...")
    await page.click("#btnCloseIAP")
    await page.wait_for_timeout(300)
    await page.click("#btnStats")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "08_stats.png"))
    raw_files.append(str(raw_dir / "08_stats.png"))

    print("  09 Gameplay 2...")
    await page.click("#btnCloseStats")
    await page.wait_for_timeout(300)
    await page.click("#btnPlay")
    await page.wait_for_timeout(600)
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(600)
    await page.mouse.click(300, 400)
    await page.wait_for_timeout(400)
    await page.screenshot(path=str(raw_dir / "09_gameplay2.png"))
    raw_files.append(str(raw_dir / "09_gameplay2.png"))

    print("  10 Gameplay 3...")
    await goto_and_inject(page, GAME_URL)
    await page.wait_for_timeout(1000)
    await page.click("#btnPlay")
    await page.wait_for_timeout(600)
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(300)
    await page.mouse.click(200, 500)
    await page.wait_for_timeout(300)
    await page.mouse.click(250, 400)
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "10_gameplay3.png"))
    raw_files.append(str(raw_dir / "10_gameplay3.png"))

    await page.close()
    return raw_files


def generate_store_screenshots_for_lang(lang, raw_files):
    captions = CAPTIONS[lang]
    lang_dir = OUT_DIR / lang
    lang_dir.mkdir(exist_ok=True)

    for i, (raw_path, caption) in enumerate(zip(raw_files, captions)):
        raw_img = Image.open(raw_path).convert("RGBA")
        store_img = compose_store_screenshot(raw_img, caption, SCREEN_STYLES[i], i)
        name = SCREENS[i]
        out_path = lang_dir / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
        store_img.save(str(out_path), "PNG", optimize=True)
        print(f"    {out_path.name}")


async def main():
    print("=== Swing & Snap — Arcade Store Screenshots ===")
    print(f"    Size: {W}x{H} | 10 screens x 6 languages\n")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for lang, locale in LANG_LOCALES.items():
            print(f"━━━ {lang.upper()} ({locale}) ━━━")
            raw_files = await capture_screens_for_lang(browser, lang, locale)
            print(f"  → Composing {len(raw_files)} screenshots...")
            generate_store_screenshots_for_lang(lang, raw_files)

        await browser.close()

    total = len(LANG_LOCALES) * 10
    print(f"\n✓ {total} arcade screenshots generated.")


if __name__ == "__main__":
    asyncio.run(main())
