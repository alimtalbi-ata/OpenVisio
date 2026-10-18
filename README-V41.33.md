OpenVisio v41.33 — Optimisation incrémentale des croisements SAN

Auteur : Abdelhalim Talbi

Objectif : supprimer le recalcul global des croisements lors de l’évaluation d’une route candidate.

Modification : score local = somme des croisements entre la route candidate et chacune des autres routes, plus longueur Manhattan.

Justification : les croisements entre routes non modifiées sont constants entre candidats ; le classement des scores reste inchangé.

Qualification : 1767 tests Node.js réussis sur 1767, dont deux tests supplémentaires.

Limites : pas de benchmark comparatif chronométré ; aucune qualification Windows ou capture réelle ; absence de preuve exhaustive d’équivalence sur diagrammes complexes.

Prochaine étape : comparaison v41.32/v41.33, cas SAN réels, contrôle géométrique et recette Windows.
