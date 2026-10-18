# OpenVisio v36.1 — Contrôle de fidélité SAN
Auteur : Abdelhalim Talbi.

La recette fonctionnelle `tests/browser-functional-v361.py` effectue un export JSON, une réouverture et un second export. Le module `tests/san-fidelity-v361.py` compare strictement le modèle complet et signale les différences des attributs SAN (WWPN, WWNN, Fabric, zoning, VSAN, LUN, ports). Les horodatages d’export connus sont les seuls champs ignorés.

Sous Windows x64 : exécuter `Build-OpenVisio-Windows.cmd`, installer Playwright et Chromium puis lancer `Qualify-OpenVisio-Windows-Functional.cmd`. Examiner `dist/qualification`. Aucun EXE compilé n’est livré dans le ZIP.
