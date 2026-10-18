# OpenVisio v41.19 — Benchmark du cycle de routage SAN
Auteur : Abdelhalim Talbi

## Périmètre
Benchmark reproductible de topologies SAN **synthétiques**, 100/500/1000 connexions, 7 répétitions, comparaison purge complète / invalidation ciblée et équivalence géométrique stricte sur les trajets produits. Script : `application/scripts/benchmark-san-cycle-v419.mjs`.

Les temps incluent la lecture des routes et les recalculs via `routeEdge`, pas le DOM, le rendu SVG, le navigateur ni Windows. Le fixture déplace un équipement et touche huit connexions. Les valeurs sont des médianes d'une seule campagne, non des garanties de performance.

## Résultats
Voir `BENCHMARK-SAN-CYCLE-V41.19.json` et `.txt`.

## Limites et suite
Qualification UI Windows, captures réelles, topologies SAN importées, comparaison multi-machines et mises à jour de tous les guides Word/PDF : non effectuées. Le versionnement historique de package.json est conservé pour ne pas casser les tests ; dette ouverte.
