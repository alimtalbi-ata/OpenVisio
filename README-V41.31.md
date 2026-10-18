# OpenVisio v41.31 — Profilage des extrémités SAN

Auteur : Abdelhalim Talbi

Le moteur de rendu mesure maintenant séparément `distributeEndpointAnchors`, `orthogonalFanOut` et `reduceFanOutCrossings` via `lastRenderPhaseProfile(svg).routingStages`. Les algorithmes et leur ordre restent inchangés.

Les mesures sont indicatives et peuvent varier selon la machine. La compilation Windows et les captures réelles ne sont pas couvertes par cette livraison.
