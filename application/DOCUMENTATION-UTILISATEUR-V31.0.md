# OpenVisio v31.0 — Audit des preuves SAN FC

Auteur : Abdelhalim Talbi.

Dans Résilience SAN, analyser le document actif, puis cliquer sur « Détail FC ». Le panneau affiche désormais une corrélation documentaire des preuves de zoning, masking et multipathing. Exporter les observations via « Exporter audit des preuves ».

Le document peut contenir `sanEvidence` : `{ "zones": [{"members":["WWPN_INI","WWPN_CIBLE"]}], "masking": [{"initiatorWwpn":"...","targetWwpn":"..."}], "hostPaths": [{"serverId":"...","storageId":"...","active":true}] }`. Les WWPN peuvent être écrits en hexadécimal sur 16 caractères ou séparés par deux-points.

**Important :** les zones, masquages et états hôtes sont des données fournies dans le document, pas des observations directes. Une absence de preuve ne démontre jamais une panne ou un défaut réel. Les écarts signalent seulement une incohérence avec les éléments fournis. Aucun changement d'équipement n'est effectué.

Windows est la plateforme prioritaire ; aucun test GUI Windows réel n'a été exécuté dans cet environnement.
