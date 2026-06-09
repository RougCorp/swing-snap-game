# App Store Privacy — Réponses au questionnaire

Dans App Store Connect → App Privacy → **"Get Started"**, Apple te posera une série de questions. Voici les réponses pour Swing & Snap (qui utilise **Google AdMob**).

## 1. Do you or your third-party partners collect data from this app?

**Réponse : YES** ✅
(Parce qu'AdMob collecte des données pour la publicité)

---

## 2. Quels types de données sont collectées ?

Coche les cases suivantes (dues à AdMob) :

### Identifiers
- [x] **Device ID** (IDFA via AdMob)
  - Usage : Third-Party Advertising
  - Linked to user : **NO**
  - Tracking : **YES**

### Usage Data
- [x] **Product Interaction** (AdMob ads shown / clicked)
  - Usage : Third-Party Advertising, Analytics
  - Linked to user : **NO**
  - Tracking : **YES**

### Diagnostics
- [x] **Crash Data** (si tu ajoutes un crash reporter)
  - Usage : App Functionality
  - Linked to user : **NO**
  - Tracking : **NO**
- [x] **Performance Data**
  - Usage : App Functionality
  - Linked to user : **NO**
  - Tracking : **NO**

**Tu ne collectes PAS** :
- Location ❌
- Contact Info ❌
- User Content ❌
- Browsing History ❌
- Search History ❌
- Health & Fitness ❌
- **Financial Info / Purchase History ❌** ← Apple gère ça via StoreKit en interne.
  Tu n'as pas accès à l'historique d'achats — ne coche PAS cette case sur Apple.
  (Google Play : à déclarer dans Data Safety — voir `IAP_PLAYCONSOLE.md`)
- Sensitive Info ❌
- Contacts ❌
- Other Data ❌

---

## 3. App Tracking Transparency (ATT)

Parce qu'AdMob est intégré, **tu dois afficher la demande ATT** au premier lancement (iOS 14.5+).

Le fichier `Info.plist` contient déjà :
```xml
<key>NSUserTrackingUsageDescription</key>
<string>This allows us to show you more relevant ads.</string>
```

Tu peux personnaliser ce texte pour qu'il soit plus convaincant, par exemple :
```
We use your device identifier to show more relevant ads and keep Swing & Snap free.
```

**Vérifie dans ton code** que `AdMob.trackingAuthorizationStatus()` ou équivalent est bien appelé au démarrage pour déclencher la pop-up ATT. Sans ça, Apple peut rejeter l'app.

---

## 4. Privacy Policy URL

App Store Connect exige une URL de politique de confidentialité publique. Tu en as déjà une dans `docs/privacy.html`.

**Action requise :** active GitHub Pages pour rendre cette URL publique, puis colle l'URL dans App Store Connect → App Information → Privacy Policy URL.

URL attendue (à adapter selon ton username GitHub) :
```
https://<ton-user>.github.io/swing-snap/privacy.html
```

---

## 5. Rating / Age classification

- **Violence** : None
- **Sexual content** : None
- **Profanity** : None
- **Drug/Alcohol** : None
- **Gambling** : None (même si ton jeu a un système "packs", ce ne sont pas des loot boxes aléatoires)
- **Horror/Fear** : None
- **Medical info** : None
- **User-generated content** : None
- **Advertising** : **Yes** (via AdMob)

Résultat attendu : **4+** (tous âges)

---

## 6. Export Compliance (ITSAppUsesNonExemptEncryption)

Pour éviter que chaque upload te demande de remplir le formulaire d'export :

**Ajoute ceci à `ios/App/App/Info.plist`** (juste avant `</dict>`) :
```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

Ton app n'utilise pas de cryptographie custom — seulement HTTPS standard, qui est exempté.
