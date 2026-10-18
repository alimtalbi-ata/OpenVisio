# OpenVisio v34.2 — Utilisation et construction Windows

Auteur : Abdelhalim Talbi.

## Construction
Sur Windows x64, extraire l’archive, puis exécuter `Build-OpenVisio-Windows.cmd`. Le script récupère le SDK .NET 8 localement, cherche ou installe Inno Setup, télécharge le prérequis WebView2 signé, publie OpenVisio et génère `dist\installer\OpenVisio-Setup-v34.2-x64.exe`.

La connexion Internet est nécessaire lors de la construction. Le SDK .NET n’est pas requis sur le poste utilisateur si la publication autonome réussit. Le runtime WebView2 est inclus dans l’installateur et installé si absent.

## Interface
L’éditeur dispose des espaces Édition, Analyse SAN et Avancé. `Ctrl+K` ouvre la recherche de commandes. La bibliothèque et l’inspecteur sont redimensionnables ; l’inspecteur permet de filtrer les propriétés et de les replier.

## Qualification
Exécuter `npm test` pour les tests JS. La compilation, l’installation et les captures réelles doivent être validées sur un poste Windows.
