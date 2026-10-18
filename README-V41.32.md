# OpenVisio v41.32 — Profilage des croisements SAN

Auteur : Abdelhalim Talbi

Cette version apporte une campagne de mesure des sous-phases introduites en v41.31, sans changement de l’algorithme de routage.

| Équipements | Calcul routes (ms) | Réduction croisements (ms) | Ancres (ms) | Fan-out (ms) |
|---:|---:|---:|---:|---:|
| 10 | 16.661 | 9.442 | 0.533 | 0.667 |
| 25 | 74.717 | 62.818 | 0.482 | 0.758 |
| 50 | 98.15 | 116.292 | 0.568 | 1.173 |
| 100 | 329.053 | 354.91 | 0.67 | 2.537 |

Mesures : une exécution froide par topologie, DOM simulé, pas de qualification navigateur ou Windows. Aucune accélération avant/après n’est revendiquée. La suite complète de tests n’a pas été réexécutée dans cette livraison.

Prochaine action : profiler `countRouteCrossings`, puis remplacer le recalcul global répété par une stratégie incrémentale avec tests de conformité géométrique.
