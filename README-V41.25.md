# OpenVisio v41.25 — Instrumentation de qualification SVG

Auteur : Abdelhalim Talbi.

Ajout du script `application/scripts/benchmark-svg-v425.mjs` pour mesurer les rendus dans un DOM simulé et contrôler la stabilité du nombre d'éléments. Première exécution interrompue après 18 secondes sans résultat exploitable. Aucun gain n'est revendiqué. Suite Node.js complète non réexécutée. Les résultats v41.24 sont historiques et ne qualifient pas v41.25.

Limites : aucune recette Chromium, Windows, collisions d'obstacles ou captures réelles. Étape suivante : profiler les coûts et réduire la durée du benchmark avant de publier des mesures.
