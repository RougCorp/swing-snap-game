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
          // Le jeu réel ne garde que 2 pivots à la fois → ne vérifier que les 2 derniers
          // (sinon impossible de caser un long niveau sans chevauchement → placements dégénérés)
          let ok = true;
          for (const p of pivots.slice(-2)) {
            if (Math.hypot(x - p.x, y - p.y) < C.minPivotDist) { ok = false; break; }
          }
          if (ok) valid = true;
        }
      }
      if (!valid) {
        // Secours : viser vers le centre de l'arène (évite de se coincer dans un coin
        // et les placements dégénérés). Distance raisonnable, clampée dans les bords.
        const last = pivots[i - 1];
        const ang = Math.atan2(DUEL_VH / 2 - last.y, DUEL_VW / 2 - last.x) + (rng() - 0.5) * 1.2;
        const d = C.minPivotDist * 1.15;
        x = Math.max(C.margin, Math.min(DUEL_VW - C.margin, last.x + Math.cos(ang) * d));
        y = Math.max(C.margin, Math.min(DUEL_VH - C.margin, last.y + Math.sin(ang) * d));
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

// ── Viewport : mappe le terrain virtuel VW×VH vers l'écran réel ───────────
// "fit-inside" centré (letterbox) → l'arène entière est visible, même aspect
// ratio sur tous les téléphones (la clé pour que le fantôme reste aligné).
function computeViewport(screenW, screenH) {
  const scale = Math.min(screenW / DUEL_VW, screenH / DUEL_VH);
  const drawW = DUEL_VW * scale, drawH = DUEL_VH * scale;
  return {
    scale,
    offsetX: (screenW - drawW) / 2,
    offsetY: (screenH - drawH) / 2,
    drawW, drawH
  };
}

// Coordonnée virtuelle → coordonnée écran (pour dessiner monde + fantôme)
function toScreen(vx, vy, vp) {
  return { x: vp.offsetX + vx * vp.scale, y: vp.offsetY + vy * vp.scale };
}

// Coordonnée écran → virtuelle (pour les taps du joueur)
function toVirtual(sx, sy, vp) {
  return { x: (sx - vp.offsetX) / vp.scale, y: (sy - vp.offsetY) / vp.scale };
}

// ── Simulation physique déterministe (portée fidèlement du jeu réel) ──────
// Orbite autour du pivot, release (+25% de vitesse), vol libre, snap dans
// le rayon, perfect dans le cône. Mêmes constantes que le jeu.
const SIM = {
  ropeLength: 70, snapRadius: 90, perfectRadius: 25, releaseBoost: 1.25,
  // [score, vitesse angulaire] — repris de CONFIG.speedTiers
  speedTiers: [[0, .032], [10, .040], [20, .048], [30, .057], [40, .067], [50, .078], [60, .090], [70, .1]]
};
function speedFor(score) {
  let sp = SIM.speedTiers[0][1];
  for (let i = SIM.speedTiers.length - 1; i >= 0; i--) { if (score >= SIM.speedTiers[i][0]) { sp = SIM.speedTiers[i][1]; break; } }
  return sp;
}
function angDiff(a, b) { let d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }

/**
 * Simule un run de façon 100% déterministe.
 * @param level  niveau généré par generateDuelLevel
 * @param opts   { taps:[frames] }  rejoue des taps précis (fantôme)
 *               { auto:true }       pilote automatique (bot / test)
 * Renvoie { traj:[{x,y,f}], taps:[frames], score, perfects, frames, finished }
 */
function simulateRun(level, opts) {
  opts = opts || {};
  const dt = 1, maxFrames = opts.maxFrames || 8000;
  const AUTO_AIM = 0.12, MIN_HOLD = 6; // seuil de visée + frames mini accrochées
  const tapSet = opts.taps ? new Set(opts.taps) : null;
  const recorded = [];

  let pivot = level[0], targetIdx = 1, attached = true;
  let angle = 0, holdFrames = 0, freeFrames = 0;
  let pos = { x: pivot.x + SIM.ropeLength, y: pivot.y }, vel = { x: 0, y: 0 };
  let score = 0, perfects = 0, ended = false, frame = 0, lastPerp = Infinity;
  const traj = [];

  for (frame = 0; frame < maxFrames && !ended; frame++) {
    const tp = level[targetIdx];
    // ── Décision de release ───────────────────────────────────────────────
    let release = false;
    if (attached) {
      holdFrames++;
      if (tapSet) {
        release = tapSet.has(frame);
      } else if (opts.auto && tp && holdFrames >= MIN_HOLD) {
        // Pilote auto : libère au MINIMUM de la distance perpendiculaire du rayon de
        // vitesse à la cible (release ne change que la norme, pas la direction → rayon valide)
        const vmag = Math.hypot(vel.x, vel.y) || 1;
        const ux = vel.x / vmag, uy = vel.y / vmag;
        const tx = tp.x - pos.x, ty = tp.y - pos.y;
        const proj = tx * ux + ty * uy;
        if (proj > 0) {
          const perp = Math.abs(tx * uy - ty * ux);
          if (perp < SIM.snapRadius * 0.9) {
            if (perp > lastPerp) release = true; // on vient de passer le minimum
            lastPerp = perp;
          } else lastPerp = Infinity;
        } else lastPerp = Infinity;
      }
    }
    if (release) {
      attached = false; holdFrames = 0; freeFrames = 0;
      vel = { x: vel.x * SIM.releaseBoost, y: vel.y * SIM.releaseBoost };
      recorded.push(frame);
    }
    // ── Mise à jour physique ──────────────────────────────────────────────
    const spd = speedFor(score);
    if (attached) {
      angle += spd * dt;
      pos.x = pivot.x + Math.cos(angle) * SIM.ropeLength;
      pos.y = pivot.y + Math.sin(angle) * SIM.ropeLength;
      const s = spd * SIM.ropeLength;
      vel.x = -Math.sin(angle) * s; vel.y = Math.cos(angle) * s;
    } else {
      pos.x += vel.x * dt; pos.y += vel.y * dt; freeFrames++;
      if (tp) {
        const d = Math.hypot(pos.x - tp.x, pos.y - tp.y);
        if (d < SIM.snapRadius) {
          attached = true; pivot = tp;
          angle = Math.atan2(pos.y - tp.y, pos.x - tp.x);
          score++;
          const half = Math.asin(Math.min(0.98, SIM.perfectRadius / SIM.snapRadius));
          if (Math.abs(angDiff(angle, tp.coneAngle)) < half) perfects++;
          targetIdx++; freeFrames = 0; holdFrames = 0; lastPerp = Infinity;
          if (targetIdx >= level.length) ended = true;
        } else if (freeFrames > 600 || d > SIM.snapRadius * 8) {
          ended = true; // raté
        }
      } else ended = true;
    }
    traj.push({ x: pos.x, y: pos.y, f: frame });
  }
  return { traj, taps: recorded, score, perfects, frames: frame, finished: targetIdx >= level.length };
}

// Bot déterministe : joue tout seul un niveau (sert de test ET de fantôme "bot")
function autoPlay(seed, pivotCount) {
  const level = generateDuelLevel(seed, pivotCount || 60);
  return simulateRun(level, { auto: true });
}

// Export (node pour les tests ; window pour le jeu plus tard)
const _api = { makeRng, generateDuelLevel, computeViewport, toScreen, toVirtual, simulateRun, autoPlay, speedFor, SIM, DUEL_VW, DUEL_VH, DUEL_CFG };
if (typeof module !== 'undefined' && module.exports) module.exports = _api;
if (typeof window !== 'undefined') window.DuelEngine = _api;
