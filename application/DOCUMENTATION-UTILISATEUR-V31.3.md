# OpenVisio v31.3 — Corrélation import SAN / diagramme

Auteur : Abdelhalim Talbi.

1. Ouvrir un diagramme contenant des chemins SAN et des WWPN déclarés.
2. Importer un extrait texte Brocade/Cisco/ESXi via le panneau d’import existant.
3. Ouvrir « Corrélation import SAN / diagramme » et cliquer « Comparer au diagramme ».
4. Examiner les statuts DOCUMENTED_PAIR, UNKNOWN_WWPN, NO_ZONE_EVIDENCE, PAIR_NOT_IN_IMPORT.
5. Exporter les observations CSV.

**Attention :** les exports peuvent être incomplets. Une paire non trouvée ne prouve pas un défaut de zoning. Aucun équipement n’est interrogé ni modifié.
