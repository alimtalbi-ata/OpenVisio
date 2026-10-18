# OpenVisio v30.7 — Traçabilité des chemins SAN
Auteur : Abdelhalim Talbi

## Nouveauté
Le module `src/san-path-trace-v307.js` enrichit chaque chemin découvert avec la séquence des connexions, ports HBA/FC/cible, WWPN et indication ISL lorsque deux commutateurs se suivent. Les métadonnées manquantes sont signalées et jamais inventées.

## Utilisation développeur
Importer `traceSanPaths(document, {serverId, storageId})` et `pathTraceCsv(result)`. Le CSV liste chaque saut dans l'ordre et protège contre l'injection de formules.

## Limites
Ce module est une API de diagnostic et d'export, pas encore un panneau graphique. Les informations sont uniquement celles documentées dans le diagramme. Aucun contrôle de zoning, masking ou multipathing réel.
