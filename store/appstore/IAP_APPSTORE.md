# App Store Connect — Configuration des In-App Purchases

Ce document couvre tout ce qu'il faut faire **côté App Store Connect** pour activer les achats intégrés dans Swing & Snap. À faire en parallèle pendant que Claude écrit le code.

⚠️ **Ordre important** : le **Paid Apps Agreement** doit être signé en premier, sinon l'onglet "In-App Purchases" reste grisé.

---

## Étape 1 — Paid Apps Agreement (~30 min)

1. Va sur [App Store Connect](https://appstoreconnect.apple.com)
2. **Business** → **Agreements, Tax, and Banking**
3. Cherche la ligne **"Paid Apps"** — status "Request" ou "View"
4. Clique → **"View Agreement"** → lis et accepte les CGU

### Sub-étape 1a — Contact Info
- **Legal** : ton nom  
- **Senior Management** : ton nom (même contact)  
- **Financial** : ton nom + ton IBAN à venir  
- **Technical** : ton nom  
- **Marketing** : ton nom

### Sub-étape 1b — Bank Info
- **Bank country** : France  
- **Currency** : EUR  
- **IBAN** : ton IBAN perso (format FR76...)  
- **SWIFT/BIC** : celui de ta banque (tu le trouves sur un RIB)  
- **Account holder name** : ton nom tel qu'à la banque

Apple fait une vérification (48-72h).

### Sub-étape 1c — Tax Forms

**Domicile Fiscal** : tu en as besoin pour chaque "territory" où tu veux vendre. Le minimum c'est le W-8BEN (US) qui débloque tous les autres pays.

**W-8BEN (US Tax)** :
- Type : **Individual**  
- Country of citizenship : **France**  
- Permanent address : ton adresse perso  
- Country of tax residence : **France**  
- **FTIN (Foreign Tax Identifying Number)** : ton numéro fiscal français (13 chiffres, à récupérer sur impots.gouv.fr si tu ne l'as pas)  
- Reference number : vide  
- Date of birth : ta date de naissance  
- **Claim of Tax Treaty Benefits** :
  - Resident of **France**
  - Special rate (si demandé) : **0%**
  - Type of income : **Royalties** (Article 12 du traité France-US)
- Signature : ton nom, date du jour

**Canada / Japan / Australia Tax Info** : peut être sauté au début (ça ne bloque que la vente dans ces pays — tu les activeras plus tard).

✅ **Résultat attendu** : le Paid Apps Agreement passe en status **"Active"** après 24-48h. À partir de ce moment, tu peux créer des IAP.

---

## Étape 2 — Créer les 7 produits IAP

**Où** : App Store Connect → Mon App "Swing & Snap" → **Monetization** → **In-App Purchases** → **"+"**

Tu vas créer **7 produits** (3 consumables + 4 non-consumables). Pour chacun :

### Comment remplir chaque produit

| Champ | Valeur |
|---|---|
| **Type** | Consumable OU Non-consumable (voir tableau ci-dessous) |
| **Reference Name** | Nom interne (pas visible par l'utilisateur) |
| **Product ID** | Identifiant UNIQUE, ne pourra plus être changé |
| **Price** | Sélectionne un tier de prix |
| **Display Name (FR)** | Ce que l'utilisateur voit |
| **Description (FR)** | Courte description (10-45 car. recommandés) |
| **Review Screenshot** | 1 screenshot de l'écran "Packs" de ton app montrant le produit |

### Tableau des 7 produits

| Product ID | Type | Prix (FR) | Display Name FR | Description FR |
|---|---|---|---|---|
| `noads` | **Non-consumable** | 2,99 € | Sans pub | Supprime toutes les publicités du jeu |
| `gems1` | **Consumable** | 0,99 € | 500 gemmes | Obtiens 500 gemmes instantanément |
| `gems2` | **Consumable** | 2,99 € | 1200 gemmes | Obtiens 1200 gemmes instantanément |
| `gems3` | **Consumable** | 4,99 € | 3000 gemmes | Obtiens 3000 gemmes instantanément |
| `starter` | **Non-consumable** | 1,99 € | Pack Starter | Balle, traînée et fond Étoile exclusifs |
| `cosmic` | **Non-consumable** | 3,49 € | Pack Cosmic | Balle, traînée et fond Supernova exclusifs |
| `ultimate` | **Non-consumable** | 4,99 € | Pack Ultimate | Balle, traînée et fond Galaxy exclusifs |

⚠️ **Les Product IDs doivent être exactement ceux-ci** — le code de l'app est hardcodé sur ces strings. Si tu changes un ID, le produit n'apparaîtra pas dans l'app.

### Price tiers Apple (équivalent €)

Apple utilise des "tiers" mondiaux. Voici les correspondances approximatives (les autres monnaies sont calculées automatiquement) :

| Tier | Prix FR |
|---|---|
| Tier 1 | 0,99 € |
| Tier 2 | 1,99 € |
| Tier 3 | 2,99 € |
| Tier 4 | 3,99 € |
| Tier 5 | 4,99 € |

Pour `cosmic` à 3,49 € il n'y a pas de tier exact — utilise **Tier 4 (3,99 €)** ou change ton prix à 3,99 €. Simplification recommandée : mets `cosmic` à **3,99 €** aussi, ou à **2,99 €** si tu préfères garder un écart avec ultimate.

### Review Screenshot (obligatoire)
- Dimensions : **640×920** minimum
- Une screenshot de l'écran Packs de l'app où on voit le bouton du produit
- Tu peux utiliser l'une de celles déjà générées dans `store/appstore/iphone-6.9/fr/` et la cropper

### Cleared for Sale
- **Availability** : coche tous les pays (ou au moins FR + US + EU)
- **Status** : après avoir rempli tout le produit, clique sur **"Save"** → l'IAP passe en **"Ready to Submit"**

✅ **Résultat attendu** : 7 IAP en status "Ready to Submit" dans la liste.

---

## Étape 3 — Tester en sandbox

**Avant d'uploader la vraie build** tu dois tester les IAP en mode sandbox.

### Créer un Sandbox Tester
1. App Store Connect → **Users and Access** → **Sandbox Testers** → **"+"**
2. Crée un email bidon (ex: `test+rougon@gmail.com`) avec un mot de passe
3. Country : France
4. ⚠️ **Ne te connecte JAMAIS avec ce compte sur l'App Store prod** — réservé au sandbox

### Se connecter sur l'iPhone de test
1. Sur l'iPhone → **Réglages** → **App Store** → déconnexion du compte normal
2. Ouvre l'app via Xcode ou TestFlight
3. Quand tu déclenches un achat IAP, iOS te demandera de te logger — utilise le compte sandbox
4. Les achats sandbox sont gratuits (pas de vrai débit)

---

## Étape 4 — Soumettre les IAP avec la build

Quand tu soumets la version 1.0 de l'app à Apple pour review :
1. Dans la fiche de version → **In-App Purchases** → **"+"** → sélectionne les 7 IAP
2. Ils seront reviewés **en même temps** que ta build
3. Apple peut refuser un IAP si :
   - Le Review Screenshot n'est pas clair
   - La Description est trompeuse
   - Le produit n'est pas accessible depuis l'app

---

## Récap des blocages possibles

| Problème | Cause | Solution |
|---|---|---|
| Onglet "In-App Purchases" grisé | Paid Apps Agreement pas actif | Retourne à l'Étape 1, attends 48h |
| IAP refusés à la review | Description/Screenshot pas clair | Corrige et resoumets |
| Produit invisible dans l'app | Product ID mal écrit | Vérifie que l'ID Apple matche exactement celui dans `www/iap.js` |
| "Cannot connect to iTunes Store" en sandbox | Compte sandbox mal configuré | Déconnecte-toi du compte prod d'abord |

---

## Checklist complète

- [ ] Paid Apps Agreement signé
- [ ] Contact Info rempli
- [ ] Bank Info : IBAN + SWIFT rempli
- [ ] W-8BEN rempli avec numéro fiscal français
- [ ] Agreement passé en status "Active" (vérifier dans Business → Agreements)
- [ ] 7 IAP créés avec les Product IDs exacts (`noads`, `gems1`, `gems2`, `gems3`, `starter`, `cosmic`, `ultimate`)
- [ ] Review screenshots uploadés pour chacun
- [ ] Sandbox tester créé
- [ ] IAP ajoutés à la version 1.0 de l'app pour review
