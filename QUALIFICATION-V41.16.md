# OpenVisio v41.16 — Raccordement transactionnel du rendu

Auteur : Abdelhalim Talbi.

Le rendu appelle maintenant `reconcileEdgeTransaction` comme point d’entrée unique de réconciliation des connexions, avec invalidation ciblée via `invalidateCachedEdgeRoutes`. La session reste attachée au canevas. Les signatures de connexions couvrent les ports, les points de passage et les extrémités.

La qualification Node.js ne remplace pas les tests interactifs Windows. Les modifications de géométrie des équipements, les benchmarks SAN comparatifs, les captures réelles et la compilation Windows restent non qualifiés.
