# Qualification v21.2 — Abdelhalim Talbi

- Diagnostic primaire/secours sans modification des données : `src/recovery-diagnostics.js`.
- Script Windows `Recette-Windows.cmd` : exécute Chromium/Playwright, génère rapport JSON et capture **uniquement si le scénario réussit**.
- La présence de Playwright et Chromium est nécessaire. Exécuter `py -3 -m playwright install chromium` si nécessaire.
- Recette Windows réelle : **non exécutée dans cet environnement**. Les captures précédentes sont historiques, pas des preuves de recette v21.2.
- Le diagnostic ne répare pas automatiquement un document corrompu.
