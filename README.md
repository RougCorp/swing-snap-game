# 🎮 Swing & Snap - Version de Production

## 📦 Structure du Projet

Voici tous les fichiers nécessaires pour publier le jeu :

```
📁 Swing & Snap/
├── 🎮 swing_snap_production.html    ← Fichier principal du jeu
├── 📱 manifest.json                 ← Configuration PWA
├── ⚙️ sw.js                         ← Service Worker (mode hors ligne)
│
├── 🖼️ ICÔNES :
│   ├── favicon.ico                  ← Icône navigateur
│   ├── favicon-96x96.png            ← Icône navigateur haute résolution
│   ├── favicon.svg                  ← Icône vectorielle
│   ├── apple-touch-icon.png         ← Icône iOS (180x180)
│   ├── web-app-manifest-192x192.png ← Icône PWA petite (192x192)
│   ├── web-app-manifest-512x512.png ← Icône PWA grande (512x512)
│   └── preview.png                  ← Image de partage réseaux sociaux
│
└── 📖 GUIDE_PUBLICATION.md          ← Guide complet de publication
```

## 🚀 Démarrage Rapide

### Option 1 : Test Local
1. Double-cliquez sur `swing_snap_production.html`
2. Le jeu s'ouvre dans votre navigateur
3. Jouez et testez toutes les fonctionnalités !

### Option 2 : Serveur Local (Recommandé)
```bash
# Si vous avez Python installé :
python -m http.server 8000

# Ou avec Node.js :
npx serve

# Puis ouvrez : http://localhost:8000/swing_snap_production.html
```

## ✅ Checklist Avant Publication

### Tests
- [ ] Le jeu se charge sans erreur
- [ ] Gameplay fluide (60 FPS)
- [ ] Toutes les langues fonctionnent
- [ ] Les skins se débloquent
- [ ] Les missions progressent
- [ ] Le score se sauvegarde
- [ ] Testé sur Chrome, Safari, Firefox
- [ ] Testé sur mobile (iOS et Android)

### Configuration
- [ ] Remplacer les IDs AdMob dans le HTML (lignes ~250-252)
- [ ] Personnaliser la politique de confidentialité
- [ ] Mettre à jour les URLs dans les meta tags
- [ ] Ajouter votre nom dans `<meta name="author">`

### Images
- [✅] Icônes fournies et intégrées
- [✅] Preview pour réseaux sociaux créée
- [ ] Captures d'écran pour les stores (optionnel)

## 📱 Publication

### Web (GitHub Pages, Netlify, Vercel)
1. Upload tous les fichiers
2. Le jeu est prêt !
3. URL exemple : `https://votre-site.com/swing_snap_production.html`

### App Mobile (iOS/Android)
Suivez le **GUIDE_PUBLICATION.md** section 6 pour :
- Installer Capacitor
- Compiler pour iOS/Android
- Publier sur les stores

## 🎨 Personnalisation

### Couleurs du Thème
Dans le HTML, cherchez `:root` pour modifier :
```css
--accent: #8E63B4;  /* Violet principal */
--accent2: #7CB342; /* Vert secondaire */
--gold: #F4A926;    /* Or pour les gemmes */
```

### Langues
Le jeu supporte 20 langues :
- Français, Anglais, Espagnol, Allemand, Italien
- Portugais, Néerlandais, Hongrois, Polonais, Turc
- Japonais, Coréen, Chinois, Russe, Arabe
- Hindi, Suédois, Danois, Norvégien, Finnois

Pour ajouter une langue, éditez la section `I18N.L` dans le HTML.

## 📊 Analytics & Monétisation

### Google Analytics (Optionnel)
Voir GUIDE_PUBLICATION.md section 4

### AdMob (Pubs)
1. Créez un compte sur https://admob.google.com/
2. Créez 2 unités publicitaires (Interstitielle + Récompensée)
3. Remplacez les IDs dans le code :
```javascript
INTERSTITIAL_ID: 'ca-app-pub-VOTRE-ID/XXXXX',
REWARDED_ID: 'ca-app-pub-VOTRE-ID/XXXXX',
```

## 🆘 Problèmes Courants

**Le jeu ne se charge pas**
- Ouvrez la console (F12) pour voir les erreurs
- Vérifiez que tous les fichiers sont dans le même dossier

**Les icônes ne s'affichent pas**
- Vérifiez que les chemins dans le HTML correspondent aux noms de fichiers
- Pour tester localement, utilisez un serveur HTTP

**Les traductions ne fonctionnent pas**
- Vérifiez la console pour les erreurs JavaScript
- Le navigateur doit supporter ES6

## 📞 Support

Pour toute question, consultez :
- **GUIDE_PUBLICATION.md** - Guide complet étape par étape
- Console du navigateur (F12) - Pour voir les erreurs
- Documentation en ligne - Liens dans le guide

## 🎉 Félicitations !

Votre jeu est prêt pour la production !
Il ne vous reste plus qu'à :
1. Tester
2. Configurer AdMob (optionnel)
3. Publier

Bonne chance ! 🚀

---

**Version :** 1.0.0  
**Dernière mise à jour :** Février 2026  
**Compatibilité :** Chrome, Safari, Firefox, Edge (dernières versions)
