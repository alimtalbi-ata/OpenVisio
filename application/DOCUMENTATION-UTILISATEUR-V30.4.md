# OpenVisio v30.4 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Comparaison Fabric A/B
Ouvrir un diagramme SAN, lancer l’analyse dans la matrice de résilience, puis cliquer sur « Comparer pannes A/B » sur le couple serveur/baie concerné. Le panneau affiche le nombre de chemins documentés restant en situation normale, en panne Fabric A et en panne Fabric B.

Le bouton « Exporter comparaison A/B » exporte les trois scénarios par couple actuellement filtré (P1–P4), avec chemins perdus, restants, statut et dépendances communes. Les champs CSV sont protégés contre l’injection de formules.

**Limites :** les chemins représentés proviennent uniquement de la topologie du document. Le rendu ne certifie pas le zoning, le masking, les chemins MPIO ni la disponibilité réelle. Une dépendance commune doit être examinée avant toute conclusion SPOF. La surbrillance porte sur les objets identifiés (terminaux et dépendances), pas nécessairement chaque segment du chemin.
