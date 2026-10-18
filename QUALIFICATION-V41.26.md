# OpenVisio v41.26 — Diagnostic borné SVG

Auteur : Abdelhalim Talbi.

Le benchmark v41.25 a dépassé 12 secondes sans sortie. v41.26 exécute chaque taille dans un processus isolé avec délai maximal de 5 secondes. Aucun temps de navigateur, de peinture SVG ou de Windows n’est mesuré.

- 10 nœuds : PASS ; durée murale 90.34 ms
- 25 nœuds : PASS ; durée murale 168.83 ms
- 50 nœuds : PASS ; durée murale 278.72 ms
- 100 nœuds : PASS ; durée murale 748.06 ms

Un TIMEOUT ne démontre pas à lui seul une régression. Il impose un profilage du chemin de routage avant optimisation. Les captures Windows restent non disponibles.
