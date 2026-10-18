# OpenVisio v32.9 — Windows desktop
Auteur : Abdelhalim Talbi

## Construire sur Windows
1. Installer le SDK .NET 8 et Node.js 22.
2. Exécuter `npm test` puis `Build-Windows-EXE.cmd`.
3. Installer Inno Setup 6 et exécuter `Build-Windows-Installer.cmd`.
4. Le programme est publié dans `dist/windows-x64`, et l’installateur dans `dist/installer`.

## Automatisation Windows
Le workflow `.github/workflows/windows-release.yml` construit sous `windows-latest`, teste JavaScript, publie le dossier Windows et l’installateur comme artefacts de CI. La CI n'a pas été exécutée dans cet environnement.

## Correctifs
Ouverture native attend l'initialisation de l'éditeur; suppression des doublons de l'historique des fichiers sans tenir compte de la casse; version synchronisée.

## Limites
L'EXE et l'installateur ne sont pas inclus dans ce ZIP source. La compilation native Windows et la recette visuelle restent à exécuter.
