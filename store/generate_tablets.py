#!/usr/bin/env python3
"""Generate tablet screenshots v1.3 — mêmes dimensions/design, nouvelles captures.

- 7" tablet  : 1200×1920 (iPad mini style)
- 10" tablet : 1600×2560 (iPad 10" style)
- iPad 13"   : 2048×2732 (App Store iPad slot)
"""

import asyncio
import datetime
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR  = Path(__file__).parent
GAME_URL = "http://localhost:8080/"

FONT_PATH      = "/System/Library/Fonts/Supplemental/Avenir Next.ttc"
FONT_HEAVY_IDX = 8
FONT_DEMI_IDX  = 2

LANG_LOCALES = {
    "fr": "fr-FR", "en": "en-US", "es": "es-ES",
    "de": "de-DE", "it": "it-IT", "pt": "pt-PT",
}

# ── Captions v1.3 ────────────────────────────────────────────────────────────
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

SCREENS = ["menu","perfect_zone","blitz","classement",
           "powerups_hud","boutique_pu","streak","balls"]

SCREEN_STYLES = [
    ((15, 5, 30),  (160, 80, 255),  (200, 140, 255)),   # 01 menu — purple
    ((25, 18, 5),  (255, 200, 40),  (255, 230, 100)),   # 02 perfect_zone — gold
    ((28, 5, 5),   (255, 60, 60),   (255, 130, 120)),   # 03 blitz — red
    ((22, 14, 5),  (255, 160, 30),  (255, 200, 80)),    # 04 classement — amber
    ((5, 20, 25),  (40, 220, 255),  (120, 240, 255)),   # 05 powerups — teal
    ((15, 8, 30),  (180, 80, 255),  (210, 140, 255)),   # 06 boutique — indigo
    ((28, 12, 5),  (255, 110, 30),  (255, 170, 80)),    # 07 streak — flame
    ((10, 10, 25), (255, 180, 40),  (255, 210, 80)),    # 08 balls — gold
]

# ── Demo data v1.3 ───────────────────────────────────────────────────────────
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

TABLET_CSS = """
    .screen { max-width: 78vw !important; width: 78vw !important;
              padding: 32px 28px !important; border-radius: 32px !important; }
    .screen h1 { font-size: 3rem !important; }
    .screen h2 { font-size: 1.5rem !important; }
    .btn { padding: 16px 22px !important; font-size: 1.1rem !important;
           border-radius: 16px !important; }
    .skin-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 10px !important; }
    .skin-card { padding: 14px 10px !important; min-height: 130px !important; }
    .gem-hud { padding: 8px 18px !important; font-size: 1rem !important;
               border-radius: 26px !important; top: 24px !important; right: 8vw !important; }
    #hudScore { font-size: 5.5rem !important; }
    .tab { padding: 12px !important; font-size: .88rem !important; }
    .mission-item { padding: 16px !important; border-radius: 16px !important; }
"""


# ── Drawing helpers (identiques à l'original) ────────────────────────────────
def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed):
    bg_light = tuple(min(255, c + 20) for c in bg_dark)
    for y in range(0, H, 2):
        t = y / H
        c = lerp_color(bg_dark, bg_light, t * 0.5 + 0.1)
        draw.rectangle([(0, y), (W, y + 1)], fill=c)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2, H // 2
    glow_r = int(max(W, H) * 0.5)
    for i in range(20, 0, -1):
        r = int(glow_r * i / 20)
        a = int(35 * (1 - i / 20))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*neon_glow, a))
    img_out = Image.alpha_composite(img, glow)
    rng = random.Random(seed)
    for _ in range(25):
        px, py = rng.randint(0, W), rng.randint(0, H)
        pr = rng.randint(1, 3); pa = rng.randint(50, 130)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse([px-pr, py-pr, px+pr, py+pr], fill=(255, 255, 255, pa))
        img_out = Image.alpha_composite(img_out, ov)
    return img_out


def draw_neon_text(img, x, y, text, font, text_color, glow_color):
    W, H = img.size
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gt = ImageDraw.Draw(glow)
    for dx in range(-3, 4, 2):
        for dy in range(-3, 4, 2):
            if dx*dx + dy*dy <= 9:
                gt.text((x + dx, y + dy), text, fill=(*glow_color, 25),
                        font=font, anchor="mt")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, glow)
    ImageDraw.Draw(img).text((x, y), text, fill=(*text_color, 255),
                              font=font, anchor="mt")
    return img


def draw_tablet_frame(img, raw_screenshot, frame_rect, corner_r, bezel):
    """Cadre iPad propre — identique à l'original."""
    draw = ImageDraw.Draw(img)
    fx, fy, fw, fh = frame_rect
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(20, 0, -1):
        a = int(1.5 + i * 1.8)
        sd.rounded_rectangle(
            (fx - i + 4, fy + i + 2, fx + fw + i + 4, fy + fh + i + 6),
            radius=corner_r + i, fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)
    edge = max(4, int(fw * 0.006))
    draw.rounded_rectangle(
        (fx - edge, fy - edge, fx + fw + edge, fy + fh + edge),
        radius=corner_r + edge, fill=(175, 175, 180))
    draw.rounded_rectangle(
        (fx, fy, fx + fw, fy + fh),
        radius=corner_r, fill=(25, 25, 28))
    sx = fx + bezel; sy = fy + bezel
    sw = fw - bezel * 2; sh = fh - bezel * 2
    sr = max(3, corner_r - bezel)
    src_w, src_h = raw_screenshot.size
    screen_ratio = sw / sh; src_ratio = src_w / src_h
    if src_ratio < screen_ratio:
        scale = sw / src_w; new_w = sw; new_h = int(src_h * scale)
    else:
        scale = sh / src_h; new_w = int(src_w * scale); new_h = sh
    resized = raw_screenshot.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - sw) // 2; top = (new_h - sh) // 2
    screen_crop = resized.crop((left, top, left + sw, top + sh)).convert("RGBA")
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=sr, fill=255)
    img.paste(screen_crop, (sx, sy), mask)
    draw = ImageDraw.Draw(img)
    bar_w = int(sw * 0.28); bar_h = max(4, int(fh * 0.004))
    bar_x = fx + (fw - bar_w) // 2; bar_y = sy + sh + (bezel - bar_h) // 2
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
                            radius=bar_h // 2, fill=(70, 70, 75))
    btn_w = max(3, int(edge * 0.5)); pwr_h = int(fh * 0.03)
    pwr_y = fy + int(fh * 0.07)
    draw.rounded_rectangle(
        (fx + fw + edge, pwr_y, fx + fw + edge + btn_w, pwr_y + pwr_h),
        radius=btn_w // 2, fill=(160, 160, 165))
    return img


def compose_tablet_7(raw_img, caption, style, idx):
    """7" : 1200×1920 — cadre max, ratio naturel viewport 820×1180."""
    W, H = 1200, 1920
    bg_dark, neon_glow, neon_text = style
    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    draw = ImageDraw.Draw(img)
    img = draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed=idx * 17 + 3)
    try:
        ft = ImageFont.truetype(FONT_PATH, 58, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 40, index=FONT_DEMI_IDX)
    except Exception:
        ft = fs = ImageFont.load_default()
    top, bottom = caption
    text_y = int(H * 0.022)
    img = draw_neon_text(img, W // 2, text_y, top, ft, neon_text, neon_glow)
    if bottom:
        img = draw_neon_text(img, W // 2, text_y + 68, bottom, fs,
                             (255, 255, 255), neon_glow)
    # Ratio naturel du viewport 7" (820×1180 = 0.695) → pas de recadrage
    fy = int(H * 0.108)        # marge texte réduite
    bottom_margin = int(H * 0.025)
    fh = H - fy - bottom_margin   # utilise tout l'espace restant
    fw = int(fh * 820 / 1180)     # ratio naturel du viewport
    if fw > int(W * 0.94): fw = int(W * 0.94); fh = int(fw * 1180 / 820)
    fx = (W - fw) // 2
    corner_r = int(fw * 0.028); bezel = int(fw * 0.030)
    img = draw_tablet_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)
    return img


def compose_tablet_10(raw_img, caption, style, idx):
    """10" : 1600×2560 — cadre max, ratio naturel viewport 1024×1366."""
    W, H = 1600, 2560
    bg_dark, neon_glow, neon_text = style
    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    draw = ImageDraw.Draw(img)
    img = draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed=idx * 23 + 7)
    try:
        ft = ImageFont.truetype(FONT_PATH, 78, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 52, index=FONT_DEMI_IDX)
    except Exception:
        ft = fs = ImageFont.load_default()
    top, bottom = caption
    text_y = int(H * 0.018)
    img = draw_neon_text(img, W // 2, text_y, top, ft, neon_text, neon_glow)
    if bottom:
        img = draw_neon_text(img, W // 2, text_y + 92, bottom, fs,
                             (255, 255, 255), neon_glow)
    # Ratio naturel du viewport 10" (1024×1366 = 0.75) → pas de recadrage
    fy = int(H * 0.097)        # marge texte réduite
    bottom_margin = int(H * 0.025)
    fh = H - fy - bottom_margin
    fw = int(fh * 1024 / 1366)
    if fw > int(W * 0.96): fw = int(W * 0.96); fh = int(fw * 1366 / 1024)
    fx = (W - fw) // 2
    corner_r = int(fw * 0.022); bezel = int(fw * 0.025)
    img = draw_tablet_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)
    return img


def compose_ipad13(raw_img, caption, style, idx):
    """iPad 13" : 2048×2732 — cadre max, ratio naturel viewport 1024×1366."""
    W, H = 2048, 2732
    bg_dark, neon_glow, neon_text = style
    img = Image.new("RGBA", (W, H), (*bg_dark, 255))
    draw = ImageDraw.Draw(img)
    img = draw_arcade_bg(draw, img, W, H, bg_dark, neon_glow, seed=idx * 29 + 11)
    try:
        ft = ImageFont.truetype(FONT_PATH, 116, index=FONT_HEAVY_IDX)
        fs = ImageFont.truetype(FONT_PATH, 80, index=FONT_DEMI_IDX)
    except Exception:
        ft = fs = ImageFont.load_default()
    top, bottom = caption
    text_y = int(H * 0.018)
    img = draw_neon_text(img, W // 2, text_y, top, ft, neon_text, neon_glow)
    if bottom:
        img = draw_neon_text(img, W // 2, text_y + 136, bottom, fs,
                             (255, 255, 255), neon_glow)
    # Ratio naturel du viewport 10" (1024×1366 = 0.75) → pas de recadrage
    fy = int(H * 0.097)
    bottom_margin = int(H * 0.022)
    fh = H - fy - bottom_margin
    fw = int(fh * 1024 / 1366)
    if fw > int(W * 0.92): fw = int(W * 0.92); fh = int(fw * 1366 / 1024)
    fx = (W - fw) // 2
    corner_r = int(fw * 0.022); bezel = int(fw * 0.022)
    img = draw_tablet_frame(img, raw_img, (fx, fy, fw, fh), corner_r, bezel)
    return img


# ── Capture (v1.3) ───────────────────────────────────────────────────────────
async def fresh_tablet_page(browser, locale, vp_width, vp_height):
    """Page tablette propre avec données démo et notifications supprimées."""
    page = await browser.new_page(
        viewport={"width": vp_width, "height": vp_height},
        device_scale_factor=2, locale=locale)
    await page.add_init_script("""
        document.addEventListener('DOMContentLoaded', () => {
            window.updateMissionDot = () => {};
            const _obs = new MutationObserver(mutations => {
                mutations.forEach(m => {
                    m.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.style &&
                            node.style.position === 'fixed' &&
                            parseInt(node.style.zIndex || '0') >= 9000)
                            node.remove();
                    });
                });
            });
            if (document.body) _obs.observe(document.body, { childList: true });
        });
    """)
    await page.goto(GAME_URL, wait_until="networkidle")
    await page.evaluate(SETUP_JS)
    await page.reload(wait_until="networkidle")
    await page.add_style_tag(content=TABLET_CSS)
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


async def capture_tablet_screens(browser, lang, locale, vp_width, vp_height, suffix):
    """Capture les 8 écrans v1.3 en viewport tablette."""
    raw_dir = OUT_DIR / "raw" / f"{lang}_{suffix}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw = []

    # ── 01 Menu ──────────────────────────────────────────────
    print(f"    01 Menu...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.evaluate("""() => {
        DataManager.updateUI();
        const badge = document.getElementById('streakBadge');
        const count = document.getElementById('streakCount');
        if (badge) badge.style.display = 'flex';
        if (count) count.textContent = '7';
    }""")
    await page.wait_for_timeout(300)
    p = str(raw_dir / "01_menu.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 02 Zone Perfect ──────────────────────────────────────
    print(f"    02 Zone Perfect...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnPlay")
    await page.wait_for_timeout(800)
    try:
        await page.click("button:has-text('JOUER')", timeout=2000)
        await page.wait_for_timeout(600)
    except Exception:
        pass
    await page.evaluate("""() => {
        const t = document.getElementById('tutorialOverlay');
        if (t) { t.classList.remove('active'); t.style.display = 'none'; }
        document.querySelectorAll('.achieve-toast').forEach(el => el.remove());
    }""")
    await page.wait_for_timeout(200)
    await page.evaluate("""() => {
        Game.state = 'PLAYING';
        Game.score = 12; Game.displayScore = 12;
        document.getElementById('hudScore').textContent = '12';
        const p = Game.pivots[0];
        if (p) {
            p.isTarget = false; p.sc = 1;
            Game.player.rope = p;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p.pos.x + Math.cos(-0.6) * 70;
            Game.player.pos.y = p.pos.y + Math.sin(-0.6) * 70;
        }
        Game.activePowerups = {shield: 300, slowmo: 0, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
    }""")
    await page.wait_for_timeout(600)
    p = str(raw_dir / "02_perfect_zone.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 03 BLITZ ─────────────────────────────────────────────
    print(f"    03 BLITZ...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnTimeAttack")
    await page.wait_for_timeout(800)
    try:
        await page.click("button:has-text('JOUER')", timeout=2000)
        await page.wait_for_timeout(600)
    except Exception:
        pass
    await page.evaluate("""() => {
        const t = document.getElementById('tutorialOverlay');
        if (t) { t.classList.remove('active'); t.style.display = 'none'; }
        document.querySelectorAll('.achieve-toast').forEach(el => el.remove());
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
        Game.activePowerups = {shield: 180, slowmo: 150, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
        const p = Game.pivots[0];
        if (p) {
            p.isTarget = false; p.sc = 1;
            Game.player.rope = p;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p.pos.x + Math.cos(-0.9) * 65;
            Game.player.pos.y = p.pos.y + Math.sin(-0.9) * 65;
        }
        document.querySelectorAll('.achieve-toast').forEach(el => el.remove());
    }""")
    await page.wait_for_timeout(500)
    p = str(raw_dir / "03_blitz.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 04 Classement ────────────────────────────────────────
    print(f"    04 Classement...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnLeaderboard")
    await page.wait_for_timeout(600)
    await page.evaluate("""() => {
        const list = document.getElementById('leaderboardList');
        const lbl  = document.getElementById('leaderboardWeekLabel');
        if (lbl) lbl.textContent = '🌍 26 mai – 1 juin';
        if (!list) return;
        const players = [
            {rank:1,name:'SwingMaster',score:89,medal:'🥇',me:false},
            {rank:2,name:'SwingPro',score:47,medal:'🥈',me:true},
            {rank:3,name:'PivotKing',score:41,medal:'🥉',me:false},
            {rank:4,name:'ArcadeHero',score:38,medal:'',me:false},
            {rank:5,name:'RopeSwinger',score:35,medal:'',me:false},
            {rank:6,name:'QuickSnap',score:29,medal:'',me:false},
        ];
        const you = I18N.t('leaderboard_its_you') || '(toi)';
        list.innerHTML = players.map(pl => {
            const isMe = pl.me;
            const bg = isMe
                ? 'background:linear-gradient(135deg,rgba(244,169,38,.18),rgba(255,200,80,.1));border:1.5px solid rgba(244,169,38,.4)'
                : 'background:var(--card,#fff);border:1.5px solid rgba(0,0,0,.06)';
            return '<div style="' + bg + ';border-radius:14px;padding:10px 14px;display:flex;align-items:center;gap:10px">'
                + '<span style="min-width:26px;font-size:' + (pl.rank<=3?'1.2rem':'.9rem') + ';font-weight:900">'
                + (pl.medal || '#' + pl.rank) + '</span>'
                + '<span style="flex:1;font-size:.9rem;font-weight:' + (isMe?900:700) + '">' + pl.name + (isMe?' '+you:'') + '</span>'
                + '<span style="font-size:1rem;font-weight:900">' + pl.score + '</span></div>';
        }).join('');
        const nd = document.getElementById('leaderboardNameDisplay');
        if (nd) nd.textContent = 'SwingPro';
        const lwr = document.getElementById('leaderboardLastWeekRewards');
        if (lwr) lwr.style.display = 'none';
        const rn = document.getElementById('leaderboardResetNote');
        if (rn) rn.style.display = 'block';
    }""")
    await page.wait_for_timeout(300)
    p = str(raw_dir / "04_classement.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 05 Power-ups HUD ─────────────────────────────────────
    print(f"    05 Power-ups HUD...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnPlay")
    await page.wait_for_timeout(800)
    try:
        await page.click("button:has-text('JOUER')", timeout=2000)
        await page.wait_for_timeout(600)
    except Exception:
        pass
    await page.evaluate("""() => {
        const t = document.getElementById('tutorialOverlay');
        if (t) { t.classList.remove('active'); t.style.display = 'none'; }
        document.querySelectorAll('.achieve-toast').forEach(el => el.remove());
    }""")
    await page.wait_for_timeout(200)
    await page.evaluate("""() => {
        Game.state = 'PLAYING';
        Game.score = 18; Game.displayScore = 18;
        document.getElementById('hudScore').textContent = '18';
        Game.activePowerups = {shield: 210, slowmo: 160, magnet: 0};
        if (typeof updatePowerupHUD === 'function') updatePowerupHUD(Game.activePowerups);
        const inv = document.getElementById('hudPUInventory');
        if (inv) inv.style.display = 'none';
        const p = Game.pivots[0];
        if (p) {
            p.isTarget = false; p.sc = 1;
            Game.player.rope = p;
            Game.player.vel.x = 0; Game.player.vel.y = 0;
            Game.player.pos.x = p.pos.x + Math.cos(-0.5) * 72;
            Game.player.pos.y = p.pos.y + Math.sin(-0.5) * 72;
        }
    }""")
    await page.wait_for_timeout(600)
    p = str(raw_dir / "05_powerups_hud.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 06 Boutique Power-ups ────────────────────────────────
    print(f"    06 Boutique...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnIAP")
    await page.wait_for_timeout(600)
    p = str(raw_dir / "06_boutique_pu.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 07 Streak popup ──────────────────────────────────────
    print(f"    07 Streak...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.evaluate("""() => {
        if (typeof showStreakPopup === 'function') showStreakPopup(7, 35, true);
    }""")
    await page.wait_for_timeout(600)
    p = str(raw_dir / "07_streak.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    # ── 08 Collection Balles ─────────────────────────────────
    print(f"    08 Balles...")
    page = await fresh_tablet_page(browser, locale, vp_width, vp_height)
    await page.click("#btnShop")
    await page.wait_for_timeout(600)
    p = str(raw_dir / "08_balls.png")
    await page.screenshot(path=p); raw.append(p)
    await page.close()

    return raw


# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    print("=== Swing & Snap — Tablet Screenshots v1.3 ===\n")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for lang, locale in LANG_LOCALES.items():
            print(f"━━━ {lang.upper()} ({locale}) ━━━")
            captions = CAPTIONS[lang]

            # ── 7" captures (820×1180 @2x) ───────────────────
            print(f"  Capture 7\" (820×1180)...")
            raw7 = await capture_tablet_screens(
                browser, lang, locale, 820, 1180, "tab7")
            dir7 = OUT_DIR / "tablet-7" / lang
            dir7.mkdir(parents=True, exist_ok=True)
            print(f"  → Compose tablet-7 (1200×1920)...")
            for i, (rp, cap) in enumerate(zip(raw7, captions)):
                img = Image.open(rp).convert("RGBA")
                out = compose_tablet_7(img, cap, SCREEN_STYLES[i], i)
                path = dir7 / f"swing_snap_{lang}_{i+1:02d}_{SCREENS[i]}.png"
                out.save(str(path), "PNG", optimize=True)
                print(f"    {path.name}")

            # ── 10" captures (1024×1366 @2x) ─────────────────
            print(f"  Capture 10\" (1024×1366)...")
            raw10 = await capture_tablet_screens(
                browser, lang, locale, 1024, 1366, "tab10")
            dir10 = OUT_DIR / "tablet-10" / lang
            dir10.mkdir(parents=True, exist_ok=True)
            print(f"  → Compose tablet-10 (1600×2560)...")
            for i, (rp, cap) in enumerate(zip(raw10, captions)):
                img = Image.open(rp).convert("RGBA")
                out = compose_tablet_10(img, cap, SCREEN_STYLES[i], i)
                path = dir10 / f"swing_snap_{lang}_{i+1:02d}_{SCREENS[i]}.png"
                out.save(str(path), "PNG", optimize=True)
                print(f"    {path.name}")

            # ── iPad 13" : réutilise les raws 10" ────────────
            dir_ipad = OUT_DIR / "tablet-ipad13" / lang
            dir_ipad.mkdir(parents=True, exist_ok=True)
            print(f"  → Compose iPad 13\" (2048×2732)...")
            for i, (rp, cap) in enumerate(zip(raw10, captions)):
                img = Image.open(rp).convert("RGBA")
                out = compose_ipad13(img, cap, SCREEN_STYLES[i], i)
                path = dir_ipad / f"swing_snap_{lang}_{i+1:02d}_{SCREENS[i]}.png"
                out.save(str(path), "PNG", optimize=True)
                print(f"    {path.name}")

        await browser.close()

    print(f"\n✅ Screenshots tablettes générés !")
    print(f"  tablet-7/      → 1200×1920  (Google Play 7\")")
    print(f"  tablet-10/     → 1600×2560  (Google Play 10\")")
    print(f"  tablet-ipad13/ → 2048×2732  (App Store iPad 13\")")


if __name__ == "__main__":
    asyncio.run(main())
