# OpenVisio v41.37 — Qualification différentielle
Auteur : Abdelhalim Talbi

## Changements
- Quatre tests différentiels déterministes ajoutés dans `application/tests/crossing-differential-v4137.test.mjs`.
- Vérification de l'invariant de variation des croisements après mutation d'une route, pour 8, 24 et 64 routes orthogonales et huit graines par taille.
- Test de restauration après déplacement (Undo/Redo simulé par copie des états).
- Aucun changement de l'algorithme de production et aucun second cache.

## Exécution réelle
- `npm test` : 1771/1771 PASS (Node.js).
- Tests ciblés : 4/4 PASS.
- Qualification Chromium/Windows : non exécutée.
- Obstacles physiques et ports réels de l'éditeur : non qualifiés par ces tests synthétiques.
- Benchmark de performance v41.37 : non exécuté.

## Suite
Tester le routage avec obstacles et ports multiples dans le moteur réel, puis profiler les cas de forte densité avant d'envisager un index spatial.
