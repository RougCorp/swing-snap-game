from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 1024
OUT  = "/Users/rougon/Documents/CREAPP/swing-snap/store/appicon_1024.png"

# ── Couleurs ──────────────────────────────────────────────────────────────────
BG          = (245, 237, 224, 255)   # crème
PURPLE      = (123,  82, 162, 255)   # violet principal
PURPLE_DARK = ( 90,  55, 130, 255)   # ombre boule
GREEN       = ( 91, 184,  93, 255)   # boule verte
GREEN_DARK  = ( 55, 140,  60, 255)
GHOST       = (180, 165, 200,  35)   # cercles fantômes
DASH_COLOR  = (170, 150, 195, 160)   # tirets
LINE_COLOR  = ( 90,  70, 120, 210)   # corde
DOT_COLOR   = (205, 180,  95, 200)   # petits points dorés
TEXT_DARK   = ( 62,  48,  58, 255)   # "SWING"
TEXT_PURPLE = (140, 100, 170, 255)   # "& SNAP"

img  = Image.new("RGBA", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)

# ── Cercles fantômes en arrière-plan ──────────────────────────────────────────
draw.ellipse([ 60, 280, 500, 720], fill=GHOST)
draw.ellipse([580,  60, 980, 460], fill=GHOST)
draw.ellipse([ 30, 520, 310, 800], fill=GHOST)

# ── Positions clés ────────────────────────────────────────────────────────────
PIVOT  = (490, 215)   # petit cercle haut
MAIN   = (615, 490)   # grande boule violette
GREEN_ = (720, 325)   # boule verte

# ── Tirets : arc de balançoire (de PIVOT vers la gauche/bas) ─────────────────
def bezier(p0, p1, p2, t):
    x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
    y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
    return x, y

ctrl_left = (PIVOT[0]-230, PIVOT[1]+220)
end_left  = (PIVOT[0]-290, PIVOT[1]+460)
for i in range(0, 100, 6):
    t  = i / 100.0
    t2 = (i+3) / 100.0
    bx,  by  = bezier(PIVOT, ctrl_left, end_left, t)
    bx2, by2 = bezier(PIVOT, ctrl_left, end_left, t2)
    if i % 12 < 6:
        draw.line([(bx, by), (bx2, by2)], fill=DASH_COLOR, width=5)

# Tirets : ligne vers la boule verte
for i in range(0, 88, 6):
    t  = i / 100.0
    t2 = (i+4) / 100.0
    x1 = PIVOT[0] + t  * (GREEN_[0]-PIVOT[0])
    y1 = PIVOT[1] + t  * (GREEN_[1]-PIVOT[1])
    x2 = PIVOT[0] + t2 * (GREEN_[0]-PIVOT[0])
    y2 = PIVOT[1] + t2 * (GREEN_[1]-PIVOT[1])
    if i % 12 < 6:
        draw.line([(x1, y1), (x2, y2)], fill=DASH_COLOR, width=4)

# ── Corde reliant PIVOT → grande boule ───────────────────────────────────────
draw.line([
    (PIVOT[0],        PIVOT[1]+38),
    (MAIN[0]-30,      MAIN[1]-183)
], fill=LINE_COLOR, width=5)

# ── Grande boule violette ─────────────────────────────────────────────────────
R = 188
draw.ellipse([MAIN[0]-R, MAIN[1]-R, MAIN[0]+R, MAIN[1]+R], fill=PURPLE)
# ombre intérieure (reflet sombre)
ri, ox, oy = 72, -45, -45
draw.ellipse([MAIN[0]+ox-ri, MAIN[1]+oy-ri, MAIN[0]+ox+ri, MAIN[1]+oy+ri], fill=PURPLE_DARK)

# ── Point pivot (petit cercle haut) ───────────────────────────────────────────
rp = 38
draw.ellipse([PIVOT[0]-rp, PIVOT[1]-rp, PIVOT[0]+rp, PIVOT[1]+rp], fill=PURPLE)
rpi = 20
draw.ellipse([PIVOT[0]-rpi, PIVOT[1]-rpi, PIVOT[0]+rpi, PIVOT[1]+rpi], fill=PURPLE_DARK)

# ── Boule verte ───────────────────────────────────────────────────────────────
rg = 48
draw.ellipse([GREEN_[0]-rg, GREEN_[1]-rg, GREEN_[0]+rg, GREEN_[1]+rg], fill=GREEN)
rgi = 19
draw.ellipse([GREEN_[0]-rgi, GREEN_[1]-rgi, GREEN_[0]+rgi, GREEN_[1]+rgi], fill=GREEN_DARK)

# ── Petits points dorés près de la grande boule ───────────────────────────────
for dx, dy, r in [(58, 65, 7), (85, 30, 5), (70, 88, 6)]:
    draw.ellipse([MAIN[0]+dx-r, MAIN[1]+dy-r, MAIN[0]+dx+r, MAIN[1]+dy+r], fill=DOT_COLOR)

# ── Texte ─────────────────────────────────────────────────────────────────────
FONT_PATHS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/SFNS.ttf",
]

def load_font(size, index=0):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size, index=index)
        except Exception:
            pass
    return ImageFont.load_default()

font_swing = load_font(148, index=1)   # bold si dispo
font_snap  = load_font( 82, index=0)

def center_text(text, font, y, color):
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text(((SIZE - tw) // 2, y), text, fill=color, font=font)

center_text("SWING",  font_swing, 720, TEXT_DARK)
center_text("& SNAP", font_snap,  872, TEXT_PURPLE)

# ── Sauvegarde ────────────────────────────────────────────────────────────────
img.convert("RGB").save(OUT)
print(f"✅ Icône sauvegardée : {OUT}")
