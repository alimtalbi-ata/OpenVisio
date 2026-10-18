# OpenVisio v34.2 — Windows

Auteur : Abdelhalim Talbi.

## Construction

Sur Windows x64, avec accès Internet, exécuter `Build-OpenVisio-Windows.cmd` depuis la racine du projet. Le script vérifie d’abord les fichiers sources et la cohérence de version, prépare .NET 8 et Inno Setup, vérifie la signature du programme d’installation WebView2, puis compile l’application et l’installateur.

Livrable attendu : `dist/installer/OpenVisio-Setup-v34.2-x64.exe`.

## Installation

Exécuter l’installateur sous Windows avec droits administrateur. Le programme d’installation embarque le runtime WebView2 et tente de l’installer si absent. L’installation et la désinstallation doivent être validées sur un poste Windows de recette.

## Limites de qualification

Les tests Node.js et les contrôles statiques ne prouvent pas que l’exécutable .NET compile, ni que l’installateur fonctionne. Aucun EXE compilé n’est livré dans cette archive source.
