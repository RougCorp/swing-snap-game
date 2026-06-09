# Xcode — Archive & Upload vers App Store Connect

Ces étapes ne peuvent être faites que par toi manuellement dans Xcode (je ne peux pas piloter Xcode depuis le terminal de façon fiable).

## Prérequis vérifiés ✅

- [x] Compte Apple Developer actif (Team ID : `6JMPGGJ966`)
- [x] Xcode installé
- [x] Projet iOS existant (`ios/App/App.xcworkspace`)
- [x] Bundle ID configuré (`com.rougcorp.swingsnap`)
- [x] Version bumped à `1.0.1` (build `2`)
- [x] `npx cap sync ios` effectué — les derniers assets web sont dedans
- [x] `ITSAppUsesNonExemptEncryption = false` ajouté dans Info.plist

---

## Étape 1 — Ouvrir le projet Xcode

⚠️ **Ouvre toujours le `.xcworkspace`, jamais le `.xcodeproj`** (à cause de CocoaPods).

```bash
open /Users/rougon/Documents/CREAPP/swing-snap/ios/App/App.xcworkspace
```

## Étape 2 — Vérifier la configuration de signing

1. Dans Xcode, sélectionne le target **"App"** dans la liste de gauche
2. Onglet **"Signing & Capabilities"**
3. Vérifie que :
   - **Automatically manage signing** est coché ✅
   - **Team** : `Arthur Rougon (6JMPGGJ966)`
   - **Bundle Identifier** : `com.rougcorp.swingsnap`
   - **Provisioning Profile** : créé automatiquement par Xcode (pas de message rouge)

Si tu vois une erreur rouge "Failed to register bundle identifier", clique sur "Try Again" ou va sur [developer.apple.com](https://developer.apple.com/account/resources/identifiers/list) pour créer l'App ID manuellement avec l'ID `com.rougcorp.swingsnap`.

## Étape 3 — Sélectionner la destination "Any iOS Device (arm64)"

En haut de Xcode, à côté du bouton Play ▶️, il y a un sélecteur de device. Clique dessus et choisis :

**Any iOS Device (arm64)**

⚠️ **Indispensable** — si tu laisses un simulateur sélectionné, l'option "Archive" sera grisée.

## Étape 4 — Archiver

Menu : **Product → Archive**

L'archivage prend 2 à 5 minutes selon ta machine. Une fois terminé, la fenêtre **Organizer** s'ouvre automatiquement et affiche ton archive.

Si tu vois une erreur "pod install" ou "Swift version", ferme Xcode et relance :
```bash
cd /Users/rougon/Documents/CREAPP/swing-snap/ios/App
pod install
open App.xcworkspace
```

## Étape 5 — Distribuer l'archive

Dans la fenêtre **Organizer** qui vient de s'ouvrir :

1. Sélectionne l'archive `Swing & Snap 1.0.1 (2)` qu'on vient de créer
2. Clique sur **"Distribute App"** (à droite)
3. Sélectionne **"App Store Connect"** → Next
4. Sélectionne **"Upload"** → Next
5. Options de distribution :
   - [x] Upload your app's symbols to receive symbolicated reports from Apple
   - [x] Manage Version and Build Number (Xcode auto-increment)
   - → Next
6. Signing : **Automatically manage signing** → Next
7. Xcode prépare l'upload, affiche un résumé → **Upload**

L'upload prend 5 à 15 minutes. Tu verras une fenêtre de progression.

## Étape 6 — Après upload

Une fois l'upload terminé :

1. Va sur [App Store Connect](https://appstoreconnect.apple.com)
2. Mon App → Swing & Snap → **TestFlight**
3. La build apparaîtra dans la liste après ~10-20 minutes avec le statut "Processing"
4. Quand le statut passe à "Ready to Submit", tu peux :
   - Soit la pousser en **TestFlight externe** pour tester
   - Soit la sélectionner dans l'onglet **"App Store"** pour la soumettre à review

## Étape 7 — Soumission pour review

Dans App Store Connect :

1. Onglet **"Distribution"** → **"App Store"**
2. Clique sur la version "1.0.1 Prepare for Submission"
3. Remplis :
   - **Description, Keywords, Subtitle** → copie depuis `store/appstore/METADATA.md`
   - **Captures** → upload depuis `store/appstore/iphone-6.9/` (et/ou `iphone-6.7/`)
   - **Build** → sélectionne la build que tu viens d'uploader
   - **App Icon** → automatique depuis le projet Xcode
   - **Copyright** → `© 2026 RougCorp`
   - **Category** → Games > Arcade (primary), Games > Casual (secondary)
   - **Age Rating** → réponds 4+ (voir `PRIVACY_QUESTIONNAIRE.md`)
   - **App Privacy** → voir `PRIVACY_QUESTIONNAIRE.md`
   - **Privacy Policy URL** → l'URL publique de ta privacy policy (GitHub Pages)
4. En haut à droite : **"Add for Review"** puis **"Submit for Review"**

Review Apple : 24h à 48h en général.

---

## Problèmes fréquents

### "No account for team 6JMPGGJ966"
→ Xcode → Settings → Accounts → ajoute ton Apple ID

### "Provisioning profile doesn't include device"
→ Normal en "Any iOS Device", ignore

### Upload échoue avec "ITMS-90XXX"
→ Lis l'erreur exacte et envoie-la-moi, ces erreurs sont très spécifiques

### Build coincée en "Processing" > 1h
→ Attends 2-3h. Si vraiment bloquée, re-archive avec un build number incrémenté
