/**
 * Test de déterminisme du moteur de duel.
 * Lancer : node duel/test-determinism.js
 * Valide que la génération de niveau est reproductible (même graine → même
 * monde, sur n'importe quel appareil) — prérequis du fantôme visuel.
 */
const { generateDuelLevel, DUEL_VW, DUEL_VH } = require('./duel-engine.js');

let pass = 0, fail = 0;
const check = (label, ok) => { console.log((ok ? '✅' : '❌') + ' ' + label); ok ? pass++ : fail++; };

// 1) Même graine → identique
const a = generateDuelLevel(12345, 60);
const b = generateDuelLevel(12345, 60);
check('Même graine → niveau identique', JSON.stringify(a) === JSON.stringify(b));

// 2) Graine différente → différent
const c = generateDuelLevel(99999, 60);
check('Graine différente → niveau différent', JSON.stringify(a) !== JSON.stringify(c));

// 3) Pivots dans le terrain virtuel
check('Tous les pivots dans le terrain', a.every(p => p.x >= 0 && p.x <= DUEL_VW && p.y >= 0 && p.y <= DUEL_VH));

// 4) Cross-appareil : 2 "téléphones" différents, même graine → identique
const phoneA = JSON.stringify(generateDuelLevel(777, 40));
const phoneB = JSON.stringify(generateDuelLevel(777, 40));
check('Téléphone A == Téléphone B (même graine)', phoneA === phoneB);

console.log('\n' + pass + ' réussis, ' + fail + ' échoués');
process.exit(fail === 0 ? 0 : 1);
