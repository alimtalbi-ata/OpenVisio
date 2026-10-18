# Qualification OpenVisio v19.4

Auteur : Abdelhalim Talbi

- Tests Node : 802 réussis sur 802 (`npm test`).
- Six nouveaux tests structurels de rétablissement, historique, raccourcis et version.
- Limites : les tests sont structurels et ne valident pas le parcours utilisateur interactif dans un navigateur Windows.
- Captures : les fichiers `snapshots/` sont des captures historiques ; aucune capture réelle v19.4 n’a été produite.
- EXE Windows : non compilé.
- Historique : l'état du canevas est restauré ; les états de panneaux auxiliaires conservés séparément ne sont pas couverts par le rétablissement.
