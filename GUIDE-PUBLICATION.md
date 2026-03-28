# 🚀 GUIDE DE PUBLICATION — Swing & Snap

## Vue d'ensemble

Ce guide couvre les 3 étapes obligatoires pour publier Swing & Snap
sur l'App Store et le Google Play Store.

Temps estimé total : **4-8 heures** (la première fois)

---

## 📋 PRÉREQUIS

Avant de commencer, installe sur ton Mac/PC :

- **Node.js 18+** → https://nodejs.org
- **Git** → https://git-scm.com
- Pour iOS : **Xcode 15+** (Mac uniquement, gratuit sur l'App Store)
- Pour Android : **Android Studio** → https://developer.android.com/studio

Vérifie que tout marche :
```bash
node --version    # doit afficher v18+ 
npm --version     # doit afficher 9+
```

---

## ÉTAPE 1 : WRAPPER CAPACITOR (transformer le HTML en app native)

### 1.1 — Initialiser le projet

Copie le dossier `swing-snap-project/` sur ton ordinateur, puis :

```bash
cd swing-snap-project

# Installer les dépendances
npm install

# Ajouter les plateformes
npx cap add ios        # Si tu vises l'App Store
npx cap add android    # Si tu vises le Play Store
```

### 1.2 — Configurer le Bundle ID

Ouvre `capacitor.config.ts` et change :
```typescript
appId: 'com.tonnom.swingandsnap',  // ← Ton propre ID unique
appName: 'Swing & Snap',
```

Le Bundle ID doit être **unique au monde**. Format recommandé :
`com.prenom.swingandsnap` ou `com.tonentreprise.swingandsnap`

### 1.3 — Synchroniser et ouvrir

```bash
# Copier le code web vers les plateformes natives
npx cap sync

# Ouvrir dans l'IDE natif
npx cap open ios       # Ouvre Xcode
npx cap open android   # Ouvre Android Studio
```

### 1.4 — Tester sur simulateur/émulateur

- **iOS** : Dans Xcode, sélectionne un simulateur iPhone (ex: iPhone 15)
  puis clique ▶️ Run
- **Android** : Dans Android Studio, lance un émulateur puis clique ▶️ Run

### 1.5 — Tester sur vrai appareil

- **iOS** : Branche ton iPhone, sélectionne-le dans Xcode, Run
  (nécessite un compte Apple Developer gratuit minimum)
- **Android** : Active "Options développeur" sur ton téléphone,
  active "Débogage USB", branche-le, Run

### 1.6 — Icône et Splash Screen

Tu auras besoin de :
- **Icône** : 1024x1024 PNG (sans transparence, coins carrés — les stores arrondissent)
- **Splash Screen** : 2732x2732 PNG (centré, le contenu important au milieu)

Place-les dans `resources/` puis :
```bash
# Générer toutes les tailles automatiquement
npm install @capacitor/assets --save-dev
npx capacitor-assets generate --iconBackgroundColor '#F5F0E8' --splashBackgroundColor '#F5F0E8'
```

Suggestions pour l'icône :
- Fond crème/lin (#F5F0E8)
- Une balle lavande (#8E63B4) avec une corde
- Style minimaliste qui ressort sur fond blanc ET noir

---

## ÉTAPE 2 : COMPTES DÉVELOPPEUR

### 2.1 — Apple Developer Program (pour l'App Store)

- **Coût** : 99 $/an (≈92€)
- **URL** : https://developer.apple.com/programs/enroll/
- **Délai** : 24-48h pour la validation
- **Requis** : Un Mac avec Xcode, un Apple ID

Étapes :
1. Va sur https://developer.apple.com/programs/enroll/
2. Connecte-toi avec ton Apple ID
3. Remplis tes infos (nom, adresse)
4. Paye les 99 $
5. Attends la validation (1-2 jours)

### 2.2 — Google Play Console (pour le Play Store)

- **Coût** : 25 $ une seule fois
- **URL** : https://play.google.com/console/signup
- **Délai** : Quelques heures à quelques jours
- **Requis** : Un compte Google

Étapes :
1. Va sur https://play.google.com/console/signup
2. Connecte-toi avec ton compte Google
3. Accepte les conditions
4. Paye les 25 $
5. Remplis les infos développeur

---

## ÉTAPE 3 : INTÉGRATION ADS + IAP (MONÉTISATION)

### 3.1 — Créer un compte AdMob

1. Va sur https://admob.google.com
2. Connecte-toi avec ton compte Google
3. Crée une application "Swing & Snap"
4. Crée 2 blocs d'annonces :
   - **Interstitielle** → pour les pubs entre les parties
   - **Rewarded Video** → pour Revive + Double Gems
5. Note les Ad Unit IDs (format: `ca-app-pub-XXXXX/YYYYY`)

### 3.2 — Intégrer AdMob dans le code

Le fichier `admob-integration.js` fourni contient tout le code.
En résumé, remplace les 3 endroits dans `index.html` :

**Revive** (dans Game.revive) :
```javascript
// AVANT:
if(confirm("📺 Pub pour Revive ?")){ ... }

// APRÈS:
const watched = await showRewardedAd();
if(watched) { ... }
```

**Double Gems** (dans btnDoubleGems.onclick) :
```javascript
// AVANT:
if(confirm("📺 Regarder une pub...")){ ... }

// APRÈS:
const watched = await showRewardedAd();
if(watched) { ... }
```

**Interstitielle** (dans gameOver) :
```javascript
// AVANT:
if(ad) setTimeout(()=>showToast("📺 Publicité affichée"),500);

// APRÈS:
if(ad) setTimeout(()=>showInterstitial(),500);
```

### 3.3 — Achats Intégrés (IAP)

**Option A : RevenueCat (recommandé, plus simple)**

RevenueCat gère Apple + Google en un seul SDK :

```bash
npm install @revenuecat/purchases-capacitor
```

1. Crée un compte sur https://www.revenuecat.com (gratuit jusqu'à 2500$/mois de revenu)
2. Configure tes produits dans App Store Connect ET Google Play Console
3. Lie-les dans RevenueCat
4. Intègre dans le code :

```javascript
import Purchases from '@revenuecat/purchases-capacitor';

// Initialiser (dans Game.init)
await Purchases.configure({ apiKey: 'ta_clé_revenuecat' });

// Acheter un pack
async function buyPack(productId) {
  try {
    const result = await Purchases.purchaseProduct({ productIdentifier: productId });
    // result.customerInfo contient les achats actifs
    return true;
  } catch (e) {
    if (e.userCancelled) return false;
    console.error('Achat échoué:', e);
    return false;
  }
}
```

**Option B : Plugin Capacitor natif (plus complexe)**

```bash
npm install capacitor-purchases
```

### 3.4 — Configurer les produits IAP

**Dans App Store Connect** (iOS) :
1. Va dans "Fonctionnalités" > "Achats intégrés"
2. Crée chaque produit :
   - `gems_500` — Consommable — 0.99€
   - `gems_1200` — Consommable — 2.99€
   - `gems_3000` — Consommable — 4.99€
   - `noads` — Non-consommable — 2.99€
   - `pack_starter` — Non-consommable — 1.99€
   - `pack_ultimate` — Non-consommable — 4.99€

**Dans Google Play Console** (Android) :
1. Va dans "Monétisation" > "Produits" > "Produits intégrés"
2. Crée les mêmes produits avec les mêmes IDs

---

## ÉTAPE 4 : PUBLIER

### 4.1 — Héberger la Privacy Policy

1. Crée un repo GitHub (ex: `swing-snap-privacy`)
2. Active GitHub Pages dans Settings > Pages
3. Upload `privacy-policy.html` comme `index.html`
4. Ton URL sera : `https://tonpseudo.github.io/swing-snap-privacy/`

### 4.2 — Builder l'app

**iOS** :
```bash
npx cap sync ios
# Dans Xcode :
# 1. Product > Archive
# 2. Distribute App > App Store Connect
# 3. Upload
```

**Android** :
```bash
npx cap sync android
# Dans Android Studio :
# 1. Build > Generate Signed Bundle / APK
# 2. Choisis Android App Bundle (.aab)
# 3. Crée ou sélectionne ta clé de signature
# 4. Build
```

### 4.3 — Soumettre sur les stores

**App Store Connect** (https://appstoreconnect.apple.com) :
1. Crée une nouvelle app
2. Remplis : nom, description, catégorie (Jeux > Casual)
3. Upload les screenshots (6.5" iPhone + 12.9" iPad minimum)
4. Colle l'URL de ta Privacy Policy
5. Classification d'âge : remplis le questionnaire (probablement 4+)
6. Soumets pour review → Apple répond en 24-48h

**Google Play Console** :
1. Crée une nouvelle app
2. Remplis la fiche store (description, screenshots)
3. Questionnaire de contenu (pub, IAP, données)
4. Colle l'URL de ta Privacy Policy
5. Upload l'.aab
6. Release en "Production" → Google répond en quelques heures à 7 jours

### 4.4 — Descriptions Store suggérées

**Titre** : Swing & Snap

**Sous-titre** : Lâche. Vise. Snape.

**Description courte** :
Accroche-toi, tourne et lâche au bon moment ! Combien de pivots
peux-tu enchaîner ?

**Description longue** :
Swing & Snap est un jeu d'adresse addictif au style provençal.

🎯 GAMEPLAY SIMPLE, MAÎTRISE DIFFICILE
Touchez l'écran pour lâcher la corde et voler vers le prochain pivot.
Ratez votre coup et c'est game over !

⚡ DIFFICULTÉ PROGRESSIVE
La vitesse augmente tous les 10 points. Esquivez des lasers,
des faisceaux clignotants, des anneaux pulsants et des sentinelles.

🎨 +25 SKINS & TRAÎNÉES
Personnalisez votre balle et votre traînée. Des classiques aux
cosmétiques Provence : lavande, tournesol, cigale, mistral...

🏆 MISSIONS & SUCCÈS
Relevez des défis quotidiens et de progression pour gagner des
gems et débloquer des récompenses exclusives.

💎 ÉCONOMIE ÉQUILIBRÉE
Gagnez des gems en jouant, pas besoin de payer pour progresser.

**Mots-clés** : swing, snap, arcade, casual, addictif, pivot, skill,
adresse, provence, français

---

## 📝 CHECKLIST FINALE

Avant de soumettre, vérifie :

- [ ] L'app tourne sans crash sur vrai appareil (iOS + Android)
- [ ] Les pubs rewarded fonctionnent (Revive + Double Gems)
- [ ] Les pubs interstitielles s'affichent entre les parties
- [ ] Les IAP fonctionnent (au moins en sandbox/test)
- [ ] La privacy policy est accessible via URL
- [ ] L'icône est nette en 1024x1024
- [ ] Tu as des screenshots pour toutes les tailles requises
- [ ] La description store est complète
- [ ] Le questionnaire de classification d'âge est rempli
- [ ] Le son fonctionne correctement
- [ ] Le tutoriel s'affiche au premier lancement
- [ ] Le jeu tourne en mode avion (pas de dépendance réseau)
- [ ] Le bouton "Supprimer mes données" fonctionne

---

## ❓ FAQ

**Q: Combien de temps avant d'être sur les stores ?**
Première soumission : ~1 semaine entre setup et validation.
Apple review : 24-48h. Google review : quelques heures à 7 jours.

**Q: Combien ça coûte au total ?**
- Apple Developer : 99$/an
- Google Play : 25$ (une fois)
- RevenueCat : gratuit jusqu'à 2500$/mois de revenu
- AdMob : gratuit
- GitHub Pages (privacy) : gratuit
- Total démarrage : ~125$

**Q: Est-ce que je peux publier que sur un seul store ?**
Oui, tu peux commencer par Android (moins cher, review plus rapide)
puis ajouter iOS plus tard.

**Q: Les pubs rapportent combien ?**
En moyenne pour un jeu casual :
- Interstitielle : 1-5€ pour 1000 affichages
- Rewarded : 5-15€ pour 1000 affichages
Le revenu dépend du nombre de joueurs actifs.
