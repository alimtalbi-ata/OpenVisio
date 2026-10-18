# OpenVisio v34.2 — Windows
Auteur : Abdelhalim Talbi

## Construction
Sur Windows x64 avec accès Internet, lancer `Build-OpenVisio-Windows.cmd`. Le script prépare le SDK .NET 8, Inno Setup et le programme d’installation WebView2, compile OpenVisio puis crée l’installateur dans `dist/installer`. Il génère également `release-manifest.json` contenant taille et SHA-256.

## Utilisation
Après installation, ouvrir OpenVisio depuis le menu Démarrer. Utiliser les espaces Édition, Analyse SAN et Avancé; `Ctrl+K` recherche les commandes. L’inspecteur peut être replié et filtré.

## Qualification
Tests JavaScript sous Linux : voir rapport. Compilation, installation, lancement et captures réelles sous Windows : non effectués ici. La présence du script ne démontre pas la réussite de la construction native.
