# OpenVisio v41.39 — Contrôle indépendant de la géométrie SAN
Auteur : Abdelhalim Talbi — 17 octobre 2026

## Changements
- `application/src/route-clearance.js` : inspecteur indépendant des segments de routes, signalant les intersections avec obstacles, les segments non orthogonaux et les coordonnées invalides.
- `application/tests/san-obstacle-validation-v4139.test.mjs` : six nouveaux tests.
- Le moteur de routage de production n'est pas modifié : la compatibilité historique est préservée.

## Limites
L'indicateur `avoided` existant signifie que la recherche sur grille a trouvé un chemin. Il ne garantit pas la validité du chemin final, notamment des raccords entre ports et grille. L'inspecteur est disponible mais n'est pas encore raccordé à l'interface utilisateur ni à un blocage de publication.

## Qualification
- Suite Node.js : 1781/1781 PASS.
- Qualification Windows et captures réelles : non effectuées.
- Benchmark et performance graphique : non effectués.
- Documentation Word/PDF spécifique : non produite.

## Suite v41.40
Raccorder les diagnostics au rendu et afficher clairement les routes non validées ; traiter les segments diagonaux d'ancrage sans changer silencieusement le contrat historique ; ajouter des jeux de tests de collision multi-obstacles.
