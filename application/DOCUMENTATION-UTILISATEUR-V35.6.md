# OpenVisio v35.6 — Qualification fonctionnelle Windows

Auteur : Abdelhalim Talbi

## Construction
Lancer `Build-OpenVisio-Windows.cmd` sous Windows x64. Le script vise `dist/installer/OpenVisio-Setup-v35.6-x64.exe`.

## Qualification de base
Exécuter `Qualify-OpenVisio-Windows.cmd` en administrateur pour les contrôles de publication, lancement et installation. Le rapport est `dist/qualification/qualification-summary.json`.

## Qualification graphique (optionnelle)
Installer Python et Playwright Chromium (`py -m pip install playwright`, `py -m playwright install chromium`), puis exécuter `Qualify-OpenVisio-Windows-Graphic.cmd` en administrateur. Le test graphique réutilise `tests/browser-san-performance.py` et génère `dist/qualification/browser/browser-report.json` ainsi que `openvisio-ui-real.png` **uniquement en cas de réussite réelle**.

L'absence de Playwright ou un test échoué doit être diagnostiqué dans le rapport, sans fabrication de captures. L'absence d'exécution graphique avec le script de base donne PARTIAL (code 2).

## Limites
La compilation Windows et l'installation n'ont pas été exécutées dans l'environnement Linux de création de cette archive. Le test navigateur ne remplace pas une recette utilisateur complète (ouvrir, éditer, enregistrer, réouvrir, exporter).
