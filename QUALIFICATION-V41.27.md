# OpenVisio v41.27 — Profilage instrumenté SVG

Auteur : Abdelhalim Talbi.

Cette livraison enrichit le benchmark DOM simulé avec cinq itérations, statistiques de mutations DOM et diagnostics du cache. Le premier rendu mesuré dans une itération est un rendu déjà réchauffé pour les itérations suivantes : il ne faut pas l’interpréter comme cinq rendus froids indépendants.

Le script est `npm run benchmark:svg:profile`. Les mesures excluent layout, paint, GPU, navigateur réel et Windows. Les phases internes du moteur ne sont pas encore chronométrées séparément.

Statut benchmark : PASS

Les tests historiques doivent être exécutés séparément. Les guides Word/PDF historiques ne sont pas mis à jour dans cette livraison.
