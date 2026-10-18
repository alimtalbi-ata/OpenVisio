# OpenVisio v30.5 — Guide utilisateur
Auteur : Abdelhalim Talbi

Dans la matrice de résilience SAN, lancer l’analyse puis utiliser « Voir dépendances » pour colorer les objets documentés : vert = équipements terminaux connus, orange = dépendances communes. Le moteur prend également en charge le rouge pour les identifiants de segments explicitement perdus, lorsqu’ils sont fournis par un module disposant de cette traçabilité. Les comptes agrégés de chemins de la matrice actuelle ne fournissent **pas** les identifiants de tous les segments ; ils ne sont donc pas colorés artificiellement. Une nouvelle analyse ou un changement de document efface la visualisation.

Les résultats sont déclaratifs et ne prouvent ni la configuration FC réelle, ni le multipathing, ni l’absence de SPOF. Les couleurs ne modifient pas le diagramme sauvegardé.
