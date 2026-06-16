#!/bin/sh

# ci_post_clone.sh
# Exécuté par Xcode Cloud juste après le clone, AVANT la compilation.
# Xcode Cloud clone un dépôt PROPRE : node_modules/ ET
# ios/App/capacitor-cordova-ios-plugins/ sont gitignorés (normal) donc absents.
# Or le Podfile pointe dessus → il faut les régénérer ici, sinon `pod install`
# échoue (exit 1) et tout le build échoue.

set -e
export HOMEBREW_NO_AUTO_UPDATE=1

# 1. Outils requis (installés seulement si absents)
command -v node >/dev/null 2>&1 || { echo "Node absent → install…"; brew install node; }
command -v pod  >/dev/null 2>&1 || { echo "CocoaPods absent → install…"; brew install cocoapods; }
echo "node $(node --version) / pod $(pod --version)"

# 2. Régénérer node_modules (le Podfile Capacitor en dépend)
cd "$CI_PRIMARY_REPOSITORY_PATH"
npm ci --no-audit --no-fund

# 3. cap sync ios = copie le web + régénère capacitor-cordova-ios-plugins + pod install
npx cap sync ios

echo "✅ npm ci + cap sync ios terminés — Pods/ et plugins régénérés"
