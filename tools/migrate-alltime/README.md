# Migration All-Time — Swing & Snap

Remplit `allTimeScores` et `blitzAllTime` avec le meilleur score de chaque
joueur, calculé sur **toutes les semaines** de `weeklyScores` / `blitzWeekly`.

Gratuit, tourne en local. Aucun forfait Blaze requis.

## Étapes

### 1. Télécharger la clé de service
1. Firebase Console → ⚙️ **Paramètres du projet**
2. Onglet **Comptes de service**
3. Bouton **Générer une nouvelle clé privée** → **Générer la clé**
4. Un fichier `.json` se télécharge
5. Renomme-le **`serviceAccountKey.json`** et place-le dans ce dossier
   (`tools/migrate-alltime/`)

### 2. Lancer la migration
```bash
cd tools/migrate-alltime
node migrate.js
```

### 3. Vérifier
Recharge les classements all-time dans le jeu : les meilleurs scores
historiques doivent maintenant apparaître.

## Important
- La clé `serviceAccountKey.json` est **secrète** → ne jamais la committer / partager.
- Tu peux **relancer ce script** quand tu veux pour resynchroniser l'historique.
