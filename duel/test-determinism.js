/**
 * Tests du moteur de duel (fondation déterministe).
 * Lancer : node duel/test-determinism.js
 * Couvre : génération de monde, simulation physique, rejeu de fantôme, bot.
 */
const E = require('./duel-engine.js');

let pass = 0, fail = 0;
const check = (label, ok) => { console.log((ok ? '✅' : '❌') + ' ' + label); ok ? pass++ : fail++; };

// 1) Monde : même graine → identique
check('Monde — même graine → identique',
  JSON.stringify(E.generateDuelLevel(12345, 60)) === JSON.stringify(E.generateDuelLevel(12345, 60)));

// 2) Monde : graine différente → différent
check('Monde — graine différente → différent',
  JSON.stringify(E.generateDuelLevel(12345, 60)) !== JSON.stringify(E.generateDuelLevel(99999, 60)));

// 3) Cross-appareil : 2 "téléphones", même graine → identique
check('Cross-appareil — même graine → identique',
  JSON.stringify(E.generateDuelLevel(777, 40)) === JSON.stringify(E.generateDuelLevel(777, 40)));

// 4) Pas de pivots dégénérés (trop proches / trop loin) sur 20 niveaux
let degenerate = 0;
for (let s = 1; s <= 20; s++) {
  const lvl = E.generateDuelLevel(s, 50);
  for (let i = 1; i < lvl.length; i++) {
    const d = Math.hypot(lvl[i].x - lvl[i - 1].x, lvl[i].y - lvl[i - 1].y);
    if (d < E.DUEL_CFG.minPivotDist * 0.79 || d > 600) degenerate++;
  }
}
check('Aucun pivot dégénéré sur 20 niveaux', degenerate === 0);

// 5) Viewport : round-trip écran <-> virtuel exact
const vp = E.computeViewport(390, 844);
const s = E.toScreen(220, 475, vp), v = E.toVirtual(s.x, s.y, vp);
check('Viewport — round-trip exact', Math.abs(v.x - 220) < 1e-6 && Math.abs(v.y - 475) < 1e-6);

// 6) Simulation : bot déterministe (même graine → trajectoire identique)
const r1 = E.autoPlay(42, 60), r2 = E.autoPlay(42, 60);
check('Simulation — bot déterministe', JSON.stringify(r1.traj) === JSON.stringify(r2.traj));

// 7) REJEU FANTÔME : taps enregistrés → trajectoire identique (cœur des duels)
const replay = E.simulateRun(E.generateDuelLevel(42, 60), { taps: r1.taps });
check('Rejeu fantôme — taps → trajectoire identique', JSON.stringify(replay.traj) === JSON.stringify(r1.traj));

// 8) Qualité du bot (fantôme de secours) : termine les niveaux sur 20 graines
let finished = 0, totalScore = 0;
for (let seed = 1; seed <= 20; seed++) {
  const r = E.autoPlay(seed, 50);
  if (r.finished) finished++;
  totalScore += r.score;
}
check('Bot — termine >=18/20 niveaux (score moyen ' + (totalScore / 20).toFixed(1) + '/50)', finished >= 18);

console.log('\n' + pass + ' réussis, ' + fail + ' échoués');
process.exit(fail === 0 ? 0 : 1);
