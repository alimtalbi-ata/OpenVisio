# OpenVisio v36.9 — Guide utilisateur

Auteur : Abdelhalim Talbi.

## Construction Windows
Extraire cette archive sur Windows x64, puis lancer `Build-OpenVisio-Windows.cmd`. Le processus prévoit un EXE portable mono-fichier et un installateur Inno Setup. Le runtime WebView2 reste requis.

## Diagnostic SAN
Ouvrir le comparateur de topologies, accéder au diagnostic SAN et importer un diagramme JSON pour examiner la redondance Fabric A/B.

## Vérifications
Lancer `npm test` pour les tests Node.js. Les scripts `Qualify-OpenVisio-Windows-Functional.cmd` et `Qualify-OpenVisio-Windows-Graphic.cmd` prévoient une recette native à exécuter sur Windows.

## Limites
La compilation native Windows et les captures réelles ne sont pas disponibles dans cet environnement Linux.
