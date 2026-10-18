# OpenVisio v27.0 — Optimisation SAN par composants
Auteur : Abdelhalim Talbi.

- Décomposition du graphe des conflits en composants indépendants.
- Résolution exacte par composant jusqu’à 18 propositions, même pour des lots globaux plus grands.
- Stratégie heuristique déterministe réservée aux composants de plus de 18 propositions.
- Rejet des identifiants dupliqués, des scores non finis et des conflits mal formés.
- Présentation dans l’interface du nombre de groupes exacts et heuristiques.
- Aucun commit automatique : validation humaine et contrôles de topologie existants conservés.
- Les snapshots préexistants sont historiques ; aucune nouvelle capture réelle Windows n’est revendiquée.
