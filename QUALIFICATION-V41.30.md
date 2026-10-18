# OpenVisio v41.30 — profilage des sous-phases
Auteur : Abdelhalim Talbi

## Changement
Instrumentation non intrusive du pipeline dans `application/src/renderer.js` : `routeCalculation`, `parallelSeparation`, `sharedSegmentHandling`, `endpointDistribution`. Les durées sont exposées dans `lastRenderPhaseProfile(svg).routingStages`. Un objet vide indique qu'aucun recalcul du pipeline n'a eu lieu. Le total `routingPipeline` inclut également les frais d'orchestration et ne doit pas être assimilé à la somme exacte des sous-phases.

## Mesures (une exécution, DOM simulé)
| Équipements | Calcul initial ms | Parallèles ms | Segments partagés ms | Distribution ms | Pipeline ms |
|---:|---:|---:|---:|---:|---:|
|10|15.171|0.399|0.701|10.956|27.631|
|25|60.497|0.454|0.828|60.728|122.984|
|50|103.464|0.817|1.111|120.129|226.172|
|100|336.520|0.736|0.875|367.488|706.518|

Les deux postes dominants sont le calcul initial et la distribution des extrémités. La séparation des parallèles et des segments partagés n'est pas prioritaire sur ce jeu de données. Ces mesures ne démontrent pas une amélioration par rapport à v41.29 : seule l'instrumentation a changé.

## Vérifications
- `npm test` : 1763/1763 PASS.
- `npm run benchmark:svg:phases` : 4/4 topologies PASS.
- Pas de qualification Windows ni de capture d'écran réelle.
- Les guides Word/PDF hérités n'ont pas été mis à jour ; ce rapport ne s'y substitue pas.

## Prochaines actions
Profiler les sous-fonctions de distribution (`distributeEndpointAnchors`, `orthogonalFanOut`, `reduceFanOutCrossings`) et le calcul de route par style. Vérifier équivalence géométrique, collisions et Undo/Redo avant optimisation.
