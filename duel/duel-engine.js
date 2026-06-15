/**
 * Duel Engine — fondation déterministe des duels (fantôme visuel)
 * ================================================================
 * Génère un niveau IDENTIQUE à partir d'une graine partagée, dans un
 * TERRAIN VIRTUEL FIXE (indépendant de la taille d'écran). Les deux joueurs
 * obtiennent exactement le même monde → le fantôme de l'adversaire s'aligne
 * parfaitement sur tes pivots/obstacles, sur n'importe quel téléphone.
 *
 * 100% côté client, aucun Blaze requis. Pas encore branché au jeu (solo
 * inchangé) — intégration + rendu mis à l'échelle au moment du build duel.
 *
 * Le rendu (plus tard) mappe le terrain virtuel VW×VH vers l'écran réel
 * avec letterbox si l'aspect diffère.
 */

// ── Terrain virtuel fixe (≈ un téléphone portrait en CSS px) ──────────────
const DUEL_VW = 440;
const DUEL_VH = 950;

// ── Constantes de jeu (reprises de CONFIG du jeu réel) ────────────────────
const DUEL_CFG = {
  margin: 60, snapRadius: 90,
  minPivotDist: 220, maxPivotDist: 450, pivotDistCap: 550,
  gemSpawnChance: 0.25, gemMaxPerScreen: 4
};

// ── PRNG seedé (mulberry32) — déterministe, rapide, 32 bits ───────────────
function makeRng(seed) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ── Génération déterministe d'un niveau de duel ───────────────────────────
// Renvoie un tableau de pivots : {x, y, coneAngle, obstacle|null}
// (mêmes seuils/probabilités que spawnObstacles du jeu réel)
function generateDuelLevel(seed, pivotCount) {
  const C = DUEL_CFG;
  const rng = makeRng(seed);
  const pivots = [];

  // Distance au prochain pivot (mirror getPivotDistance, score ≈ index)
  function pivotDistance(score) {
    const range = C.maxPivotDist - C.minPivotDist;
    const scaled = Math.min(range + score * 1.5, C.pivotDistCap - C.minPivotDist);
    return C.minPivotDist + rng() * scaled;
  }

  for (let i = 0; i < pivotCount; i++) {
    let x, y;
    if (i === 0) {
      x = DUEL_VW / 2; y = DUEL_VH / 2;
    } else {
      const last = pivots[i - 1];
      const dist = pivotDistance(i);
      let valid = false, att = 0;
      while (!valid && att < 100) {
        att++;
        const a = rng() * 6.28;
        const d = dist * (0.8 + rng() * 0.4);
        x = last.x + Math.cos(a) * d;
        y = last.y + Math.sin(a) * d;
        if (x > C.margin && x < DUEL_VW - C.margin && y > C.margin && y < DUEL_VH - C.margin) {
          let ok = true;
          for (const p of pivots) {
            if (Math.hypot(x - p.x, y - p.y) < C.minPivotDist) { ok = false; break; }
          }
          if (ok) valid = true;
        }
      }
      if (!valid) {
        x = rng() * (DUEL_VW - 2 * C.margin) + C.margin;
        y = rng() * (DUEL_VH - 2 * C.margin) + C.margin;
      }
    }

    // Cône orienté vers le pivot précédent (direction d'approche du joueur)
    let coneAngle = 0;
    if (i > 0) {
      const last = pivots[i - 1];
      coneAngle = Math.atan2(last.y - y, last.x - x);
    }

    pivots.push({ x, y, coneAngle, obstacle: null });
  }

  // 2e passe : obstacles (a besoin du pivot précédent ET de l'avant-dernier)
  for (let i = 0; i < pivots.length; i++) {
    pivots[i].obstacle = pickObstacle(rng, pivots, i, C);
  }

  return pivots;
}

// Angle "safe" : évite de pointer vers le pivot précédent (mirror getSafeAngle)
function safeAngle(rng, pivots, i) {
  const blocked = i > 0
    ? Math.atan2(pivots[i - 1].y - pivots[i].y, pivots[i - 1].x - pivots[i].x)
    : rng() * 6.28;
  for (let k = 0; k < 12; k++) {
    const a = rng() * 6.28;
    let d = Math.abs(a - blocked);
    if (d > Math.PI) d = 2 * Math.PI - d;
    if (d > 1.2) return a;
  }
  return blocked + Math.PI;
}

// Choix d'obstacle (mêmes seuils/probas que spawnObstacles)
function pickObstacle(rng, pivots, i, C) {
  const s = i; // score ≈ index du pivot
  const prevP = i >= 2 ? pivots[i - 2] : null;
  const pivGap = prevP ? Math.hypot(pivots[i].x - prevP.x, pivots[i].y - prevP.y) : 9999;

  if (s >= 5 && pivGap >= 280 && rng() < 0.45) {
    const lStart = C.snapRadius + 25;
    const maxLen = Math.min(50 + rng() * 50, pivGap - C.snapRadius - 20 - lStart);
    return { type: 'laser', angle: safeAngle(rng, pivots, i), len: Math.max(20, maxLen) };
  }
  if (s >= 30 && rng() < 0.30) return { type: 'sentry', angle: safeAngle(rng, pivots, i) };
  if (s >= 40 && rng() < 0.28) return { type: 'saw', angle: safeAngle(rng, pivots, i), radius: C.snapRadius + 25 + rng() * 20 };
  if (s >= 25 && i >= 2 && rng() < 0.22) {
    // BlinkingLaser : timing on/off déterministe (mirror constructeur)
    return { type: 'blink', onTime: 1.8 + rng() * 0.8, offTime: 1.5 + rng() * 0.6 };
  }
  if (s >= 35 && rng() < 0.22) return { type: 'pulse' };
  return null;
}

// Export (node pour les tests ; window pour le jeu plus tard)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { makeRng, generateDuelLevel, DUEL_VW, DUEL_VH, DUEL_CFG };
}
