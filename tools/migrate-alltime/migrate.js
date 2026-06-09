/**
 * Migration "All-Time" pour Swing & Snap
 * --------------------------------------
 * Parcourt TOUTES les semaines de `weeklyScores` et `blitzWeekly`,
 * calcule le MEILLEUR score de chaque joueur (toutes semaines confondues),
 * puis met à jour `allTimeScores` et `blitzAllTime` si ce score est
 * supérieur à celui déjà présent.
 *
 * Tourne en local avec firebase-admin (bypasse les règles de sécurité).
 * 100% gratuit, aucun forfait Blaze requis.
 *
 * Usage : node migrate.js
 */

const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
const db = admin.firestore();

// Lit toutes les semaines d'une collection hebdo et renvoie une Map uid -> {name, score}
async function collectWeeklyBests(weeklyCollection) {
  const bests = new Map(); // uid -> {name, score}
  // listDocuments() renvoie aussi les docs "parents fantômes" (qui n'ont que des sous-collections)
  const weekRefs = await db.collection(weeklyCollection).listDocuments();
  console.log(`  ${weeklyCollection}: ${weekRefs.length} semaine(s) trouvée(s)`);

  for (const weekRef of weekRefs) {
    const players = await weekRef.collection('players').get();
    players.forEach(doc => {
      const data = doc.data() || {};
      const score = Number(data.score) || 0;
      if (score <= 0) return;
      const uid = doc.id;
      const prev = bests.get(uid);
      if (!prev || score > prev.score) {
        bests.set(uid, { name: data.name || 'Joueur', score });
      }
    });
    console.log(`    • semaine ${weekRef.id} : ${players.size} joueur(s)`);
  }
  return bests;
}

// Écrit les meilleurs scores dans la collection all-time (si > existant)
async function writeAllTime(allTimeCollection, bests) {
  // Charge les all-time existants
  const existingSnap = await db.collection(allTimeCollection).get();
  const existing = new Map();
  existingSnap.forEach(doc => existing.set(doc.id, Number(doc.data().score) || 0));

  let writes = 0;
  let batch = db.batch();
  let opsInBatch = 0;

  for (const [uid, { name, score }] of bests) {
    const current = existing.get(uid) || 0;
    if (score > current) {
      const ref = db.collection(allTimeCollection).doc(uid);
      batch.set(ref, {
        name,
        score,
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
      writes++;
      opsInBatch++;
      if (opsInBatch >= 450) { // limite Firestore = 500 ops/batch
        await batch.commit();
        batch = db.batch();
        opsInBatch = 0;
      }
    }
  }
  if (opsInBatch > 0) await batch.commit();
  console.log(`  → ${allTimeCollection}: ${writes} score(s) mis à jour\n`);
}

async function main() {
  console.log('🚀 Migration All-Time démarrée\n');

  console.log('📊 CLASSIQUE (weeklyScores → allTimeScores)');
  const classicBests = await collectWeeklyBests('weeklyScores');
  await writeAllTime('allTimeScores', classicBests);

  console.log('⚡ BLITZ (blitzWeekly → blitzAllTime)');
  const blitzBests = await collectWeeklyBests('blitzWeekly');
  await writeAllTime('blitzAllTime', blitzBests);

  console.log('✅ Migration terminée !');
  process.exit(0);
}

main().catch(err => {
  console.error('❌ Erreur:', err);
  process.exit(1);
});
