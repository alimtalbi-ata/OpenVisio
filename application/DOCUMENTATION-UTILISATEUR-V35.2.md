# OpenVisio v35.2 — Windows
Auteur : Abdelhalim Talbi

## Génération du programme et de l'installateur
Sur Windows 10/11 x64, extraire entièrement le ZIP, puis lancer `Build-OpenVisio-Windows.cmd` dans le dossier racine. Connexion Internet requise. Le script vérifie les sources, installe localement le SDK .NET 8 si absent, installe Inno Setup via winget si nécessaire, télécharge et vérifie le prérequis WebView2, publie `dist/windows-x64/OpenVisio.exe`, puis génère `dist/installer/OpenVisio-Setup-v35.2-x64.exe`. Il échoue sans annoncer de succès si une étape est invalide.

## Qualification recommandée
Après construction, exécuter PowerShell : `powershell -NoProfile -ExecutionPolicy Bypass -File windows/Test-Installer-E2E.ps1` sur une VM Windows de recette. Vérifier manuellement ouverture, édition, sauvegarde, export, analyses SAN, raccourcis et désinstallation. Conserver les logs sous `dist/qualification`.

## Note
Les artefacts EXE ne sont pas fournis dans ce ZIP source. Aucune capture d'écran réelle Windows n'a été produite dans cet environnement.
