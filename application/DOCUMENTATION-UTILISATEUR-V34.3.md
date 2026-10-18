# OpenVisio v34.3 — Guide Windows
Auteur : Abdelhalim Talbi

## Construction
Sous Windows x64 avec accès Internet, lancer `Build-OpenVisio-Windows.cmd`. Le script prépare le SDK .NET 8, Inno Setup et le runtime WebView2, puis construit l’installateur dans `dist/installer`.

## Qualification automatisée de l’installation
Le workflow Windows exécute `windows/Test-Installer-E2E.ps1` : installation silencieuse dans un dossier temporaire, vérification de l’EXE et des ressources, lancement de l’application, contrôle du processus, puis désinstallation. Le journal d’installation est publié comme artefact même en cas d’échec.

## Utilisation
L’application propose l’édition de diagrammes, les formes d’infrastructure, les analyses SAN et l’inspecteur de propriétés. Ctrl+K ouvre la recherche de commandes. Les espaces Édition, Analyse SAN et Avancé réduisent l’encombrement visuel.

## Limites
Ce ZIP contient les sources et scripts, pas l’installateur compilé. La recette E2E est définie mais n’a pas été exécutée ici sur Windows. Le test de processus ne démontre pas le rendu graphique ni le bon fonctionnement de chaque opération métier.
