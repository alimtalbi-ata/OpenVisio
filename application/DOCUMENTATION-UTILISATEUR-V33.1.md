# OpenVisio v33.1 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Interface
Cliquer sur **Rechercher une action** en bas à gauche, ou appuyer sur **Ctrl+K**. Saisir une partie du nom d’une fonction (par exemple `SAN`, `SPOF`, `zoning`), puis cliquer sur l’action. **Entrée** lance la première action affichée, **Échap** ferme le lanceur. Les anciens menus restent disponibles.

## Compilation Windows
Sur Windows x64, extraire le ZIP et exécuter `Build-OpenVisio-Windows.cmd`. Le script tente de télécharger .NET 8, d’installer Inno Setup avec winget, de télécharger WebView2, de publier le logiciel puis de construire `dist\installer\OpenVisio-Setup-v33.1-x64.exe`. Internet et winget sont nécessaires à cette chaîne. Ne pas présenter le fichier EXE comme existant tant que le script n’a pas réussi.

## Installation
Lancer l’EXE construit sur Windows. L’installateur inclut le bootstrapper WebView2 et tente l’installation silencieuse si absent. Tester installation/désinstallation et l’ouverture de fichiers `.ovjson` sur une machine de recette avant diffusion.
