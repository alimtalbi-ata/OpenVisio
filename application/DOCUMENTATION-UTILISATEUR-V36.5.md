# OpenVisio v36.5 — Guide Windows
Auteur : Abdelhalim Talbi

## Construction
Sur Windows x64, exécuter `Build-OpenVisio-Windows.cmd` depuis le dossier extrait. Le script prépare .NET 8, Inno Setup et le prérequis WebView2, compile l’application puis construit l’installateur et la distribution portable.

## Livrables attendus après construction réussie
- `dist\windows-x64\OpenVisio.exe` (avec `wwwroot` et d’éventuels fichiers annexes)
- `dist\installer\OpenVisio-Setup-v36.5-x64.exe`
- `dist\portable\OpenVisio-v36.5-Windows-x64-Portable.zip`

## Mode portable
Extraire **tout** le ZIP portable, puis lancer `OpenVisio.exe`. Ne pas isoler l’EXE de `wwwroot`. WebView2 Runtime doit être installé sur Windows. Le programme n’a pas besoin d’être installé via Inno Setup. Les données utilisateur WebView2 et l’historique récent restent enregistrés dans `%LOCALAPPDATA%\OpenVisio` : ce n’est pas un mode sans traces.

## Qualification
Lancer `Qualify-OpenVisio-Windows-Functional.cmd` sur Windows, après installation de Playwright et Chromium. Conserver les rapports et captures de `dist\qualification`.
