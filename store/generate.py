#!/usr/bin/env python3
"""Generate store screenshots for Swing & Snap — Arcade Design + iPhone 15 Pro."""

import asyncio
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- CONFIG ---
# iPhone 6.7"  → 1290×2796  (slot "6.7 inch Display" App Store)
# iPhone 6.5"  → 1242×2688  (slot "6.5 inch Display" App Store)
# iPad 13"     → 2048×2732  (slot "iPad 13 inch Display" App Store)
W, H = 1290, 2796          # iPhone 6.7"
W65, H65 = 1242, 2688      # iPhone 6.5"
W_IPAD, H_IPAD = 2048, 2732  # iPad 13" / 12.9"
OUT_DIR = Path(__file__).parent
GAME_URL = "http://localhost:8080/"

FONT_PATH = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX = 2

# --- CAPTIONS v1.3 (8 screens x 6 languages) ---
CAPTIONS = {
    "fr": [
        ("Enchaîne les pivots", "et bats ton record !"),
        ("Zone Perfect & ×4", "Vise la zone dorée !"),
        ("Mode BLITZ", "60 secondes, pas de mort !"),
        ("Classement mondial", "Compare ton score chaque semaine"),
        ("Bouclier · Slow-Mo · Aimant", "Active en pleine partie"),
        ("Boutique Power-Ups", "Achète et utilise en jeu"),
        ("Série quotidienne", "14 jours = skin Flamme exclusif !"),
        ("33 balles uniques", "à collectionner"),
    ],
    "en": [
        ("Chain the pivots", "and set new records!"),
        ("Perfect Zone & ×4", "Hit the golden zone!"),
        ("BLITZ mode", "60 seconds, no death!"),
        ("Global Leaderboard", "Compare your score weekly"),
        ("Shield · Slow-Mo · Magnet", "Activate during your run"),
        ("Power-Up Shop", "Buy and use in game"),
        ("Daily Streak", "14 days = exclusive Flame skin!"),
        ("33 unique balls", "to collect"),
    ],
    "es": [
        ("Encadena los pivotes", "¡y bate tu récord!"),
        ("Zona Perfect & ×4", "¡Apunta a la zona dorada!"),
        ("Modo BLITZ", "¡60 segundos, sin muerte!"),
        ("Clasificación mundial", "Compara tu score cada semana"),
        ("Escudo · Slow-Mo · Imán", "Activa en plena partida"),
        ("Tienda de Power-Ups", "Compra y usa en juego"),
        ("Racha diaria", "¡14 días = skin Llama exclusivo!"),
        ("33 bolas únicas", "por coleccionar"),
    ],
    "de": [
        ("Reihe die Pivots", "und stelle Rekorde auf!"),
        ("Perfect-Zone & ×4", "Triff die goldene Zone!"),
        ("BLITZ-Modus", "60 Sekunden, kein Tod!"),
        ("Weltrangliste", "Vergleich deinen Score wöchentlich"),
        ("Schild · Zeitlupe · Magnet", "Im Spiel aktivieren"),
        ("Power-Up Shop", "Kaufen und im Spiel nutzen"),
        ("Tägliche Serie", "14 Tage = exklusives Flammen-Skin!"),
        ("33 einzigartige Bälle", "zum Sammeln"),
    ],
    "it": [
        ("Concatena i pivot", "e batti il tuo record!"),
        ("Zona Perfect & ×4", "Mira alla zona dorata!"),
        ("Modalità BLITZ", "60 secondi, senza morte!"),
        ("Classifica mondiale", "Confronta il tuo score ogni settimana"),
        ("Scudo · Slow-Mo · Magnete", "Attiva durante la partita"),
        ("Negozio Power-Up", "Acquista e usa in gioco"),
        ("Serie quotidiana", "14 giorni = skin Fiamma esclusivo!"),
        ("33 palle uniche", "da collezionare"),
    ],
    "pt": [
        ("Encadeia os pivots", "e bate o teu recorde!"),
        ("Zona Perfect & ×4", "Mira na zona dourada!"),
        ("Modo BLITZ", "60 segundos, sem morte!"),
        ("Classificação mundial", "Compara o teu score cada semana"),
        ("Escudo · Câm. Lenta · Íman", "Ativa durante a partida"),
        ("Loja de Power-Ups", "Compra e usa em jogo"),
        ("Série diária", "14 dias = skin Chama exclusivo!"),
        ("33 bolas únicas", "para colecionar"),
    ],
}

# Arcade style: dark backgrounds with neon accent colors
# (bg_dark, bg_mid, neon_glow, neon_text) — 8 screens v1.3
SCREEN_STYLES = [
    # 01 Menu — Dark purple + neon violet
    ((15, 5, 30), (40, 15, 70), (160, 80, 255), (200, 140, 255)),
    # 02 Zone Perfect — Dark gold + neon gold
    ((25, 18, 5), (55, 40, 10), (255, 200, 40), (255, 230, 100)),
    # 03 BLITZ — Dark red + neon red
    ((28, 5, 5), (60, 10, 10), (255, 60, 60), (255, 130, 120)),
    # 04 Classement — Dark gold/bronze + neon amber
    ((22, 14, 5), (50, 32, 10), (255, 160, 30), (255, 200, 80)),
    # 05 Power-ups HUD — Dark teal + neon cyan
    ((5, 20, 25), (12, 45, 55), (40, 220, 255), (120, 240, 255)),
    # 06 Boutique — Dark indigo + neon purple
    ((15, 8, 30), (35, 18, 65), (180, 80, 255), (210, 140, 255)),
    # 07 Streak — Dark orange + neon flame
    ((28, 12, 5), (60, 28, 8), (255, 110, 30), (255, 170, 80)),
    # 08 Balls — Dark blue + neon gold
    ((10, 10, 25), (25, 25, 55), (255, 180, 40), (255, 210, 80)),
]

SCREENS = [
    "menu", "perfect_zone", "blitz", "classement",
    "powerups_hud", "boutique_pu", "streak", "balls",
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


def draw_ipad_frame(img, raw_screenshot, px, py, pw, ph):
    """Draw a realistic iPad Pro frame (no notch, thin bezels, center pill camera)."""
    draw = ImageDraw.Draw(img)
    corner_r = int(pw * 0.06)
    bezel = int(pw * 0.022)

    # Shadow
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(20, 0, -1):
        a = int(2 + i * 3)
        sd.rounded_rectangle(
            (px - i + 3, py + i, px + pw + i + 3, py + ph + i + 6),
            radius=corner_r + i, fill=(0, 0, 0, a)
        )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # Outer silver frame
    draw.rounded_rectangle((px - 4, py - 4, px + pw + 4, py + ph + 4),
                            radius=corner_r + 4, fill=(175, 175, 180))
    draw.rounded_rectangle((px - 2, py - 2, px + pw + 2, py + ph + 2),
                            radius=corner_r + 2, fill=(195, 195, 200))
    # Body
    draw.rounded_rectangle((px, py, px + pw, py + ph),
                            radius=corner_r, fill=(14, 14, 14))

    # Screen
    scr_x = px + bezel
    scr_y = py + bezel
    scr_w = pw - bezel * 2
    scr_h = ph - bezel * 2
    screen = raw_screenshot.resize((scr_w, scr_h), Image.LANCZOS)
    mask = Image.new("L", (scr_w, scr_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, scr_w, scr_h),
                                            radius=corner_r - bezel, fill=255)
    img.paste(screen, (scr_x, scr_y), mask)

    # Front camera — small pill centered at top bezel
    pill_w = int(pw * 0.055)
    pill_h = int(pw * 0.018)
    pill_x = px + (pw - pill_w) // 2
    pill_y = py + (bezel - pill_h) // 2
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                            radius=pill_h // 2, fill=(0, 0, 0))

    # Power button (right side, top)
    pb_w = 3; pb_h = int(ph * 0.06)
    pb_y = py + int(ph * 0.12)
    draw.rounded_rectangle((px + pw + 1, pb_y, px + pw + 1 + pb_w, pb_y + pb_h),
                            radius=2, fill=(140, 140, 145))

    # Volume buttons (right side)
    for vy in [int(ph * 0.22), int(ph * 0.30)]:
        draw.rounded_rectangle((px + pw + 1, py + vy, px + pw + 1 + pb_w, py + vy + int(ph * 0.055)),
                                radius=2, fill=(140, 140, 145))
    return img


def compose_ipad_screenshot(raw_img, caption, style, screen_idx):
    """Compose iPad store screenshot (2048×2732) with iPad Pro frame."""
    bg_dark, bg_mid, neon_glow, neon_text = style
    W_i, H_i = W_IPAD, H_IPAD

    img = Image.new("RGBA", (W_i, H_i), (*bg_dark, 255))
    img = draw_arcade_bg(img, bg_dark, bg_mid, neon_glow, seed=screen_idx * 31 + 99)

    # Fonts — plus grand pour iPad
    try:
        font_title = ImageFont.truetype(FONT_PATH, 148, index=FONT_HEAVY_IDX)
        font_sub   = ImageFont.truetype(FONT_PATH, 108, index=FONT_DEMI_IDX)
    except Exception:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 148)
        font_sub   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 108)

    top_text, bottom_text = caption
    text_y = int(H_i * 0.028)
    img = draw_neon_text(img, (W_i // 2, text_y), top_text, font_title, neon_text, neon_glow)
    if bottom_text:
        img = draw_neon_text(img, (W_i // 2, text_y + 162), bottom_text, font_sub,
                             (255, 255, 255), neon_glow)

    # iPad frame — centré, proportions iPad Pro 12.9"
    pw = int(W_i * 0.58)
    ph = int(pw * 1.333)   # ratio iPad Pro 12.9" portrait
    px = (W_i - pw) // 2
    py = int(H_i * 0.13)
    if py + ph > H_i - 20:
        ph = H_i - 20 - py

    # Le raw est en 1024×1366, on le redimensionne à la taille écran de l'iPad frame
    bezel = int(pw * 0.022)
    scr_w = pw - bezel * 2
    scr_h = ph - bezel * 2
    raw_resized = raw_img.resize((scr_w, scr_h), Image.LANCZOS)

    img = draw_ipad_frame(img, raw_resized, px, py, pw, ph)
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

# --- Capture logic (8 screens, same as tablets) ---
import datetime
_TODAY = datetime.date.today().strftime("%a %b %d %Y") + " 00:00:00"

DEMO_DATA = """{
    "highScore": 47, "gems": 420, "streak": 7, "_streakGemReward": 70,
    "nameIsLocked": true, "playerName": "SwingPro", "noAds": false,
    "v130TutoSeen": true,
    "lastStreakDate": \"""" + _TODAY + """\",
    "stats": {"totalRuns": 89, "totalPivots": 2847, "totalGems": 1240,
              "blitzRuns": 12, "weeklySubmitCount": 8, "weeklyTop10Count": 3},
    "timeAttackBest": 38,
    "skins": ["classic","night","sunset","ocean","forest","volcanic","candy","space","arctic","royal"],
    "trails": ["classic","night","sunset","ocean","forest","volcanic"],
    "backgrounds": ["classic","night","sunset","ocean"],
    "currentSkin": "royal", "currentTrail": "night", "currentBg": "classic",
    "powerups": {"shield": 2, "slowmo": 1, "magnet": 3},
    "campaignLevel": 8
}"""

SETUP_JS = f"""() => {{
    localStorage.setItem('swingSnapData', JSON.stringify({DEMO_DATA}));
}}"""

async def fresh_page(browser, locale):
    """Create a fresh page at 430×932 @3x with demo data injected."""
    page = await browser.new_page(
        viewport={"width": 430, "height": 932},
        device_scale_factor=3,
        locale=locale,
    )
    # add_init_script runs BEFORE any page JS on every navigation/reload.
    # IMPORTANT: plain statements (not wrapped in () => {}), otherwise the
    # function is defined but never called.
    # Sets up a MutationObserver on DOMContentLoaded that removes notification
    # banners (z-index:9999 divs appended to body by showMissionBanner).
    await page.add_init_script("""
        document.addEventListener('DOMContentLoaded', () => {
            // Override updateMissionDot (regular function, not const — override works)
            window.updateMissionDot = () => {};
            // MutationObserver catches any z-index:9999 div added to body
            const _obs = new MutationObserver(mutations => {
                mutations.forEach(m => {
                    m.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.style &&
                            node.style.position === 'fixed' &&
                            parseInt(node.style.zIndex || '0') >= 9000) {
                            node.remove();
                        }
                    });
                });
            });
            if (document.body) _obs.observe(document.body, { childList: true });
        });
    """)
    await page.goto(GAME_URL, wait_until="networkidle")
    await page.evaluate(SETUP_JS)
    await page.reload(wait_until="networkidle")
    await page.add_style_tag(content=FULLSCREEN_CSS)
    await page.wait_for_timeout(1800)
    # Cleanup: close modals & suppress remaining notification functions
    await page.evaluate("""() => {
        ['whatsNewModal','streakModal','pauseModal'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
        window.showToast = () => {};
        window.showAchievementToast = () => {};
        window.updateMissionDot = () => {};
        document.querySelectorAll('.achieve-toast, #challengeBar').forEach(el => el.remove());
        const md = document.getElementById('missionDot');
        if (md) md.style.display = 'none';
    }""")
    await page.wait_for_timeout(300)
    return page


async def start_game_and_inject(page, js_state):
    """Click PLAY, dismiss mode intro, inject game state."""
    await page.click("#btnPlay")
    await page.wait_for_timeout(800)
    # Dismiss mode intro by clicking JOUER button
    try:
        await page.click("button:has-text('JOUER')", timeout=2000)
        await page.wait_for_timeout(600)
    except Exception:
        pass
    # Hide tutorial overlay and any toast notifications
    await page.evaluate("""() => {
        const t = document.getElementById('tutorialOverlay');
        if (t) { t.classList.remove('active'); t.style.display = 'none'; }
        const hb = document.getElementById('gameHintBar');
        if (hb) hb.style.display = 'none';
        document.querySelectorAll('.achieve-toast, #challengeBar').forEach(el => el.remove());
    }""")
    await page.wait_for_timeout(200)
    # Inject state — keep PLAYING so the game loop renders properly
    await page.evaluate(js_state)
    await page.wait_for_timeout(600)


async def capture_screens_for_lang(browser, lang, locale):
    raw_dir = OUT_DIR / "raw" / lang
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_files = []

    # ─────────────────────────────────────────────────────────
    # 01 Menu — streak badge + BLITZ + CLASSEMENT visible
    # ─────────────────────────────────────────────────────────
    print("  01 Menu...")
    page = await fresh_page(browser, locale)
    await page.evaluate("""() => {
        DataManager.updateUI();
        // Force streak badge to show 7 days
        const badge = document.getElementById('streakBadge');
        const count = document.getElementById('streakCount');
        if (badge) badge.style.display = 'flex';
        if (count) count.textContent = '7';
        // Hide missions claimable notification popup
        document.querySelectorAll('.achieve-toast, #challengeBar').forEach(el => el.remove());
        const md = document.getElementById('missionDot');
        if (md) md.style.display = 'none';
    }""")
    await page.wait_for_timeout(300)
    await page.screenshot(path=str(raw_dir / "01_menu.png"))
    raw_files.append(str(raw_dir / "01_menu.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 02 Zone PERFECT — ball attached, golden cone, ×2 multiplier
    # ─────────────────────────────────────────────────────────
    print("  02 Zone Perfect (score 12)...")
    page = await fresh_page(browser, locale)
    await start_game_and_inject(page, """() => {
        Game.state = 'PLAYING';
        Game.score = 12; Game.displayScore = 12;
        document.getElementById('hudScore').textContent = '12';
        // Attach player to existing first pivot
        const p = Game.pivots[0];
        if (p) {
            p.isTarget = false; p.sc = 1;
            Game.player.rope = p;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p.pos.x + Math.cos(-0.6) * 70;
            Game.player.pos.y = p.pos.y + Math.sin(-0.6) * 70;
        }
        // Show active power-ups on RIGHT side only
        Game.activePowerups = {shield: 300, slowmo: 0, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        // Hide inventory HUD (left side) — only RIGHT active HUD
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
    }""")
    await page.screenshot(path=str(raw_dir / "02_perfect_zone.png"))
    raw_files.append(str(raw_dir / "02_perfect_zone.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 03 MODE BLITZ — dark background, timer 0:38, red ball
    # ─────────────────────────────────────────────────────────
    print("  03 Mode BLITZ (score 22, timer 38s)...")
    page = await fresh_page(browser, locale)
    await page.click("#btnTimeAttack")
    await page.wait_for_timeout(800)
    try:
        await page.click("button:has-text('JOUER')", timeout=2000)
        await page.wait_for_timeout(600)
    except Exception:
        pass
    # Hide tutorial overlay
    await page.evaluate("""() => {
        const t = document.getElementById('tutorialOverlay');
        if (t) { t.classList.remove('active'); t.style.display = 'none'; }
        const hb = document.getElementById('gameHintBar');
        if (hb) hb.style.display = 'none';
    }""")
    await page.wait_for_timeout(200)
    await page.evaluate("""() => {
        Game.state = 'PLAYING'; Game.mode = 'timeattack';
        Game.score = 22; Game.displayScore = 22;
        document.getElementById('hudScore').textContent = '22';
        Game._taStartTime = Date.now() - 22000;
        Game.timeLeft = 38000;
        const ht = document.getElementById('hudTimer');
        if (ht) { ht.textContent = '38'; ht.style.display = 'block'; }
        // Active power-ups RIGHT side only
        Game.activePowerups = {shield: 180, slowmo: 150, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        // Hide inventory HUD (left side)
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
        // Use existing game-created pivots
        const p1 = Game.pivots[0];
        if (p1) {
            p1.isTarget = false; p1.sc = 1;
            Game.player.rope = p1;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p1.pos.x + Math.cos(-0.9) * 65;
            Game.player.pos.y = p1.pos.y + Math.sin(-0.9) * 65;
        }
        const pb = document.getElementById('btnPauseBlitz');
        if (pb) pb.style.display = 'block';
        // Remove any notification toasts
        document.querySelectorAll('.achieve-toast, #challengeBar').forEach(el => el.remove());
    }""")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(raw_dir / "03_blitz.png"))
    raw_files.append(str(raw_dir / "03_blitz.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 04 Classement mondial
    # ─────────────────────────────────────────────────────────
    print("  04 Classement mondial...")
    page = await fresh_page(browser, locale)
    await page.click("#btnLeaderboard")
    await page.wait_for_timeout(600)
    # Inject fake leaderboard since Firebase won't connect
    await page.evaluate("""() => {
        const list = document.getElementById('leaderboardList');
        const lbl = document.getElementById('leaderboardWeekLabel');
        if (lbl) lbl.textContent = I18N.t('leaderboard_week_label','26 mai','1 juin') || '🌍 26 mai – 1 juin';
        if (!list) return;
        const players = [
            {rank:1,name:'SwingMaster',score:89,medal:'🥇',me:false},
            {rank:2,name:'SwingPro',score:47,medal:'🥈',me:true},
            {rank:3,name:'PivotKing',score:41,medal:'🥉',me:false},
            {rank:4,name:'ArcadeHero',score:38,medal:'',me:false},
            {rank:5,name:'RopeSwinger',score:35,medal:'',me:false},
            {rank:6,name:'QuickSnap',score:29,medal:'',me:false},
            {rank:7,name:'FlipChamp',score:24,medal:'',me:false},
            {rank:8,name:'SpeedPivot',score:19,medal:'',me:false},
        ];
        const you = I18N.t('leaderboard_its_you') || '(toi)';
        list.innerHTML = players.map(p => {
            const isMe = p.me;
            const bg = isMe
                ? 'background:linear-gradient(135deg,rgba(244,169,38,.18),rgba(255,200,80,.1));border:1.5px solid rgba(244,169,38,.4)'
                : 'background:var(--card,#fff);border:1.5px solid rgba(0,0,0,.06)';
            return '<div style="' + bg + ';border-radius:14px;padding:10px 14px;display:flex;align-items:center;gap:10px">' +
                '<span style="min-width:26px;font-size:' + (p.rank<=3?'1.2rem':'.9rem') + ';font-weight:900;color:' + (isMe?'var(--gold)':'var(--text-light)') + '">' + (p.medal||('#'+p.rank)) + '</span>' +
                '<span style="flex:1;font-size:.9rem;font-weight:' + (isMe?900:700) + ';color:var(--text)">' + p.name + (isMe?' '+you:'') + '</span>' +
                '<span style="font-size:1rem;font-weight:900;color:' + (p.rank===1?'var(--gold)':'var(--text)') + '">' + p.score + '</span>' +
                '</div>';
        }).join('');
        const lwr = document.getElementById('leaderboardLastWeekRewards');
        if (lwr) lwr.style.display = 'none';
        const nd = document.getElementById('leaderboardNameDisplay');
        if (nd) nd.textContent = 'SwingPro';
    }""")
    await page.wait_for_timeout(300)
    await page.screenshot(path=str(raw_dir / "04_classement.png"))
    raw_files.append(str(raw_dir / "04_classement.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 05 Power-ups HUD actifs en jeu (bouclier + slow-mo)
    # ─────────────────────────────────────────────────────────
    print("  05 Power-ups HUD actifs...")
    page = await fresh_page(browser, locale)
    await start_game_and_inject(page, """() => {
        Game.state = 'PLAYING';
        Game.score = 18; Game.displayScore = 18;
        document.getElementById('hudScore').textContent = '18';
        // Active power-ups RIGHT side only — NO inventory HUD (left)
        Game.activePowerups = {shield: 210, slowmo: 160, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        // Hide inventory HUD (left side)
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
        // Use existing game-created pivots
        const p1 = Game.pivots[0];
        if (p1) {
            p1.isTarget = false; p1.sc = 1;
            Game.player.rope = p1;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p1.pos.x + Math.cos(-0.5) * 72;
            Game.player.pos.y = p1.pos.y + Math.sin(-0.5) * 72;
        }
        const pb = document.getElementById('btnPauseBlitz');
        if (pb) pb.style.display = 'block';
    }""")
    await page.screenshot(path=str(raw_dir / "05_powerups_hud.png"))
    raw_files.append(str(raw_dir / "05_powerups_hud.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 06 Boutique Power-ups
    # ─────────────────────────────────────────────────────────
    print("  06 Boutique Power-ups...")
    page = await fresh_page(browser, locale)
    await page.click("#btnIAP")
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(raw_dir / "06_boutique_pu.png"))
    raw_files.append(str(raw_dir / "06_boutique_pu.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 07 Série quotidienne — streak popup (7 jours)
    # ─────────────────────────────────────────────────────────
    print("  07 Série quotidienne (streak popup)...")
    page = await fresh_page(browser, locale)
    # Trigger streak popup directly
    await page.evaluate("""() => {
        if (typeof showStreakPopup === 'function') {
            showStreakPopup(7, 35, true);
        }
    }""")
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(raw_dir / "07_streak.png"))
    raw_files.append(str(raw_dir / "07_streak.png"))
    await page.close()

    # ─────────────────────────────────────────────────────────
    # 08 Collection Balles — avec skin Flamme streak visible
    # ─────────────────────────────────────────────────────────
    print("  08 Collection Balles...")
    page = await fresh_page(browser, locale)
    await page.click("#btnShop")
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(raw_dir / "08_balls.png"))
    raw_files.append(str(raw_dir / "08_balls.png"))
    await page.close()

    return raw_files


def generate_store_screenshots_for_lang(lang, raw_files, raw_ipad_files=None):
    captions = CAPTIONS[lang]

    # ── iPhone 6.7" (1290×2796) ──────────────────────────────
    dir67 = OUT_DIR / "screenshots" / "67" / lang
    dir67.mkdir(parents=True, exist_ok=True)

    # ── iPhone 6.5" (1242×2688) ──────────────────────────────
    dir65 = OUT_DIR / "screenshots" / "65" / lang
    dir65.mkdir(parents=True, exist_ok=True)

    # ── iPad 13" (2048×2732) ─────────────────────────────────
    dir_ipad = OUT_DIR / "screenshots" / "ipad" / lang
    dir_ipad.mkdir(parents=True, exist_ok=True)

    for i, (raw_path, caption) in enumerate(zip(raw_files, captions)):
        raw_img = Image.open(raw_path).convert("RGBA")
        name = SCREENS[i]

        # iPhone 6.7"
        img67 = compose_store_screenshot(raw_img, caption, SCREEN_STYLES[i], i)
        out67 = dir67 / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
        img67.save(str(out67), "PNG", optimize=True)

        # iPhone 6.5" (resize)
        img65 = img67.resize((W65, H65), Image.LANCZOS)
        out65 = dir65 / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
        img65.save(str(out65), "PNG", optimize=True)

        # iPad 13"
        if raw_ipad_files and i < len(raw_ipad_files):
            raw_ipad = Image.open(raw_ipad_files[i]).convert("RGBA")
        else:
            raw_ipad = raw_img  # fallback: utilise le raw phone
        img_ipad = compose_ipad_screenshot(raw_ipad, caption, SCREEN_STYLES[i], i)
        out_ipad = dir_ipad / f"swing_snap_{lang}_{i+1:02d}_{name}.png"
        img_ipad.save(str(out_ipad), "PNG", optimize=True)

        print(f"    {out67.name}  +  6.5\"  +  iPad")


async def capture_screens_ipad(browser, lang, locale):
    """Capture les 8 écrans en viewport iPad (1024×1366 @2x = 2048×2732)."""
    raw_dir = OUT_DIR / "raw" / f"{lang}_ipad"
    raw_dir.mkdir(parents=True, exist_ok=True)

    async def fresh_ipad(loc):
        page = await browser.new_page(
            viewport={"width": 1024, "height": 1366},
            device_scale_factor=2,
            locale=loc,
        )
        await page.add_init_script("""
            document.addEventListener('DOMContentLoaded', () => {
                window.updateMissionDot = () => {};
                const _obs = new MutationObserver(mutations => {
                    mutations.forEach(m => {
                        m.addedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.style &&
                                node.style.position === 'fixed' &&
                                parseInt(node.style.zIndex || '0') >= 9000) {
                                node.remove();
                            }
                        });
                    });
                });
                if (document.body) _obs.observe(document.body, { childList: true });
            });
        """)
        await page.goto(GAME_URL, wait_until="networkidle")
        await page.evaluate(SETUP_JS)
        await page.reload(wait_until="networkidle")
        await page.add_style_tag(content=FULLSCREEN_CSS)
        await page.wait_for_timeout(1800)
        await page.evaluate("""() => {
            ['whatsNewModal','streakModal','pauseModal'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = 'none';
            });
            window.showToast = () => {};
            window.showAchievementToast = () => {};
            window.updateMissionDot = () => {};
            document.querySelectorAll('.achieve-toast, #challengeBar').forEach(el => el.remove());
            const md = document.getElementById('missionDot');
            if (md) md.style.display = 'none';
        }""")
        await page.wait_for_timeout(300)
        return page

    raw_files = []
    screens = [
        ("01_menu.png", None),
        ("02_perfect_zone.png", None),
        ("03_blitz.png", None),
        ("04_classement.png", None),
        ("05_powerups_hud.png", None),
        ("06_boutique_pu.png", None),
        ("07_streak.png", None),
        ("08_balls.png", None),
    ]

    # Réutiliser les mêmes captures phone — le jeu s'adapte au viewport
    # On recapture simplement à la taille iPad
    for i, (fname, _) in enumerate(screens):
        out = raw_dir / fname
        raw_files.append(str(out))

    # Capturer les écrans principaux en viewport iPad
    # 01 Menu
    page = await fresh_ipad(locale)
    await page.evaluate("""() => {
        DataManager.updateUI();
        const badge = document.getElementById('streakBadge');
        const count = document.getElementById('streakCount');
        if (badge) badge.style.display = 'flex';
        if (count) count.textContent = '7';
        document.querySelectorAll('.achieve-toast').forEach(el => el.remove());
        const md = document.getElementById('missionDot');
        if (md) md.style.display = 'none';
    }""")
    await page.wait_for_timeout(300)
    await page.screenshot(path=raw_files[0])
    await page.close()

    # 02-08 : capturer les autres écrans (réutilise les raws phone rescalés)
    # Pour iPad, on va juste copier et redimensionner les raws phone
    phone_raw_dir = OUT_DIR / "raw" / lang
    for i in range(1, 8):
        fname = screens[i][0]
        phone_raw = phone_raw_dir / fname
        if phone_raw.exists():
            img = Image.open(str(phone_raw))
            # Redimensionner proportionnellement pour remplir 1024×1366
            img_resized = img.resize((1024, 1366), Image.LANCZOS)
            img_resized.save(raw_files[i])
        else:
            # Fallback : screenshot simple
            import shutil
            if phone_raw.exists():
                shutil.copy(str(phone_raw), raw_files[i])

    return raw_files


async def main():
    print("=== Swing & Snap — Arcade Store Screenshots ===")
    print(f"    iPhone 6.7\": {W}×{H}  |  6.5\": {W65}×{H65}  |  iPad: {W_IPAD}×{H_IPAD}")
    print(f"    8 écrans × 6 langues\n")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for lang, locale in LANG_LOCALES.items():
            print(f"━━━ {lang.upper()} ({locale}) ━━━")
            # iPhone captures
            raw_files = await capture_screens_for_lang(browser, lang, locale)
            # iPad captures (menu capturé, autres redimensionnés depuis phone raw)
            raw_ipad = await capture_screens_ipad(browser, lang, locale)
            print(f"  → Composing (iPhone 6.7\" + 6.5\" + iPad)...")
            generate_store_screenshots_for_lang(lang, raw_files, raw_ipad)

        await browser.close()

    total = len(LANG_LOCALES) * 8
    print(f"\n✓ {total * 3} screenshots générés")
    print(f"  iPhone 6.7\"  → screenshots/67/{{lang}}/")
    print(f"  iPhone 6.5\"  → screenshots/65/{{lang}}/")
    print(f"  iPad 13\"     → screenshots/ipad/{{lang}}/")


if __name__ == "__main__":
    asyncio.run(main())
