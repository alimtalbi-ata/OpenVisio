# OpenVisio v32.9 — Guide Windows
Auteur : Abdelhalim Talbi

## Installation
Sur un PC Windows avec SDK .NET 8 et Inno Setup 6 : lancer `Build-Windows-Installer.cmd` depuis la racine. Le logiciel distribué est autonome vis-à-vis du SDK .NET, mais nécessite WebView2 Runtime.

## Diagnostic
Menu **Aide → Ouvrir les diagnostics** : les incidents de démarrage, de navigation et d’ouverture de documents sont enregistrés dans `%LOCALAPPDATA%\OpenVisio\diagnostics.log`. Les chemins locaux et messages d’exception peuvent apparaître dans ce journal ; ne pas le partager sans relecture.

## Vérification Windows
`powershell -ExecutionPolicy Bypass -File windows/Smoke-Test-Windows.ps1` démarre l’EXE compilé, vérifie qu’il reste actif, puis l’arrête. Ce test n’établit pas à lui seul le bon fonctionnement de l’interface et des imports/exports.

## État de qualification
Les tests JavaScript sont exécutés dans le conteneur Linux. La compilation et la recette Windows doivent être exécutées sur une machine Windows ou par GitHub Actions. Les captures réelles ne sont pas disponibles dans ce livrable.
