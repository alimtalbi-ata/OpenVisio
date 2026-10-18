# OpenVisio v38.2 — audit de persistance SAN
Auteur : Abdelhalim Talbi

## Modification vérifiable
Les actions « Export JSON » et « Import JSON » de `src/main.js` invoquent maintenant respectivement `serializeSanDiagram` et `deserializeSanDiagram` de `src/zoning-document.js`.
Un domaine SAN non textuel ou supérieur à 256 caractères provoque le refus de l’export ou de l’import, sans remplacement du diagramme actif.

## Limites
Les sauvegardes automatiques via `unified-storage.js`, la restauration portable et les imports de topologie des autres panneaux ne sont pas encore intégralement reliés à ces validateurs. Aucun test natif Windows ou capture réelle n’a été effectué. Les tests d’intégration DOM et WebView2 restent à réaliser.
