## OpenVisio v27.8 — Moteur de recommandations SAN

Le module `src/san-recommendations.js` expose deux fonctions :
- `analyzeSanRecommendations(corrections)` : valide les entrées, calcule les indicateurs, signale les conflits et dépendances, produit un ordre déterministe et retourne un rapport sans modifier les données d'entrée.
- `recommendationsCsv(report)` : exporte les recommandations en CSV avec neutralisation des cellules susceptibles d'être interprétées comme des formules.

Chaque correction peut définir `id`, `groupId`, `title`, `gain`, `severity` (`critical`, `high`, `medium`, `low`, `info`), `risk` (`critical`, `high`, `medium`, `low`, `none`), `selected`, `blocked`, `dependsOn`, `conflictsWith`, `fabric` et `reason`.

Les gains restent des estimations issues des données fournies ; ils ne prouvent pas un gain réel sur le SAN. Les corrections avec dépendances non satisfaites, blocages, conflits sélectionnés ou cycles ne sont pas comptabilisées dans le gain admissible. Le module n'applique aucune correction et ne se connecte pas aux équipements.

Qualification locale : `npm test`. La recette graphique Windows doit être exécutée séparément. Les snapshots historiques ne sont pas des captures réelles de la v27.8.

Auteur : Abdelhalim Talbi.

