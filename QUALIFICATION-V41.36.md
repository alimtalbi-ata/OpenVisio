# OpenVisio v41.36 — Qualification comparative bornée

Auteur : Abdelhalim Talbi

## Méthode
Trois topologies synthétiques (échelle, dense, parallèle), 20/50/100 connexions, médiane de trois répétitions. Ordre des algorithmes alterné. Comparaison stricte des points et chemins de chaque route. Pas de navigateur ni Windows.

| Scénario | Connexions | Historique ms | Incrémental ms | Équivalence |
|---|---:|---:|---:|---|
| ladder | 20 | 18.23 | 9.692 | PASS |
| ladder | 50 | 94.756 | 8.181 | PASS |
| ladder | 100 | 788.606 | 30.468 | PASS |
| dense | 20 | 6.551 | 1.398 | PASS |
| dense | 50 | 102.009 | 7.791 | PASS |
| dense | 100 | 860.129 | 31.729 | PASS |
| parallel | 20 | 6.949 | 1.326 | PASS |
| parallel | 50 | 105.903 | 7.547 | PASS |
| parallel | 100 | 809.651 | 30.359 | PASS |

## Qualification
- Suite Node.js : 1767/1767 PASS.
- Benchmark : 9/9 cas équivalents.
- Compilation Windows, capture réelle et mesure de fluidité : non effectuées.
- Les guides historiques restent inchangés ; ce rapport est spécifique à la version.
- Ne pas généraliser les gains à des diagrammes réels sans campagne navigateur.