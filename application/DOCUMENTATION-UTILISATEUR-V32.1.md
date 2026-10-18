# OpenVisio v32.1 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Preuves FC multi-attributs
Le moteur `src/san-fc-evidence-v321.js` expose `evaluateFcEvidence(entry, snapshot)` et `fcEvidenceCsv(reports)`. Il croise les WWPN exacts avec les ports FC et la Fabric lorsqu’ils sont renseignés, et conserve les marqueurs ISL.

Résultats : `CORROBORATED` (WWPN, port et Fabric concordants), `PARTIAL` (preuve incomplète), `CONFLICT` (port ou Fabric contradictoire), `NO_MATCH`, `NO_WWPN_EVIDENCE`. Les champs absents restent `UNKNOWN`.

**Portée** : API logicielle livrée pour intégration au panneau SAN. Les exports ne sont pas des preuves de zoning actif ou de connectivité physique. Aucun changement de configuration d’équipement.
