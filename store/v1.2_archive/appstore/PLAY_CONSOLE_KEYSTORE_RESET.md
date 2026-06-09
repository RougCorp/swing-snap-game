# Google Play Console — Reset de la clé d'upload

## Pourquoi ?

Google Play a enregistré un certificat (`SHA1 EC:24:33:14:...`) qui ne correspond à aucun keystore présent sur ce Mac. Ton keystore actuel (`swingwnap.jks`, `SHA1 FD:3D:FB:1C:...`) est différent. Il faut demander à Google de réinitialiser la clé d'upload pour accepter le nouveau.

## Prérequis : Play App Signing activé

Cette procédure ne fonctionne **QUE** si Play App Signing est activé sur ton app (activé par défaut pour toutes les nouvelles apps depuis août 2021).

**Pour vérifier :**
1. Play Console → Swing & Snap
2. Menu gauche → **Configuration** → **Intégrité de l'application**
3. Onglet **"Signature de l'application"**
4. Tu dois voir une section "Clé d'application" avec un certificat géré par Google

Si tu vois "Play App Signing non activé" → la procédure est différente et plus compliquée. Envoie-moi une capture de cette page si c'est le cas.

---

## Étape 1 — Générer le certificat upload depuis ton keystore

Ouvre **Terminal** et copie-colle cette commande :

```bash
JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home" \
"$JAVA_HOME/bin/keytool" \
  -export -rfc \
  -keystore /Users/rougon/Documents/CREAPP/swing-snap/keystore/swingwnap.jks \
  -alias swingsnap \
  -file /Users/rougon/Documents/CREAPP/swing-snap/keystore/upload_certificate.pem
```

Il te demandera le **mot de passe du keystore** (celui que tu utilises dans Android Studio pour signer).

Tape-le, appuie sur Entrée. Tu devrais voir :
```
Le certificat a été stocké dans le fichier </Users/rougon/.../upload_certificate.pem>
```

## Étape 2 — Vérifier l'empreinte du certificat généré

```bash
JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home" \
"$JAVA_HOME/bin/keytool" \
  -printcert -file /Users/rougon/Documents/CREAPP/swing-snap/keystore/upload_certificate.pem
```

Tu dois voir une empreinte SHA-1 qui commence par `FD:3D:FB:1C:75:90:BC:1D:2A:6D:59:D8:10:C7:EA:40:5F:95:E7:9C` — c'est celle que Play Console refusait dans le message d'erreur. **C'est normal — c'est ce qu'on veut envoyer à Google pour remplacer l'ancienne.**

## Étape 3 — Demander le reset sur Play Console

1. Va sur Play Console → Swing & Snap
2. Menu gauche → **Configuration** → **Intégrité de l'application**
3. Onglet **"Signature de l'application"**
4. Cherche la section **"Clé d'upload"** (en bas)
5. Clique sur **"Demander la réinitialisation de la clé d'upload"** (ou "Request upload key reset")

Un formulaire Google s'ouvre. Remplis-le :

- **Raison** : choisis *"J'ai perdu ou supprimé ma clé d'upload"* (Lost or deleted upload key)
- **Message** (en anglais recommandé) :
  ```
  Hello,

  I have lost access to my original upload keystore. I am requesting to reset
  my upload key to a new one. I have the new keystore ready (SHA-1 fingerprint:
  FD:3D:FB:1C:75:90:BC:1D:2A:6D:59:D8:10:C7:EA:40:5F:95:E7:9C) and I am attaching
  the corresponding .pem certificate to this request.

  Thank you.
  ```
- **Fichier du nouveau certificat** : upload le fichier `upload_certificate.pem` généré à l'étape 1
  - Chemin : `/Users/rougon/Documents/CREAPP/swing-snap/keystore/upload_certificate.pem`

6. Envoie le formulaire.

## Étape 4 — Attendre la validation Google

- **Délai** : 1 à 2 jours ouvrés (parfois 2h seulement)
- Tu recevras un email de `noreply-play-developer@google.com` une fois la clé réinitialisée
- Après ça, tu pourras uploader ton `app-release.aab` sans le message d'erreur

---

## Et en attendant ?

Pendant que Google valide, tu peux :
1. **Continuer à préparer la fiche Play Console** : description, captures, classification, data safety → tout sauf l'upload du bundle
2. **Avancer sur l'App Store** en parallèle — ça n'a rien à voir avec ton keystore Android
3. **Finaliser la privacy policy** en activant GitHub Pages

---

## Alternative : créer une nouvelle app

Si tu n'as pas envie d'attendre 48h, tu peux :
1. Créer une **nouvelle app** Play Console avec un package name légèrement différent (ex: `com.rougcorp.swingandsnap2`)
2. Modifier `applicationId` dans `android/app/build.gradle`
3. Rebuilder un .aab qui ne rentrera en conflit avec rien
4. ⚠️ Tu perdras tout le travail déjà fait sur la fiche actuelle

**Ma reco : attends les 48h.** Le reset est la solution propre.
