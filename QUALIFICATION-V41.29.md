# OpenVisio v41.29 — Profilage des phases SVG

Auteur : Abdelhalim Talbi.

Le benchmark borné collecte désormais les durées par phase (`lastRenderPhaseProfile`) pour chaque itération, dans un DOM simulé. Les mesures ne représentent ni le navigateur ni Windows.

Commande : `cd application && npm run benchmark:svg:phases`.

Les cinq itérations réutilisent le même canevas : seules les premières mesures sont des rendus à froid. Aucun gain de performance n’est revendiqué.
