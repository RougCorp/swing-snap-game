/**
 * Swing & Snap — In-App Purchase wrapper
 *
 * Wraps cordova-plugin-purchase v13 (CdvPurchase) with a tiny API that the
 * rest of the game uses:
 *
 *   IAP.init(onDeliver)           — must be called once on app start.
 *                                    onDeliver(productId) is called by the
 *                                    plugin when a purchase is approved and
 *                                    we need to unlock the entitlement in the
 *                                    game (credit gems, flip noAds, unlock
 *                                    skin pack). Called on both fresh buys
 *                                    AND restored purchases.
 *   IAP.isNative()                — true on iOS/Android with plugin present.
 *   IAP.getPrice(productId)       — localized price string from the store
 *                                    (e.g. "2,99 €" or "$2.99"), or the
 *                                    hardcoded fallback when not available.
 *   IAP.isOwned(productId)        — true if the user owns this non-consumable.
 *   IAP.buy(productId)            — triggers the native payment sheet.
 *                                    Returns a promise that resolves once the
 *                                    transaction is approved (delivery is
 *                                    handled via the onDeliver callback).
 *   IAP.restore()                 — re-syncs non-consumable purchases from
 *                                    the store. Required by Apple.
 *   IAP.onReady(cb)               — fires once the store is initialized and
 *                                    prices are loaded.
 *
 * Product catalogue is declared here so only ONE file knows about the 7 IDs.
 */
(function (global) {
  'use strict';

  // --- Product catalogue ---------------------------------------------------
  // IDs MUST match what you create on App Store Connect + Play Console.
  // Types: 'consumable' for gem packs (can be bought multiple times),
  //        'non_consumable' for noads + skin packs (forever unlock).
  const CATALOG = [
    { id: 'noads',    type: 'non_consumable', fallback: '2,99 €' },
    { id: 'gems1',    type: 'consumable',     fallback: '0,99 €' },
    { id: 'gems2',    type: 'consumable',     fallback: '2,99 €' },
    { id: 'gems3',    type: 'consumable',     fallback: '4,99 €' },
    { id: 'starter',  type: 'non_consumable', fallback: '1,99 €' },
    { id: 'cosmic',   type: 'non_consumable', fallback: '3,49 €' },
    { id: 'ultimate', type: 'non_consumable', fallback: '4,99 €' },
    { id: 'eclipse',  type: 'non_consumable', fallback: '3,99 €' },
    { id: 'prism',    type: 'non_consumable', fallback: '4,49 €' },
  ];

  // --- State ---------------------------------------------------------------
  let store = null;              // CdvPurchase.store when native
  let platformType = null;       // CdvPurchase.Platform.* when native
  let productTypeMap = null;     // CdvPurchase.ProductType.* aliases
  let ready = false;
  let deliverCallback = null;    // set by IAP.init()
  const readyCallbacks = [];

  function log(...args) {
    try { console.log('[IAP]', ...args); } catch (e) {}
  }

  function fireReady() {
    if (ready) return;
    ready = true;
    log('ready');
    while (readyCallbacks.length) {
      try { readyCallbacks.shift()(); } catch (e) { log('ready cb error', e); }
    }
  }

  function deliver(productId) {
    if (!deliverCallback) {
      log('deliver called before init()', productId);
      return;
    }
    try { deliverCallback(productId); }
    catch (e) { log('deliver error', productId, e); }
  }

  // --- Detection -----------------------------------------------------------
  function hasNativePlugin() {
    return typeof global.CdvPurchase !== 'undefined'
        && global.CdvPurchase
        && global.CdvPurchase.store;
  }

  // --- Public API ----------------------------------------------------------
  const IAP = {
    isNative() { return hasNativePlugin(); },

    onReady(cb) {
      if (typeof cb !== 'function') return;
      if (ready) { cb(); return; }
      readyCallbacks.push(cb);
    },

    init(onDeliver) {
      deliverCallback = typeof onDeliver === 'function' ? onDeliver : null;

      if (!hasNativePlugin()) {
        log('native plugin not found — running in browser fallback mode');
        // In browser we're "ready" right away so the UI shows fallback prices.
        setTimeout(fireReady, 0);
        return;
      }

      const CdvPurchase = global.CdvPurchase;
      store = CdvPurchase.store;
      platformType = CdvPurchase.Platform;
      productTypeMap = {
        consumable: CdvPurchase.ProductType.CONSUMABLE,
        non_consumable: CdvPurchase.ProductType.NON_CONSUMABLE,
      };

      // Optional: log level
      try { store.verbosity = CdvPurchase.LogLevel.WARNING; } catch (e) {}

      // 1. Register every product for BOTH platforms. The plugin will only
      //    query the one relevant to the current device (APPLE_APPSTORE on
      //    iOS, GOOGLE_PLAY on Android). Registering both keeps the catalogue
      //    declared in one place.
      const toRegister = [];
      for (const p of CATALOG) {
        const pt = productTypeMap[p.type];
        toRegister.push({ id: p.id, type: pt, platform: platformType.APPLE_APPSTORE });
        toRegister.push({ id: p.id, type: pt, platform: platformType.GOOGLE_PLAY });
      }
      store.register(toRegister);

      // 2. Wire up event callbacks BEFORE calling initialize().
      store.when()
        .productUpdated(function (product) {
          log('product updated', product.id, product.pricing && product.pricing.price);
        })
        .approved(function (transaction) {
          // A purchase was approved by the store. Deliver the entitlement
          // and mark the transaction finished so iOS/Android stop pinging us.
          log('approved', transaction && transaction.products);
          try {
            if (transaction && Array.isArray(transaction.products)) {
              for (const entry of transaction.products) {
                if (entry && entry.id) deliver(entry.id);
              }
            }
          } finally {
            try { transaction.finish(); } catch (e) { log('finish error', e); }
          }
        })
        .finished(function (transaction) {
          log('finished', transaction && transaction.products);
        })
        .receiptUpdated(function (receipt) {
          log('receipt updated', receipt && receipt.platform);
        });

      store.error(function (err) {
        log('error', err && err.code, err && err.message);
      });

      // 3. Initialize with both platforms — the plugin picks the right one
      //    at runtime based on the OS.
      store.initialize([
        platformType.APPLE_APPSTORE,
        platformType.GOOGLE_PLAY,
      ]).then(function (errors) {
        if (errors && errors.length) {
          for (const e of errors) log('init error', e.code, e.message);
        }
        log('initialized');
        // Ready fires once products are loaded. The plugin guarantees at
        // least one update tick after initialize, even on error.
        fireReady();
      }).catch(function (e) {
        log('initialize threw', e);
        fireReady(); // unblock UI anyway
      });
    },

    getPrice(productId) {
      if (store) {
        try {
          const p = store.get(productId);
          if (p) {
            const offer = p.getOffer && p.getOffer();
            if (offer && offer.pricingPhases && offer.pricingPhases[0]) {
              return offer.pricingPhases[0].price;
            }
          }
        } catch (e) { log('getPrice error', productId, e); }
      }
      const found = CATALOG.find(p => p.id === productId);
      return found ? found.fallback : '';
    },

    isOwned(productId) {
      if (!store) return false;
      try { return !!store.owned(productId); }
      catch (e) { return false; }
    },

    buy(productId) {
      return new Promise(function (resolve, reject) {
        if (!store) {
          reject(new Error('IAP not available'));
          return;
        }
        try {
          const product = store.get(productId);
          if (!product) {
            reject(new Error('Product not found: ' + productId));
            return;
          }
          const offer = product.getOffer && product.getOffer();
          if (!offer) {
            reject(new Error('Offer not found: ' + productId));
            return;
          }
          store.order(offer).then(function (err) {
            if (err) reject(new Error(err.message || 'order failed'));
            else resolve();
          }).catch(reject);
        } catch (e) { reject(e); }
      });
    },

    restore() {
      return new Promise(function (resolve, reject) {
        if (!store) { reject(new Error('IAP not available')); return; }
        try {
          store.restorePurchases().then(function (err) {
            if (err) reject(new Error(err.message || 'restore failed'));
            else resolve();
          }).catch(reject);
        } catch (e) { reject(e); }
      });
    },
  };

  global.IAP = IAP;
})(typeof window !== 'undefined' ? window : this);
