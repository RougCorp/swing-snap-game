#!/usr/bin/env python3
"""Generate App Store iPad 13" screenshots (2048x2732).

Uses tablet raw captures (rendered at iPad 1024x1366 viewport with tablet CSS
so the game UI adapts to the wider format), embedded in a sleek iPad frame
on a neon arcade background. Output is RGB (no alpha) as required by App
Store Connect.
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = Path(__file__).parent
FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

LANGS = ["fr", "en", "es", "de", "it", "pt"]

CAPTIONS = {
    "fr": [
        ("Accroche-toi", "et balance-toi !"),
        ("33 balles uniques", "à collectionner"),
        ("33 traînées", "spectaculaires"),
        ("Défis quotidiens", "et progression"),
        ("Statistiques", "et 12 succès"),
        ("Enchaîne", "les pivots !"),
        ("Vise le point vert", "et lâche la corde !"),
        ("Jusqu'où iras-tu ?", ""),
    ],
    "en": [
        ("Hold on", "and swing!"),
        ("33 unique balls", "to collect"),
        ("33 spectacular", "trail effects"),
        ("Daily challenges", "and progression"),
        ("Statistics", "and 12 achievements"),
        ("Chain", "the pivots!"),
        ("Aim for the green dot", "and release the rope!"),
        ("How far", "will you go?"),
    ],
    "es": [
        ("Agárrate", "¡y balancéate!"),
        ("33 bolas únicas", "por coleccionar"),
        ("33 estelas", "espectaculares"),
        ("Desafíos diarios", "y progresión"),
        ("Estadísticas", "y 12 logros"),
        ("¡Encadena", "los pivotes!"),
        ("Apunta al punto verde", "¡y suelta la cuerda!"),
        ("¿Hasta dónde", "llegarás?"),
    ],
    "de": [
        ("Halte fest", "und schwing dich!"),
        ("33 einzigartige Bälle", "zum Sammeln"),
        ("33 spektakuläre", "Schweif-Effekte"),
        ("Tägliche Herausforderungen", "und Fortschritt"),
        ("Statistiken", "und 12 Erfolge"),
        ("Reihe die Pivots", "aneinander!"),
        ("Ziele auf den grünen Punkt", "und lass das Seil los!"),
        ("Wie weit", "kommst du?"),
    ],
    "it": [
        ("Aggrappati", "e dondolati!"),
        ("33 palle uniche", "da collezionare"),
        ("33 effetti scia", "spettacolari"),
        ("Sfide giornaliere", "e progressione"),
        ("Statistiche", "e 12 obiettivi"),
        ("Concatena", "i pivot!"),
        ("Punta al punto verde", "e rilascia la corda!"),
        ("Fin dove", "arriverai?"),
    ],
    "pt": [
        ("Segura firme", "e balança!"),
        ("33 bolas únicas", "para colecionar"),
        ("33 efeitos de rasto", "espetaculares"),
        ("Desafios diários", "e progressão"),
        ("Estatísticas", "e 12 conquistas"),
        ("Encadeia", "os pivots!"),
        ("Aponta ao ponto verde", "e larga a corda!"),
        ("Até onde", "vais chegar?"),
    ],
}

SCREENS = [
    "menu", "balls", "trails", "missions",
    "stats", "gameplay1", "gameplay2", "gameplay3",
]

# (bg_dark, bg_mid, neon_glow, neon_text)
SCREEN_STYLES = [
    ((15, 5, 30), (40, 15, 70), (160, 80, 255), (200, 140, 255)),
    ((10, 10, 25), (25, 25, 55), (255, 180, 40), (255, 210, 80)),
    ((5, 18, 15), (15, 40, 35), (80, 255, 140), (130, 255, 180)),
    ((25, 5, 10), (55, 12, 20), (255, 60, 80), (255, 120, 140)),
    ((20, 5, 25), (45, 12, 55), (255, 60, 200), (255, 130, 220)),
    ((25, 12, 5), (55, 25, 10), (255, 140, 30), (255, 180, 80)),
    ((8, 8, 28), (20, 20, 60), (60, 120, 255), (120, 170, 255)),
    ((5, 10, 30), (15, 25, 60), (40, 200, 255), (100, 220, 255)),
]


def draw_arcade_bg(img, bg_dark, bg_mid, neon_glow, seed):
    """Smooth vertical gradient + radial glow + soft particles."""
    import numpy as np
    W, H = img.size

    yy = np.arange(H).astype(np.float64).reshape(H, 1)
    t = yy / H
    bg = np.zeros((H, W, 3), dtype=np.float64)
    bg[:, :, 0] = bg_dark[0] + (bg_mid[0] - bg_dark[0]) * (t * 0.6 + 0.2)
    bg[:, :, 1] = bg_dark[1] + (bg_mid[1] - bg_dark[1]) * (t * 0.6 + 0.2)
    bg[:, :, 2] = bg_dark[2] + (bg_mid[2] - bg_dark[2]) * (t * 0.6 + 0.2)

    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float64)
    cx, cy = W * 0.5, H * 0.5
    dist = np.sqrt((xx2 - cx) ** 2 + (yy2 - cy) ** 2)
    rad = W * 0.6
    glow_strength = np.clip(1.0 - dist / rad, 0, 1) ** 2 * 0.35
    bg[:, :, 0] += glow_strength * neon_glow[0]
    bg[:, :, 1] += glow_strength * neon_glow[1]
    bg[:, :, 2] += glow_strength * neon_glow[2]

    bg += np.random.RandomState(seed).uniform(-0.8, 0.8, bg.shape)
    bg = np.clip(bg, 0, 255).astype(np.uint8)
    img = Image.fromarray(bg).convert("RGBA")

    particle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particle_layer)
    rng = random.Random(seed)
    for _ in range(80):
        x, y = rng.randint(0, W), rng.randint(0, H)
        r = rng.randint(2, 6)
        a = rng.randint(80, 180)
        pd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

    for _ in range(8):
        x1 = rng.randint(-100, W + 100)
        y1 = rng.randint(0, H)
        length = rng.randint(200, 500)
        pd.line(
            [(x1, y1), (x1 + int(length * 0.25), y1 - length)],
            fill=(*neon_glow, rng.randint(25, 55)),
            width=rng.randint(3, 6),
        )

    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=1.8))
    img = Image.alpha_composite(img, particle_layer)
    return img


def draw_neon_text(img, x, y, text, font, text_color, glow_color):
    """Neon text with multi-pass glow."""
    W, H = img.size
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for spread in [8, 5, 3]:
        for dx in range(-spread, spread + 1, 2):
            for dy in range(-spread, spread + 1, 2):
                if dx * dx + dy * dy <= spread * spread:
                    gd.text((x + dx, y + dy), text,
                            fill=(*glow_color, 22), font=font, anchor="mt")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, glow)
    ImageDraw.Draw(img).text((x, y), text, fill=(*text_color, 255),
                             font=font, anchor="mt")
    return img


def draw_ipad_frame(img, raw_screenshot, frame_rect, corner_r, bezel):
    """Draw a clean modern iPad Pro-style frame with the screenshot inside."""
    fx, fy, fw, fh = frame_rect

    # Drop shadow (soft, realistic)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(30, 0, -1):
        a = int(1.5 + i * 1.8)
        sd.rounded_rectangle(
            (fx - i + 6, fy + i + 4, fx + fw + i + 6, fy + fh + i + 10),
            radius=corner_r + i, fill=(0, 0, 0, a))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # Aluminum edge (titanium look)
    edge = max(6, int(fw * 0.007))
    draw.rounded_rectangle(
        (fx - edge, fy - edge, fx + fw + edge, fy + fh + edge),
        radius=corner_r + edge, fill=(175, 175, 180))

    # Dark body (iPad black bezel area)
    draw.rounded_rectangle(
        (fx, fy, fx + fw, fy + fh),
        radius=corner_r, fill=(20, 20, 22))

    # Screen area (thin uniform bezels)
    sx = fx + bezel
    sy = fy + bezel
    sw = fw - bezel * 2
    sh = fh - bezel * 2
    sr = max(6, corner_r - bezel)

    # Crop-to-fill the tablet screenshot into the screen area
    src_w, src_h = raw_screenshot.size
    screen_ratio = sw / sh
    src_ratio = src_w / src_h
    if src_ratio < screen_ratio:
        scale = sw / src_w
        new_w = sw
        new_h = int(src_h * scale)
    else:
        scale = sh / src_h
        new_w = int(src_w * scale)
        new_h = sh

    resized = raw_screenshot.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - sw) // 2
    top = (new_h - sh) // 2
    screen = resized.crop((left, top, left + sw, top + sh)).convert("RGBA")

    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=sr, fill=255)
    img.paste(screen, (sx, sy), mask)
    draw = ImageDraw.Draw(img)

    # Front camera dot (small, top-center of screen area)
    cam_r = max(4, int(fw * 0.004))
    cam_x = fx + fw // 2
    cam_y = fy + bezel // 2
    draw.ellipse(
        (cam_x - cam_r, cam_y - cam_r, cam_x + cam_r, cam_y + cam_r),
        fill=(50, 50, 55))

    # Home indicator bar (bottom center inside bezel)
    bar_w = int(sw * 0.25)
    bar_h = max(5, int(fh * 0.004))
    bar_x = fx + (fw - bar_w) // 2
    bar_y = sy + sh + (bezel - bar_h) // 2
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=bar_h // 2, fill=(75, 75, 80))

    return img


def compose_ipad13(raw_img, caption, style, idx):
    """Compose iPad 13" screenshot at 2048x2732 with iPad frame + neon bg."""
    W, H = 2048, 2732
    bg_dark, bg_mid, neon_glow, neon_text = style

    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    img = draw_arcade_bg(img, bg_dark, bg_mid, neon_glow, seed=idx * 47 + 13)

    # Caption at top
    try:
        ft = ImageFont.truetype(FONT_PATH, 120, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 84, index=FONT_DEMI_IDX)
    except Exception:
        ft = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        fs = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 84)

    top_text, bottom_text = caption
    img = draw_neon_text(img, W // 2, int(H * 0.028), top_text,
                         ft, neon_text, neon_glow)
    if bottom_text:
        img = draw_neon_text(img, W // 2, int(H * 0.065), bottom_text,
                             fs, (255, 255, 255), neon_glow)

    # iPad frame — 2:3 ratio (modern iPad), ~84% of canvas width
    fw = int(W * 0.84)           # ~1720 px
    fh = int(fw * 3 / 2)         # ~2580 px → 2:3 portrait iPad
    # Ensure vertical budget (text ~12% + frame + 4% bottom margin)
    max_fh = int(H * 0.84)
    if fh > max_fh:
        fh = max_fh
        fw = int(fh * 2 / 3)
    fx = (W - fw) // 2
    fy = int(H * 0.135)
    corner_r = int(fw * 0.028)   # ~3% of width (iPad Pro radius)
    bezel = int(fw * 0.026)      # ~2.6% uniform thin bezels

    img = draw_ipad_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)
    return img


def main():
    print("=== Swing & Snap — iPad 13\" screenshots (2048x2732) ===\n")

    for lang in LANGS:
        raw_dir = OUT_DIR / "raw" / f"{lang}_tab10"
        if not raw_dir.exists():
            print(f"  ! Missing raw dir {raw_dir.name}, skipping")
            continue

        out_dir = OUT_DIR / "appstore" / "ipad-13" / lang
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"━━━ {lang.upper()} ━━━")
        captions = CAPTIONS[lang]

        raw_names = [
            "01_menu.png",
            "02_balls.png",
            "03_trails.png",
            "04_missions.png",
            "05_stats.png",
            "06_gameplay1.png",
            "07_gameplay2.png",
            "08_gameplay3.png",
        ]

        for i in range(8):
            raw_path = raw_dir / raw_names[i]
            if not raw_path.exists():
                print(f"  ! Missing {raw_path.name}, skipping")
                continue

            raw_img = Image.open(raw_path).convert("RGBA")
            out = compose_ipad13(raw_img, captions[i], SCREEN_STYLES[i], i)

            # Apple requires RGB (no alpha)
            rgb = Image.new("RGB", out.size, (0, 0, 0))
            rgb.paste(out, mask=out.split()[3])

            name = SCREENS[i]
            path = out_dir / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
            rgb.save(str(path), "PNG", optimize=True)
            print(f"  ✓ {path.name}")

    print("\n✅ iPad 13\" screenshots generated at appstore/ipad-13/")


if __name__ == "__main__":
    main()
