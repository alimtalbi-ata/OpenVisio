# OpenVisio v35.8 — Qualification fonctionnelle étendue
Auteur : Abdelhalim Talbi

## Construction Windows
Exécuter `Build-OpenVisio-Windows.cmd` depuis la racine extraite. La compilation et l’installateur nécessitent Windows x64.

## Qualification
Installer Playwright (`py -m pip install playwright` puis `py -m playwright install chromium`), lancer en administrateur `Qualify-OpenVisio-Windows-Functional.cmd`.

Le scénario vérifie l’ouverture de l’éditeur, l’ajout de deux formes, leur liaison, undo/redo, l’export JSON, l’export SVG et la réouverture du JSON. Les artefacts réels sont enregistrés dans `dist/qualification/functional/` si l’environnement autorise Chromium. Les contrôles navigateur ne remplacent pas un test de WebView2 natif.
