# OpenVisio v37.0 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Utilisation
Ouvrir le comparateur SAN, importer un diagramme JSON contenant `nodes` et `edges` dans le panneau de diagnostic. La synthèse présente les chemins Fabric A/B, erreurs et avertissements. Le diagnostic est en lecture seule.

## Nouveaux contrôles
Les identifiants de nœuds manquants ou dupliqués, les identifiants de liens dupliqués et les boucles sur soi-même sont signalés. Une anomalie d'identifiant invalide les résultats de redondance et doit être corrigée à la source.

## Windows
Exécuter `Build-OpenVisio-Windows.cmd` sur Windows x64 pour tenter la compilation de la version portable et de l'installateur. Puis utiliser les scripts `Qualify-OpenVisio-Windows-*.cmd`. La compilation et les tests natifs n'ont pas été exécutés dans cet environnement Linux.
