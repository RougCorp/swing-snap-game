/**
 * Cloud Functions — Swing & Snap
 *
 * Synchro automatique des classements "all-time".
 * Dès qu'un score hebdo est écrit (Classique ou Blitz), on met à jour le
 * meilleur score "all-time" du joueur s'il est dépassé. Remplace le script
 * manuel tools/migrate-alltime/migrate.js et garantit que TOUS les scores
 * (même venant d'anciennes versions de l'app) remontent dans l'all-time.
 */
const { onDocumentWritten } = require("firebase-functions/v2/firestore");
const { initializeApp } = require("firebase-admin/app");
const { getFirestore, FieldValue } = require("firebase-admin/firestore");

initializeApp();
const db = getFirestore();

async function syncAllTime(allTimeCol, event) {
  const after = event.data && event.data.after && event.data.after.data();
  if (!after) return; // suppression → rien à faire
  const score = Number(after.score) || 0;
  if (score <= 0) return;
  const uid = event.params.uid;
  const ref = db.collection(allTimeCol).doc(uid);
  const snap = await ref.get();
  const current = snap.exists ? (Number(snap.data().score) || 0) : 0;
  if (score > current) {
    await ref.set(
      { name: after.name || "Joueur", score, updatedAt: FieldValue.serverTimestamp() },
      { merge: true }
    );
  }
}

// Classique : weeklyScores/{week}/players/{uid} → allTimeScores/{uid}
exports.syncClassicAllTime = onDocumentWritten(
  "weeklyScores/{week}/players/{uid}",
  (event) => syncAllTime("allTimeScores", event)
);

// Blitz : blitzWeekly/{week}/players/{uid} → blitzAllTime/{uid}
exports.syncBlitzAllTime = onDocumentWritten(
  "blitzWeekly/{week}/players/{uid}",
  (event) => syncAllTime("blitzAllTime", event)
);
