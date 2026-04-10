#!/usr/bin/env python3
"""Generate Feature Graphic + Tablet screenshots for Google Play Store."""

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

# Taglines per language for feature graphic
TAGLINES = {
    "fr": "Balance-toi, enchaîne les pivots !",
    "en": "Swing, chain the pivots!",
    "es": "¡Balancéate y encadena pivotes!",
    "de": "Schwing dich, reihe Pivots aneinander!",
    "it": "Dondolati, concatena i pivot!",
    "pt": "Balança e encadeia os pivots!",
}

# Same arcade style colors
SCREEN_STYLES = [
    ((15, 5, 30), (40, 15, 70), (160, 80, 255), (200, 140, 255)),
    ((10, 10, 25), (25, 25, 55), (255, 180, 40), (255, 210, 80)),
    ((5, 18, 15), (15, 40, 35), (80, 255, 140), (130, 255, 180)),
    ((25, 5, 10), (55, 12, 20), (255, 60, 80), (255, 120, 140)),
    ((5, 10, 30), (15, 25, 60), (40, 200, 255), (100, 220, 255)),
    ((210, 60, 10), (55, 25, 10), (255, 140, 30), (255, 180, 80)),
    ((5, 18, 18), (12, 40, 40), (40, 255, 220), (100, 255, 230)),
    ((20, 5, 25), (45, 12, 55), (255, 60, 200), (255, 130, 220)),
    ((8, 8, 28), (20, 20, 60), (60, 120, 255), (120, 170, 255)),
    ((25, 8, 15), (55, 18, 30), (255, 80, 100), (255, 150, 120)),
]

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


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def draw_neon_text_on(img, pos, text, font, color, glow_color):
    """Draw neon glow text."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for spread in [6, 4, 2]:
        for dx in range(-spread, spread + 1, 2):
            for dy in range(-spread, spread + 1, 2):
                if dx * dx + dy * dy <= spread * spread:
                    gd.text((pos[0] + dx, pos[1] + dy), text,
                            fill=(*glow_color, 30), font=font, anchor=pos[2] if len(pos) > 2 else "mt")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.text((pos[0], pos[1]), text, fill=(*color, 255), font=font, anchor=pos[2] if len(pos) > 2 else "mt")
    return img


def draw_radial_gradient(img, cx, cy, radius, center_color, edge_color, steps=120):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        c = lerp_color(edge_color, center_color, 1 - t)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


# ============================================================
# 1) FEATURE GRAPHIC — 1024 x 500
# ============================================================
IMPACT_PATH = "/System/Library/Fonts/Supplemental/Impact.ttf"
FUTURA_PATH = "/System/Library/Fonts/Supplemental/Futura.ttc"
FUTURA_COND_EXTRABOLD_IDX = 4
ARIAL_BLACK_PATH = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def _make_mini_phone(screenshot_path, phone_w, phone_h, corner_r):
    """Create a mini phone mockup from a screenshot."""
    phone = Image.new("RGBA", (phone_w, phone_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(phone)

    # Phone body
    bezel = max(3, int(phone_w * 0.02))
    draw.rounded_rectangle((0, 0, phone_w, phone_h),
                           radius=corner_r, fill=(15, 15, 18))

    # Screen area
    sx, sy = bezel, bezel
    sw, sh = phone_w - bezel * 2, phone_h - bezel * 2
    sr = corner_r - bezel

    raw = Image.open(screenshot_path).convert("RGBA")
    screen = raw.resize((sw, sh), Image.LANCZOS)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=sr, fill=255)
    phone.paste(screen, (sx, sy), mask)

    return phone


def generate_feature_graphic(lang):
    """Feature graphic rendered natively at 2048x1000 for maximum sharpness."""
    import numpy as np
    from PIL import ImageEnhance

    W, H = 2048, 1000  # Native hi-res (Google Play accepts and downscales)

    # === Background: numpy float64 gradient + dithering = zero banding ===
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    ty = yy / H

    bg = np.zeros((H, W, 3), dtype=np.float64)
    bg[:, :, 0] = 12 + 25 * ty
    bg[:, :, 1] = 5 + 5 * ty
    bg[:, :, 2] = 35 + 25 * ty

    # Smooth radial glows
    for cx, cy, rad, color in [
        (W*0.40, H*0.50, W*0.45, (40, 15, 5)),
        (W*0.08, H*0.15, W*0.30, (20, 5, 35)),
        (W*0.88, H*0.80, W*0.22, (5, 25, 35)),
    ]:
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        glow = np.clip(1.0 - dist / rad, 0, 1) ** 2
        for ch in range(3):
            bg[:, :, ch] += glow * color[ch]

    bg += np.random.RandomState(42).uniform(-0.5, 0.5, bg.shape)
    bg = np.clip(bg, 0, 255).astype(np.uint8)
    img = Image.fromarray(bg, "RGB").convert("RGBA")
    draw = ImageDraw.Draw(img)

    # === Particles (soft, bigger, fewer — render then blur) ===
    particle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particle_layer)
    rng = random.Random(77)
    pcolors = [(255,255,255), (255,140,30), (255,210,50), (50,210,255), (140,60,230)]
    for _ in range(60):
        x, y = rng.randint(0, W), rng.randint(0, H)
        r = rng.randint(6, 14)
        a = rng.randint(100, 230)
        col = pcolors[rng.randint(0, len(pcolors) - 1)]
        pd.ellipse([x-r, y-r, x+r, y+r], fill=(*col, a))

    # === Speed lines ===
    for _ in range(10):
        x1 = rng.randint(-50, W+50)
        y1 = rng.randint(0, H)
        length = rng.randint(400, 900)
        angle = rng.uniform(-0.15, 0.15)
        x2 = x1 + int(length * math.cos(angle))
        y2 = y1 + int(length * math.sin(angle))
        col = pcolors[rng.randint(0, len(pcolors) - 1)]
        pd.line([(x1,y1),(x2,y2)], fill=(*col, rng.randint(20, 45)), width=rng.randint(3, 6))

    # Slight blur on particles/lines to soften the look
    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, particle_layer)
    draw = ImageDraw.Draw(img)

    # === Phones (from hi-res raw captures, native size) ===
    fg_dir = OUT_DIR / "feature-graphic"
    gameplay_path = fg_dir / "raw_gameplay.png"
    menu_path = fg_dir / "raw_menu.png"

    pw, ph = 340, 680
    cr = 44

    if gameplay_path.exists() and menu_path.exists():
        phone2 = _make_mini_phone(str(menu_path), pw, ph, cr)
        phone2_rot = phone2.rotate(-6, expand=True, resample=Image.BICUBIC)
        img.paste(phone2_rot, (int(W*0.54), int(H*0.14)), phone2_rot)

        phone1 = _make_mini_phone(str(gameplay_path), pw, ph, cr)
        phone1_rot = phone1.rotate(8, expand=True, resample=Image.BICUBIC)
        img.paste(phone1_rot, (int(W*0.67), int(H*0.06)), phone1_rot)

    # === Text (native at 2048 wide — sharp) ===
    draw = ImageDraw.Draw(img)
    text_cx = int(W * 0.27)

    try:
        font_big = ImageFont.truetype(IMPACT_PATH, 210)
        font_amp = ImageFont.truetype(IMPACT_PATH, 148)
    except:
        font_big = ImageFont.truetype(FONT_PATH, 190, index=FONT_HEAVY_IDX)
        font_amp = ImageFont.truetype(FONT_PATH, 135, index=FONT_HEAVY_IDX)

    # "SWING"
    swing_y = int(H * 0.10)
    draw.text((text_cx+4, swing_y+4), "SWING", fill=(0,0,0,130), font=font_big, anchor="mt")
    draw.text((text_cx, swing_y), "SWING", fill=(255,255,255,255), font=font_big, anchor="mt")

    # "& SNAP"
    snap_y = int(H * 0.37)
    draw.text((text_cx+3, snap_y+3), "& SNAP", fill=(0,0,0,110), font=font_amp, anchor="mt")
    draw.text((text_cx, snap_y), "& SNAP", fill=(255,140,30,255), font=font_amp, anchor="mt")

    # Tagline in pill
    try:
        font_tag = ImageFont.truetype(FUTURA_PATH, 56, index=FUTURA_COND_EXTRABOLD_IDX)
    except:
        font_tag = ImageFont.truetype(FONT_PATH, 52, index=FONT_DEMI_IDX)

    tagline = TAGLINES.get(lang, TAGLINES["en"])
    tag_y = int(H * 0.66)
    bbox = font_tag.getbbox(tagline)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    ppx, ppy = 48, 20
    px1, py1 = text_cx - tw//2 - ppx, tag_y - th//2 - ppy
    px2, py2 = text_cx + tw//2 + ppx, tag_y + th//2 + ppy
    draw.rounded_rectangle((px1, py1, px2, py2), radius=44, fill=(0,0,0,130))
    draw.rounded_rectangle((px1-2, py1-2, px2+2, py2+2), radius=46, outline=(255,140,30,90))
    draw.text((text_cx, tag_y), tagline, fill=(255,255,255,255), font=font_tag, anchor="mm")

    # Badge
    try:
        font_badge = ImageFont.truetype(FUTURA_PATH, 36, index=FUTURA_COND_EXTRABOLD_IDX)
    except:
        font_badge = ImageFont.truetype(FONT_PATH, 34, index=FONT_DEMI_IDX)

    badge_txt = {"fr": "UN SEUL DOIGT", "en": "ONE FINGER", "es": "UN SOLO DEDO",
                 "de": "EIN FINGER", "it": "UN DITO", "pt": "UM DEDO"}
    draw.text((text_cx, int(H*0.82)), badge_txt.get(lang, "ONE FINGER"),
              fill=(50,210,255,230), font=font_badge, anchor="mt")

    # === Final: convert RGB, no downscale — keep 2048x1000 ===
    img = img.convert("RGB")

    return img


# ============================================================
# 2) TABLET SCREENSHOTS (adapt phone screenshots)
# ============================================================
def draw_arcade_bg_tablet(img, bg_dark, bg_mid, neon_glow, seed):
    """Arcade background for tablet format."""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed)

    for y in range(h):
        t = y / h
        c = lerp_color(bg_dark, bg_mid, t * 0.6 + 0.2)
        draw.line([(0, y), (w, y)], fill=c)

    img = draw_radial_gradient(img, w // 2, int(h * 0.50), int(w * 0.9),
                               (*neon_glow, 45), (*bg_dark, 0))

    draw = ImageDraw.Draw(img)
    for _ in range(50):
        x, y = rng.randint(0, w), rng.randint(0, h)
        r = rng.randint(1, 4)
        a = rng.randint(60, 160)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, a))
        img = Image.alpha_composite(img, overlay)

    for _ in range(6):
        x1 = rng.randint(-50, w + 50)
        y1 = rng.randint(0, h)
        length = rng.randint(80, 250)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).line(
            [(x1, y1), (x1 + int(length * 0.3), y1 - length)],
            fill=(*neon_glow, 25), width=rng.randint(2, 4))
        img = Image.alpha_composite(img, overlay)

    return img


def compose_tablet_screenshot(raw_img, caption, style, screen_idx, size):
    """Compose tablet screenshot with same arcade style."""
    W, H = size
    bg_dark, bg_mid, neon_glow, neon_text = style

    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    img = draw_arcade_bg_tablet(img, bg_dark, bg_mid, neon_glow, seed=screen_idx * 31 + 99)

    # Fonts (scaled for tablet)
    scale = W / 1290.0
    try:
        font_title = ImageFont.truetype(FONT_PATH, max(40, int(92 * scale)), index=FONT_HEAVY_IDX)
        font_sub = ImageFont.truetype(FONT_PATH, max(30, int(68 * scale)), index=FONT_DEMI_IDX)
    except:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", max(40, int(92 * scale)))
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", max(30, int(68 * scale)))

    top_text, bottom_text = caption

    text_y = int(H * 0.025)
    img = draw_neon_text_on(img, (W // 2, text_y), top_text, font_title, neon_text, neon_glow)
    if bottom_text:
        sub_y = text_y + int(100 * scale)
        img = draw_neon_text_on(img, (W // 2, sub_y), bottom_text, font_sub,
                                (255, 255, 255), neon_glow)

    # Phone frame in tablet layout (smaller, centered)
    pw = int(W * 0.55)
    ph = int(pw * 2.165)
    if ph > H * 0.82:
        ph = int(H * 0.82)
        pw = int(ph / 2.165)
    px = (W - pw) // 2
    py = int(H * 0.13)

    corner_r = int(pw * 0.13)
    bezel = int(pw * 0.018)

    draw = ImageDraw.Draw(img)

    # Shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(20, 0, -1):
        a = int(3 + i * 2)
        sd.rounded_rectangle(
            (px - i + 3, py + i, px + pw + i + 3, py + ph + i + 6),
            radius=corner_r + i, fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # Titanium
    draw.rounded_rectangle((px - 4, py - 4, px + pw + 4, py + ph + 4),
                           radius=corner_r + 4, fill=(120, 120, 125))
    draw.rounded_rectangle((px - 2, py - 2, px + pw + 2, py + ph + 2),
                           radius=corner_r + 2, fill=(145, 145, 150))
    draw.rounded_rectangle((px, py, px + pw, py + ph),
                           radius=corner_r, fill=(10, 10, 10))

    # Screen
    scr_x, scr_y = px + bezel, py + bezel
    scr_w, scr_h = pw - bezel * 2, ph - bezel * 2
    scr_r = corner_r - bezel

    screen = raw_img.resize((scr_w, scr_h), Image.LANCZOS)
    mask = Image.new("L", (scr_w, scr_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, scr_w, scr_h), radius=scr_r, fill=255)
    img.paste(screen, (scr_x, scr_y), mask)

    # Dynamic Island
    di_w = int(pw * 0.27)
    di_h = int(pw * 0.055)
    di_x = px + (pw - di_w) // 2
    di_y = py + bezel + int(pw * 0.022)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((di_x, di_y, di_x + di_w, di_y + di_h),
                           radius=di_h // 2, fill=(0, 0, 0))

    return img


# ============================================================
# CAPTURE + GENERATE
# ============================================================
async def capture_raw_screens(browser, lang, locale):
    """Capture raw screens for a language (reuse if already exist)."""
    raw_dir = OUT_DIR / "raw" / lang
    # Check if raw files already exist
    existing = list(raw_dir.glob("*.png")) if raw_dir.exists() else []
    if len(existing) >= 10:
        print(f"  → Using existing {len(existing)} raw captures")
        return sorted([str(f) for f in existing])

    raw_dir.mkdir(parents=True, exist_ok=True)
    page = await browser.new_page(
        viewport={"width": 430, "height": 932},
        device_scale_factor=3,
        locale=locale,
    )
    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)
    raw_files = []

    for step, (sel, wait, name) in enumerate([
        (None, 0, "01_menu"),
        ("#btnShop", 500, "02_balls"),
        ("#tabTrails", 500, "03_trails"),
        ("#btnCloseShop|#btnMissions", 500, "04_missions"),
        ("#btnCloseMissions|#btnPlay", 1000, "05_tutorial"),
    ]):
        if sel:
            for s in sel.split("|"):
                await page.click(s)
                await page.wait_for_timeout(300)
        if wait:
            await page.wait_for_timeout(wait)
        p = str(raw_dir / f"{name}.png")
        await page.screenshot(path=p)
        raw_files.append(p)

    # Gameplay 1
    await page.mouse.click(215, 600)
    await page.wait_for_timeout(400)
    p = str(raw_dir / "06_gameplay1.png")
    await page.screenshot(path=p)
    raw_files.append(p)

    await page.goto(GAME_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    await page.click("#btnIAP")
    await page.wait_for_timeout(500)
    p = str(raw_dir / "07_packs.png")
    await page.screenshot(path=p)
    raw_files.append(p)

    await page.click("#btnCloseIAP")
    await page.wait_for_timeout(300)
    await page.click("#btnStats")
    await page.wait_for_timeout(500)
    p = str(raw_dir / "08_stats.png")
    await page.screenshot(path=p)
    raw_files.append(p)

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
    raw_files.append(p)

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
    raw_files.append(p)

    await page.close()
    return raw_files


async def main():
    print("=== Swing & Snap — Feature Graphic + Tablet Screenshots ===\n")

    from playwright.async_api import async_playwright

    # --- Feature Graphics ---
    print("━━━ FEATURE GRAPHICS (1024x500) ━━━")
    fg_dir = OUT_DIR / "feature-graphic"
    fg_dir.mkdir(exist_ok=True)
    for lang in LANG_LOCALES:
        fg = generate_feature_graphic(lang)
        path = fg_dir / f"feature_graphic_{lang}.png"
        fg.save(str(path), "PNG", optimize=True)
        print(f"  ✓ {path.name}")

    # --- Tablet screenshots ---
    # 7" tablet: 1200 x 1920 (9:16 portrait)
    # 10" tablet: 1600 x 2560 (9:16 portrait)
    TABLET_SIZES = {
        "tablet-7": (1200, 1920),
        "tablet-10": (1600, 2560),
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for lang, locale in LANG_LOCALES.items():
            print(f"\n━━━ {lang.upper()} ━━━")
            raw_files = await capture_raw_screens(browser, lang, locale)

            for tablet_name, size in TABLET_SIZES.items():
                tab_dir = OUT_DIR / tablet_name / lang
                tab_dir.mkdir(parents=True, exist_ok=True)
                print(f"  {tablet_name} ({size[0]}x{size[1]}):")

                captions = CAPTIONS[lang]
                for i, (raw_path, caption) in enumerate(zip(raw_files, captions)):
                    raw_img = Image.open(raw_path).convert("RGBA")
                    tab_img = compose_tablet_screenshot(
                        raw_img, caption, SCREEN_STYLES[i], i, size)
                    name = SCREENS[i]
                    out = tab_dir / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
                    tab_img.save(str(out), "PNG", optimize=True)
                    print(f"    {out.name}")

        await browser.close()

    print("\n✓ Feature graphics + tablet screenshots generated!")


if __name__ == "__main__":
    asyncio.run(main())
