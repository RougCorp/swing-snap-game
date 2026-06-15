/**
 * Particules lumineuses — code maison pour Swing & Snap (aucune dépendance, libre).
 * Bursts "glow" dans le style néon du jeu. Pensé léger pour mobile.
 *
 * Usage (à intégrer plus tard dans le jeu, testé en navigateur d'abord) :
 *   const fx = new FxLayer();
 *   fx.burst(x, y, 'perfect');        // sur un PERFECT
 *   fx.update(dt); fx.draw(ctx);      // dans la boucle
 *
 * Presets accordés aux couleurs du jeu :
 *   perfect → or/orange (zone dorée)   gem → cyan/bleu   snap → violet (pivot)
 */

const FX_PRESETS = {
  perfect: { count: 20, speed: [2.2, 6.5], size: [2, 5], life: [26, 46], gravity: 0.05, drag: 0.91, colors: ['#FFE46E', '#F4A926', '#FF8C00'], glow: 14 },
  gem:     { count: 10, speed: [1.4, 3.8], size: [1.5, 3.5], life: [18, 32], gravity: 0.03, drag: 0.92, colors: ['#7FE9FF', '#64B5F6', '#B388FF'], glow: 10 },
  snap:    { count: 12, speed: [1.6, 4.2], size: [1.5, 3], life: [16, 28], gravity: 0, drag: 0.90, colors: ['#C7A6E8', '#8E63B4'], glow: 0 },
  star:    { count: 26, speed: [2.5, 7.5], size: [2, 6], life: [30, 54], gravity: 0.04, drag: 0.93, colors: ['#FFFFFF', '#FFE46E', '#FFB300'], glow: 16 }
};

function _rand(a, b) { return a + Math.random() * (b - a); }
function _pick(arr) { return arr[(Math.random() * arr.length) | 0]; }

class FxLayer {
  constructor() { this.parts = []; }

  // Émet un burst au point (x,y). preset = clé de FX_PRESETS (ou objet custom).
  burst(x, y, preset) {
    const p = typeof preset === 'string' ? (FX_PRESETS[preset] || FX_PRESETS.perfect) : preset;
    for (let i = 0; i < p.count; i++) {
      const a = Math.random() * Math.PI * 2;
      const sp = _rand(p.speed[0], p.speed[1]);
      this.parts.push({
        x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
        size: _rand(p.size[0], p.size[1]),
        life: _rand(p.life[0], p.life[1]), maxLife: 0,
        color: _pick(p.colors), gravity: p.gravity, drag: p.drag, glow: p.glow
      });
      const last = this.parts[this.parts.length - 1]; last.maxLife = last.life;
    }
  }

  update(dt) {
    dt = dt || 1;
    for (let i = this.parts.length - 1; i >= 0; i--) {
      const q = this.parts[i];
      q.vx *= q.drag; q.vy = q.vy * q.drag + q.gravity * dt;
      q.x += q.vx * dt; q.y += q.vy * dt;
      q.life -= dt;
      if (q.life <= 0) this.parts.splice(i, 1);
    }
  }

  draw(ctx) {
    for (const q of this.parts) {
      const a = q.life / q.maxLife;          // fondu en sortie
      ctx.globalAlpha = a < 0 ? 0 : a;
      if (q.glow) { ctx.shadowBlur = q.glow; ctx.shadowColor = q.color; }
      ctx.fillStyle = q.color;
      ctx.beginPath();
      ctx.arc(q.x, q.y, q.size * (0.4 + 0.6 * a), 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1; ctx.shadowBlur = 0;
  }

  get count() { return this.parts.length; }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { FxLayer, FX_PRESETS };
if (typeof window !== 'undefined') window.FxLayer = FxLayer;
