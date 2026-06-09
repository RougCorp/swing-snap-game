# Google Play Console — Configuration des In-App Purchases

Ce document couvre tout ce qu'il faut faire **côté Google Play Console** pour activer les achats intégrés. À faire en parallèle pendant que Claude écrit le code.

⚠️ **Ordre important** : le **compte marchand Google Payments** doit être créé en premier, sinon l'onglet "In-app products" reste bloqué.

---

## Étape 1 — Créer un compte marchand Google Payments (~20 min)

1. Play Console → sélectionne l'app **Swing & Snap** (ou crée-la si pas encore fait)
2. Menu gauche → **Monetize** → **Monetization setup**
3. Clique sur **"Set up a merchant account"** → ça ouvre `payments.google.com/merchant`

### Sub-étape 1a — Infos du compte marchand

- **Business name** : ton nom (ou "RougCorp" si tu veux un nom plus pro — pas besoin d'être déposé)
- **Country** : France
- **Contact email** : ton email
- **Account type** : **Individual** (pas d'entreprise)
- **Legal name** : ton nom complet
- **Address** : ton adresse perso (chez tes parents OK)
- **Phone** : ton numéro FR
- **Date of birth** : ta date de naissance

### Sub-étape 1b — Tax info

- **Tax residency** : France
- **Tax Identification Number (TIN)** : ton numéro fiscal français (13 chiffres)
- **Are you a US person?** : **No**
- **Activity performed in the US?** : **No** (tu développes depuis la France)
- **Tax treaty claim** : **Yes**, France, **0%** withholding sur royalties

### Sub-étape 1c — Bank Info

- **Bank country** : France
- **Currency** : EUR
- **IBAN** : ton IBAN perso (format FR76...)
- **SWIFT/BIC** : celui de ta banque (RIB)
- **Account holder name** : ton nom exact tel qu'à la banque
- Google Payments fait une **micro-vérification** (1-3 jours) en envoyant un petit montant sur ton compte, que tu devras confirmer. Surveille ton app bancaire.

✅ **Résultat attendu** : compte marchand en status **"Active"** après 24-72h. L'onglet "In-app products" de Play Console devient accessible.

---

## Étape 2 — Activer la monétisation sur l'app

1. Retour Play Console → **Swing & Snap** → **Monetize** → **Monetization setup**
2. Vérifie que **"Merchant account"** est bien lié (status vert)
3. Clique sur **Google Play Billing** → **"Add"** pour l'activer sur l'app
4. Retour à gauche → **Products** → **In-app products** (maintenant déverrouillé)

---

## Étape 3 — Créer les 7 produits IAP

**Où** : Play Console → **Swing & Snap** → **Monetize** → **Products** → **In-app products** → **"Create product"**

Tu vas créer **7 produits**. Google ne distingue pas Consumable/Non-consumable à la création (c'est géré côté code : l'app consomme ou pas l'achat après). Tous se créent de la même façon.

### Champs pour chaque produit

| Champ | Valeur |
|---|---|
| **Product ID** | Identifiant unique, impossible à changer après création |
| **Name** | Nom affiché en boutique |
| **Description** | Courte description |
| **Default price** | Prix de base (en EUR) |

### Tableau des 7 produits

| Product ID | Nom (FR) | Description | Prix |
|---|---|---|---|
| `noads` | Sans pub | Supprime toutes les publicités du jeu | 2,99 € |
| `gems1` | 500 gemmes | Obtiens 500 gemmes instantanément | 0,99 € |
| `gems2` | 1200 gemmes | Obtiens 1200 gemmes instantanément | 2,99 € |
| `gems3` | 3000 gemmes | Obtiens 3000 gemmes instantanément | 4,99 € |
| `starter` | Pack Starter | Balle, traînée et fond Étoile exclusifs | 1,99 € |
| `cosmic` | Pack Cosmic | Balle, traînée et fond Supernova exclusifs | 3,49 € |
| `ultimate` | Pack Ultimate | Balle, traînée et fond Galaxy exclusifs | 4,99 € |

⚠️ **Les Product IDs doivent être exactement ceux-ci** — le code de l'app est hardcodé dessus. Contrairement à Apple, Google accepte 3,49 € pile (pas de tier obligatoire).

### Après la création de chaque produit

- Clique **"Save"** → le produit est en status **"Inactive"**
- Clique **"Activate"** → le produit passe en **"Active"**
- ⚠️ Tant qu'un produit n'est pas "Active", il ne peut pas être acheté, même en test

### Pricing automatique par pays
- Google génère automatiquement les prix localisés (USD, GBP, etc.) à partir du prix EUR
- Tu peux les override manuellement si tu veux, mais au début laisse faire

---

## Étape 4 — Licence testing (indispensable pour tester sans payer)

1. Play Console → **Settings** → **License testing** (en bas du menu gauche, sous "Developer account")
2. Ajoute ton adresse **Google** (celle que tu utilises sur l'appareil Android de test)
3. **License response** : laisse sur "RESPOND_NORMALLY"
4. Tu pourras maintenant faire des achats de test sans être facturé (la popup Google montrera "This is a test purchase")

---

## Étape 5 — Uploader une build dans un track fermé (indispensable)

⚠️ **Les IAP ne fonctionnent QUE si l'app est uploadée dans au moins un track** (closed testing, internal testing, ou production). Tu ne peux pas tester IAP depuis une build locale sans ça.

### Option la plus rapide : Internal testing
1. Play Console → **Testing** → **Internal testing**
2. **"Create new release"**
3. Upload ton `app-release.aab` (une fois que la clé d'upload est reset — voir `PLAY_CONSOLE_KEYSTORE_RESET.md`)
4. Ajoute ton compte Google dans la liste des testeurs
5. **Start rollout** → tu reçois un lien d'opt-in
6. Clique le lien sur ton tel Android → installe l'app → teste les IAP

Les IAP ne deviennent visibles dans l'app qu'après un délai de **~2h** après la première publication sur un track.

---

## Étape 6 — Soumettre en production

Quand tu soumets l'app en production :
1. Les 7 IAP "Active" dans le Play Console sont automatiquement disponibles
2. Google ne review pas les IAP séparément (contrairement à Apple)
3. Mais Google peut refuser l'app si les prix/descriptions enfreignent leurs politiques

---

## Récap des blocages possibles

| Problème | Cause | Solution |
|---|---|---|
| Onglet "In-app products" grisé | Merchant account pas actif | Retourne à l'Étape 1, attends validation bancaire |
| IAP pas visible dans l'app | Produit pas "Active" OU app pas dans un track | Étape 3 (activate) + Étape 5 (upload) |
| "Item not found" dans l'app | Product ID ne matche pas | Vérifie que l'ID Google matche exactement celui dans `www/iap.js` |
| "Authentification failed" en test | Pas dans la liste des license testers | Étape 4 |
| Délai après création | Normal | Attendre ~2h après le premier upload |

---

## Checklist complète

- [ ] Compte Google Payments créé en mode Individual
- [ ] Bank Info : IBAN + SWIFT + micro-transaction vérifiée
- [ ] Tax Info : TIN français rempli, treaty claim France 0%
- [ ] Merchant account en status "Active"
- [ ] Google Play Billing activé sur l'app
- [ ] 7 IAP créés avec les Product IDs exacts (`noads`, `gems1`, `gems2`, `gems3`, `starter`, `cosmic`, `ultimate`)
- [ ] Chaque IAP passé en status "Active"
- [ ] License testing activé pour ton compte Google
- [ ] Build uploadée dans Internal testing
- [ ] Attente ~2h avant premier test
