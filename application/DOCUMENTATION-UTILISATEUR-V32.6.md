# OpenVisio v32.6 — Application Windows
Auteur : Abdelhalim Talbi

## Construction
Sur Windows x64, installer .NET SDK 8, puis exécuter `Build-Windows-EXE.cmd`. Pour produire un installateur, installer Inno Setup 6 et exécuter `Build-Windows-Installer.cmd`. L’application finale nécessite le runtime Microsoft Edge WebView2.

## Usage
Ouvrir les documents OpenVisio JSON via Fichier > Ouvrir ou Ctrl+O. Les documents récents sont mémorisés dans le profil local. Les exports utilisent la boîte Enregistrer sous de Windows. Les imports spécialisés SAN restent accessibles depuis l'éditeur.

## Qualification
Le projet contient des tests automatisés JavaScript. La compilation Windows, la validation du runtime WebView2, la recette graphique et l'installateur ne sont pas vérifiés dans cet environnement Linux.
