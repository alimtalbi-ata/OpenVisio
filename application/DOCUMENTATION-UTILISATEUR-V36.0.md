# OpenVisio v36.0 — Qualification de fidélité du modèle

Auteur : Abdelhalim Talbi.

## Nouveauté

Le scénario `tests/browser-functional-v360.py` réexporte le diagramme JSON après réouverture et compare le modèle complet au modèle initial. Seuls les horodatages d’export explicitement énumérés sont exclus de la comparaison. Les identifiants, relations, attributs et métadonnées SAN restent comparés.

## Construction Windows

Exécuter `Build-OpenVisio-Windows.cmd` sur Windows x64, puis `Qualify-OpenVisio-Windows-Functional.cmd` pour les tests navigateur. L’exécution sur Windows reste à effectuer.

## Limites

Les tests Node.js vérifient la structure des scénarios et les modules ; ils ne prouvent ni la réussite du scénario Chromium, ni la compilation .NET ou Inno Setup.
