# Audit Windows v35.2 — Abdelhalim Talbi

## Défaut bloquant confirmé
Le script `windows/Preflight-Windows.ps1` comparait la version à `34.3.0` alors que le projet était en `35.1.0`. Le `Build-OpenVisio-Windows.cmd` exécutait ce précontrôle en première étape : la construction Windows était donc bloquée avant toute compilation. Remplacé par une comparaison dérivée de `package.json`.

## Corrections
- Préflight dynamique : package.json / Inno Setup / csproj / script CMD.
- Titre et boîte À propos du shell WinForms synchronisés en v35.2.
- Tests de non-régression sur les métadonnées de la chaîne Windows.

## Limites de validation
- Tests JavaScript exécutables sur Linux ; aucune compilation native .NET, aucun Inno Setup, aucune installation et aucun lancement graphique Windows réalisés ici.
- L'installation du SDK .NET 8, d'Inno Setup et de WebView2 requiert accès Internet et autorisations Windows adaptées.
- Le test E2E PowerShell existant vérifie lancement de processus et fichiers, mais pas l'interaction réelle avec l'interface ; un essai sur VM Windows reste nécessaire.
