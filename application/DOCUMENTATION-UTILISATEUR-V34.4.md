# OpenVisio v34.4 — Qualification Windows

Auteur : Abdelhalim Talbi.

## Construire
Sur Windows x64 avec connexion Internet, exécuter `Build-OpenVisio-Windows.cmd` à la racine. Le script prépare .NET 8 (outil de compilation), Inno Setup et le runtime WebView2, puis produit `dist/installer/OpenVisio-Setup-v34.4-x64.exe` si toutes les étapes réussissent.

## Qualification de l’installateur
Après construction, lancer PowerShell : `./windows/Test-Installer-E2E.ps1`. Ce script installe dans un répertoire temporaire, vérifie l’EXE et les ressources, démarre OpenVisio, puis désinstalle. Il échoue en cas de timeout, code retour non nul, absence de désinstalleur ou présence résiduelle de l’EXE. Les résultats sont dans `dist/qualification/installer-e2e-result.json`.

## Limites
Aucune compilation native Windows ni capture d’écran réelle n’a été effectuée dans l’environnement de génération Linux. Les tests Node.js vérifient le code et les contrats, pas le rendu graphique Windows.
