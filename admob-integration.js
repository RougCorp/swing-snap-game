// ============================================================
// ADMOB INTEGRATION - Swing & Snap
// ============================================================
// Ce fichier montre comment remplacer les confirm() par de vraies pubs.
// À intégrer dans votre index.html APRÈS avoir installé @capacitor-community/admob
//
// IMPORTANT: Les IDs ci-dessous sont des IDs DE TEST Google.
// Remplacez-les par vos vrais IDs une fois votre compte AdMob créé.
// ============================================================

// --- INITIALISATION (à appeler dans Game.init) ---
async function initAdMob() {
  try {
    const { AdMob } = await import('@capacitor-community/admob');
    
    await AdMob.initialize({
      // requestTrackingAuthorization: true,  // Décommenter pour iOS ATT
      // testingDevices: ['VOTRE_DEVICE_ID'],  // Pour le dev
    });
    
    window._admob = AdMob;
    console.log('AdMob initialisé ✅');
  } catch (e) {
    console.warn('AdMob non disponible (mode web?):', e);
  }
}

// --- PUB INTERSTITIELLE (entre les parties) ---
async function showInterstitial() {
  if (!window._admob) return;
  
  try {
    const { AdMob } = window._admob;
    await AdMob.prepareInterstitial({
      adId: 'ca-app-pub-3940256099942544/1033173712',  // ← ID DE TEST
      // adId: 'ca-app-pub-VOTRE_ID/VOTRE_AD_UNIT',    // ← Votre vrai ID
      isTesting: true
    });
    await AdMob.showInterstitial();
  } catch (e) {
    console.warn('Interstitial failed:', e);
  }
}

// --- PUB REWARDED (Revive + Double Gems) ---
// Retourne true si la pub a été vue en entier, false sinon
async function showRewardedAd() {
  if (!window._admob) {
    // Fallback pour le web (dev): simuler avec confirm
    return confirm("📺 Regarder une pub ?");
  }
  
  try {
    const { AdMob, RewardAdPluginEvents } = window._admob;
    
    return new Promise(async (resolve) => {
      // Écouter la récompense
      const listener = await AdMob.addListener(
        RewardAdPluginEvents.Rewarded,
        () => {
          listener.remove();
          resolve(true);
        }
      );
      
      // Écouter la fermeture sans récompense
      const dismissListener = await AdMob.addListener(
        RewardAdPluginEvents.Dismissed,
        () => {
          dismissListener.remove();
          resolve(false);
        }
      );
      
      await AdMob.prepareRewardVideoAd({
        adId: 'ca-app-pub-3940256099942544/5224354917',  // ← ID DE TEST
        // adId: 'ca-app-pub-VOTRE_ID/VOTRE_AD_UNIT',    // ← Votre vrai ID
        isTesting: true
      });
      
      await AdMob.showRewardVideoAd();
    });
  } catch (e) {
    console.warn('Rewarded ad failed:', e);
    return false;
  }
}

// ============================================================
// COMMENT INTÉGRER DANS LE JEU
// ============================================================
//
// 1. REVIVE - Remplacer le code actuel:
//    
//    AVANT:
//    if(confirm("📺 Pub pour Revive ?")){ ... }
//    
//    APRÈS:
//    const watched = await showRewardedAd();
//    if(watched) { ... }
//
// 2. DOUBLE GEMS - Même principe:
//    
//    AVANT:  
//    if(confirm("📺 Regarder une pub pour doubler vos gems ?")){ ... }
//    
//    APRÈS:
//    const watched = await showRewardedAd();
//    if(watched) { ... }
//
// 3. INTERSTITIELLE (entre les parties) - Dans gameOver():
//
//    AVANT:
//    if(ad) setTimeout(()=>showToast("📺 Publicité affichée"),500);
//    
//    APRÈS:
//    if(ad) setTimeout(()=>showInterstitial(),500);
//
// ============================================================
