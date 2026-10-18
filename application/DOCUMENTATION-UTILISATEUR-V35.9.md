# OpenVisio v35.9 — Guide utilisateur et recette Windows

Auteur : Abdelhalim Talbi.

## Construction
Sur Windows x64, exécuter `Build-OpenVisio-Windows.cmd` à la racine du projet. Le script prépare les outils, compile l’application et l’installateur.

## Qualification fonctionnelle
Installer Playwright et Chromium avec `py -m pip install playwright` et `py -m playwright install chromium`, puis exécuter `Qualify-OpenVisio-Windows-Functional.cmd` dans un terminal administrateur.

Le scénario v35.9 insère deux objets et une connexion, teste undo/redo, exporte JSON/SVG, réimporte le JSON et compare les nombres de noeuds **et** de connexions avant/après. Les rapports sont écrits sous `dist/qualification`.

## Limites
Les tests Node.js et la syntaxe Python ne prouvent pas le fonctionnement de l’installateur Windows. Aucune capture réelle Windows n’est incluse sans exécution native.
