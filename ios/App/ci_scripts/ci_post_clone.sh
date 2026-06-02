#!/bin/sh

# ci_post_clone.sh
# Exécuté automatiquement par Xcode Cloud juste après le clone du dépôt,
# AVANT la compilation. Le dossier Pods/ étant volontairement ignoré par git,
# il faut le régénérer ici (sinon Pods-App.release.xcconfig est absent → build KO).

set -e

# 1. S'assurer que CocoaPods est disponible (ne réinstalle que si absent → plus rapide, zéro conflit)
if ! command -v pod >/dev/null 2>&1; then
  echo "CocoaPods absent → installation via Homebrew…"
  brew install cocoapods
else
  echo "CocoaPods déjà présent : $(pod --version)"
fi

# 2. Régénérer le dossier Pods/ à partir du Podfile.lock commité
cd "$CI_PRIMARY_REPOSITORY_PATH/ios/App"
pod install

echo "✅ pod install terminé — Pods/ régénéré pour Xcode Cloud"
