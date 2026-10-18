# OpenVisio v31.1 — Import de preuves SAN

Auteur : Abdelhalim Talbi.

Le module `src/san-config-import-v311.js` importe **hors ligne** des extraits texte de zoning Brocade (`zone:`), Cisco MDS (`zone name` et `member pwwn`) et états de chemins ESXi (`Runtime Name`, `State`). API : `importSanConfiguration(texte,{vendor,source})`, `compareImportedZonesToDiagram(import, paires)`. Le moteur renvoie zones, alias, chemins hôtes et avertissements. Il ne se connecte pas aux équipements et ne prouve pas la configuration active. Les alias non résolus ne sont pas assimilés à des WWPN. Aucun import graphique n’est encore disponible dans cette version.
