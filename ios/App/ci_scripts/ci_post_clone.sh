#!/bin/sh

# ci_post_clone.sh
# Exécuté automatiquement par Xcode Cloud juste après le clone du dépôt,
# AVANT la compilation. Le dossier Pods/ étant volontairement ignoré par git,
# il faut le régénérer ici (sinon Pods-App.release.xcconfig est absent → build KO).

set -e

# 1. Installer CocoaPods (l'environnement Xcode Cloud est vierge)
brew install cocoapods

# 2. Régénérer le dossier Pods/ à partir du Podfile.lock commité
cd "$CI_PRIMARY_REPOSITORY_PATH/ios/App"
pod install

echo "✅ pod install terminé — Pods/ régénéré pour Xcode Cloud"
