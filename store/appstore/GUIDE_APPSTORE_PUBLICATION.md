# Guide complet — Publication sur l'App Store (Swing & Snap)

Ce guide couvre **tout** ce qu'il faut faire sur App Store Connect pour publier Swing & Snap, de l'archive Xcode jusqu'à la mise en ligne. À faire dans l'ordre.

---

## Pré-requis avant de commencer

- [ ] Xcode à jour (≥ 15)
- [ ] Paid Apps Agreement signé et en status "Active" (voir `IAP_APPSTORE.md`)
- [ ] 7 IAP créés et en status "Ready to Submit" (voir `IAP_APPSTORE.md`)
- [ ] GitHub Pages activé avec la Privacy Policy publique
- [ ] Captures d'écran iPhone + iPad prêtes (voir dossiers `iphone-6.9/`, `ipad-13/`)

---

## Étape 1 — Archiver et uploader depuis Xcode

### 1a. Ouvrir le workspace
```
Finder → swing-snap/ios/App/ → double-clic sur App.xcworkspace
```
⚠️ Toujours ouvrir `App.xcworkspace`, jamais `App.xcodeproj`.

### 1b. Sélectionner la cible de build
- En haut à gauche de Xcode : sélectionne **"Any iOS Device (arm64)"** (pas un simulateur)
- Si tu branches ton iPhone, tu peux le choisir — mais pour uploader, "Any iOS Device" suffit

### 1c. Vérifier le numéro de version
- Clique sur **App** dans le Project Navigator (gauche)
- Onglet **General** → **Identity**
  - **Version** : `1.0` (ce qui apparaît dans l'App Store)
  - **Build** : `1` (incrémenter à chaque upload, ex. 1, 2, 3…)

### 1d. Archiver
```
Menu Xcode → Product → Archive
```
Ça prend 2-5 minutes. Une fenêtre "Organizer" s'ouvre automatiquement.

### 1e. Uploader sur App Store Connect
Dans l'Organizer :
1. Sélectionne l'archive → **"Distribute App"**
2. Méthode : **"App Store Connect"**
3. Distribution : **"Upload"** (pas Export)
4. Options :
   - ✅ Include bitcode for iOS content
   - ✅ Upload your app's symbols
   - ✅ Manage Version and Build Number (laisse Xcode gérer)
5. Signe avec ton **Distribution Certificate** + **App Store Provisioning Profile**
6. **"Upload"** → attendre 2-5 min

✅ Résultat : la build apparaît dans App Store Connect → TestFlight (et aussi dans "Builds" lors de la soumission)

---

## Étape 2 — Créer la fiche de l'app sur App Store Connect

**Où** : appstoreconnect.apple.com → Swing & Snap → **App Store** → **1.0 Prepare for Submission**

### 2a. App Information (une seule fois, pas par version)

**Où** : onglet **"App Information"** dans la sidebar gauche

| Champ | Valeur |
|---|---|
| **Name** | Swing & Snap |
| **Subtitle** | Snap the rope, beat the score |
| **Primary Category** | Games → Action |
| **Secondary Category** | Games → Casual |
| **Content Rights** | ✅ "This app does not use third-party content" |
| **Age Rating** | 4+ (rempli via questionnaire — voir ci-dessous) |
| **Privacy Policy URL** | `https://<ton-user>.github.io/swing-snap/privacy.html` |

### 2b. Pricing and Availability

**Où** : onglet **"Pricing and Availability"**

| Champ | Valeur |
|---|---|
| **Price** | Free (0,00 €) |
| **Availability** | All countries and regions (ou sélectionne FR+EU+US pour commencer) |
| **Pre-order** | No |

### 2c. App Privacy (questionnaire de données)

**Où** : onglet **"App Privacy"** → **"Get Started"**

#### Question 1 : Collectez-vous des données ?
→ **YES** (AdMob collecte des données)

#### Question 2 : Types de données collectées

**Identifiers**
- [x] **Device ID**
  - Purpose : Third-Party Advertising
  - Linked to user : **No**
  - Used for tracking : **Yes**

**Usage Data**
- [x] **Product Interaction** (clics sur les pubs)
  - Purpose : Third-Party Advertising, Analytics
  - Linked to user : **No**
  - Used for tracking : **Yes**

**Diagnostics** (optionnel, seulement si tu as un crash reporter)
- [ ] Crash Data → laisse décoché si pas de Firebase Crashlytics

**Financial Info**
- ❌ **Ne coche PAS** "Purchase History" ici
  - Apple gère ça via StoreKit en interne, tu n'as pas accès à ces données
  - C'est uniquement requis si TOI tu stockes l'historique d'achats sur un serveur

**Tout le reste : ne coche pas**
- Location ❌, Contact Info ❌, Health ❌, Contacts ❌, Messages ❌

→ **Save** → **Publish**

---

## Étape 3 — Remplir la fiche de version (1.0)

**Où** : App Store Connect → Swing & Snap → **App Store** → **Version 1.0**

### 3a. Screenshots (OBLIGATOIRE)

Apple exige des screenshots pour chaque taille déclarée. Tu as besoin de :

| Taille | Dossier | Requis |
|---|---|---|
| iPhone 6.9" (iPhone 15 Pro Max) | `store/appstore/iphone-6.9/` | ✅ OBLIGATOIRE |
| iPad 13" Pro | `store/appstore/ipad-13/` | Si tu veux distribuer sur iPad |

**Comment uploader** :
1. Clique sur **"iPhone 6.9" Display"** dans la sidebar
2. Drag & drop les fichiers PNG depuis `iphone-6.9/fr/` (commence par FR)
3. Ordonne les screenshots en glissant-déposant (du plus accrocheur en premier)
4. Répète pour chaque langue (FR, EN, DE, ES, IT, PT, NL)
5. Pour iPad : même chose depuis `ipad-13/fr/`

⚠️ **Les noms de fichiers n'ont pas d'importance**, seule la taille compte.

### 3b. Description

**Promotional Text** (170 char max, peut être changé sans nouvelle review) :
```
🎮 Nouveau jeu de réflexes ! Attrape la corde, vise, lâche au bon moment. Gratuit et sans abonnement.
```

**Description** (4000 char max) :
```
Swing & Snap est un jeu de réflexes addictif où chaque milliseconde compte !

🎯 LE PRINCIPE
Touche l'écran pour lâcher la corde et propulser ta balle vers l'accroche suivante. Vise le point vert, enchaîne les pivots, bats ton record !

⚡ CARACTÉRISTIQUES
• Gameplay one-tap ultra intuitif
• Vitesse progressive — ça s'accélère !
• Des dizaines de skins, traînées et fonds à débloquer
• Missions quotidiennes et défis de progression
• Classement personnel et statistiques détaillées
• Mode sans pub disponible

💎 BOUTIQUE
Débloque des skins exclusifs et des packs de gemmes pour personnaliser ton expérience. Aucun abonnement — achat unique.

🌍 Disponible en 19 langues.
Joue, bats ton record, partage ton score !
```

**Keywords** (100 char max, séparés par virgules) :
```
jeu,reflex,arcade,corde,swing,addictif,score,skins,gratuit,casual
```

**Support URL** :
```
https://<ton-user>.github.io/swing-snap/
```

**Marketing URL** (optionnel) :
```
https://<ton-user>.github.io/swing-snap/
```

### 3c. Build

1. Clique sur **"+ Add Build"** sous la section Build
2. Sélectionne la build uploadée depuis Xcode (numéro de build 1)
3. Si elle n'apparaît pas, attends 10-15 min (traitement Apple)

### 3d. Age Rating

1. Clique **"Edit"** à côté d'Age Rating
2. Réponds au questionnaire IARC :
   - Violence : **None**
   - Contenu sexuel : **None**
   - Grossièretés : **None**
   - Drogues/Alcool : **None**
   - Jeux de hasard simulés : **None** ← important (tes packs ne sont pas des lootboxes)
   - Horreur : **None**
   - Contenu médical : **None**
   - Contenu généré par les utilisateurs : **None**
   - Publicités : **Yes** (AdMob)
   - Achats numériques : **Yes** (IAP)
3. Résultat attendu : **4+**

### 3e. Copyright

```
© 2025 RougCorp
```

### 3f. In-App Purchases

1. Clique sur **"+"** à droite de "In-App Purchases"
2. Sélectionne les 7 IAP que tu as créés
3. Ils doivent tous être en status "Ready to Submit"

### 3g. Review Information

| Champ | Valeur |
|---|---|
| **First Name** | Ton prénom |
| **Last Name** | Ton nom |
| **Phone** | Ton numéro |
| **Email** | Ton email |
| **Demo Account** | Laisse vide (pas de login dans le jeu) |
| **Notes for reviewer** | "No account needed. Tap the PACKS button on the main menu to access in-app purchases. For IAP testing, the purchase flow uses StoreKit sandbox. Ad banners appear during gameplay." |

### 3h. Version Release

- **Automatically release this version** ← recommandé pour la v1.0
  (ça se publie dès que la review est acceptée, sans action de ta part)

---

## Étape 4 — Soumettre pour review

1. Clique **"Add for Review"** en haut à droite
2. Vérifie la checklist qu'Apple affiche (tout doit être vert)
3. Clique **"Submit to App Review"**

⏱️ **Délai de review** : 24-48h pour la v1.0. Tu recevras un email quand c'est approuvé (ou si refusé avec les raisons).

---

## Étape 5 — Après la review

### Si approuvée ✅
- L'app est en ligne (si tu avais choisi "Automatically release")
- Vérifie la fiche sur l'App Store depuis ton iPhone
- Teste un achat en sandbox (avec le compte sandbox que tu as créé)

### Si refusée ❌
Les raisons les plus fréquentes pour une v1.0 avec IAP :
| Raison | Solution |
|---|---|
| Screenshot IAP pas visible | Refaire les screenshots en montrant l'écran Packs |
| ATT pop-up non implémentée | Vérifier que AdMob déclenche la demande d'autorisation |
| Privacy Policy URL inaccessible | Vérifier que GitHub Pages est bien activé |
| IAP pas accessible depuis l'app | Vérifier que le bouton PACKS est visible sur le menu |
| Description IAP pas claire | Préciser dans les notes reviewer comment accéder aux IAP |

---

## Checklist finale avant soumission

### App Store Connect
- [ ] Paid Apps Agreement en status "Active"
- [ ] Privacy Policy URL accessible publiquement
- [ ] 7 IAP en status "Ready to Submit"
- [ ] Screenshots iPhone 6.9" uploadées (toutes langues)
- [ ] Screenshots iPad 13" uploadées (si distribué sur iPad)
- [ ] Description remplie (FR + EN minimum)
- [ ] Keywords remplis
- [ ] Age Rating : 4+
- [ ] Build uploadée et sélectionnée
- [ ] Review Information remplie avec notes
- [ ] IAP ajoutés à la version

### Xcode / Code
- [ ] `Info.plist` contient `ITSAppUsesNonExemptEncryption = false`
- [ ] Bundle ID correspond à celui créé sur App Store Connect
- [ ] Version = 1.0, Build = 1
- [ ] Distribution Certificate + App Store Provisioning Profile valides

### Test avant soumission
- [ ] L'app tourne sans crash sur un vrai iPhone
- [ ] Le bouton PACKS est visible et ouvre l'écran des achats
- [ ] En sandbox, cliquer sur un pack déclenche la sheet iOS
- [ ] Le bouton "Restaurer mes achats" fonctionne
- [ ] Les pubs AdMob s'affichent (en mode test)
- [ ] ATT pop-up apparaît au premier lancement

---

## Rappel : URLs à adapter

Remplace `<ton-user>` par ton username GitHub partout :
- Privacy Policy : `https://<ton-user>.github.io/swing-snap/privacy.html`
- Support URL : `https://<ton-user>.github.io/swing-snap/`
