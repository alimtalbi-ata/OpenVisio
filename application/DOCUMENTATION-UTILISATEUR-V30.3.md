# OpenVisio v30.3 — guide utilisateur
Auteur : Abdelhalim Talbi

## Matrice de résilience SAN
Ouvrir un diagramme, lancer l’analyse dans le panneau SAN, puis sélectionner « Comparer pannes A/B » sur un couple serveur/stockage. Le statut indique les chemins documentés restants après perte de Fabric A ou de Fabric B. Le canvas met en évidence les composants référencés par leurs identifiants SVG.

## Interprétation
LOSS = aucun chemin documenté restant ; DEGRADED = chemins restants mais pas de double fabric ; DOCUMENTED_DUAL_FABRIC = chemins A et B présents. Les dépendances communes sont signalées. Ces calculs ne remplacent pas une vérification physique du zoning, du masking, du multipathing ou des contrôleurs.

## Installation Windows
Décompresser le ZIP, puis suivre le README du projet. La version v30.3 ne nécessite pas d’action sur les équipements SAN.
