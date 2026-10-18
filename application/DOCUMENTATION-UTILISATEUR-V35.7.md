# OpenVisio v35.7 — Qualification fonctionnelle Windows

Auteur : Abdelhalim Talbi.

## Construction
Sur Windows x64, exécuter `Build-OpenVisio-Windows.cmd`.

## Qualification fonctionnelle
Installer Playwright : `py -m pip install playwright` puis `py -m playwright install chromium`.
Lancer `Qualify-OpenVisio-Windows-Functional.cmd` depuis un terminal administrateur. Ce lanceur inclut les contrôles de prévol, binaires, installateur, navigateur et scénario fonctionnel.
Le scénario Chromium réel vérifie l'ouverture de l'éditeur, l'insertion de deux formes, leur connexion, l'annulation, le rétablissement et une capture réelle. Il ne prétend pas couvrir la sauvegarde, le réimport, l'export ou la validation native WebView2.
Preuves : `dist/qualification/functional/functional-report.json`, `functional-ui-real.png`, et `dist/qualification/qualification-summary.json`.
Un statut PARTIAL signifie que des étapes ont été volontairement ignorées.
