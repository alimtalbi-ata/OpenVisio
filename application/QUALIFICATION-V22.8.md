# Qualification OpenVisio v22.8

Auteur : Abdelhalim Talbi

- `npm test` : 976 tests réussis, 0 échec.
- `npm run benchmark:dense` : exécuté avec 100, 300, 600 connexions et 7 répétitions mesurées après 3 échauffements.
- Médianes 600 connexions : sparse 0,461 ms ; parallel 1,852 ms ; dense 7,051 ms.
- Les mesures concernent le diagnostic seulement, pas le rendu SVG ni Windows.
- Recette graphique Windows non effectuée ; les snapshots sont historiques.
- Analyse non destructive ; budgets maxSegments, maxPairs, maxFindings ; statut complete.
