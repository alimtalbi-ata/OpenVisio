# OpenVisio V43.05 — Transparent Visio group selection

Auteur : Abdelhalim Talbi — 24 octobre 2026.

## Défaut reproduit
Un cadre de groupe Visio (`shape=visio-group`) est dessiné sans remplissage,
mais l'algorithme de hit-test sélectionnait toute sa surface. Lorsqu'un groupe
était placé après ses enfants dans le document, il empêchait la sélection des
équipements et des liaisons SAN internes.

## Correction fonctionnelle
`render.node_at` recherche d'abord les équipements pleins, puis seulement les
contours de groupe, avec une tolérance bornée. `app.node_at` adapte la tolérance
au zoom tout en préservant l'intérieur transparent. Aucune mutation du modèle
persisté ni du routage n'est introduite.

## Preuves exécutées localement
- Suite Python : 574 tests, 22 ignorés, 0 échec (Linux Python 3.13).
- Six tests V43.05 dédiés : 6 réussis.
- Les deux arborescences moteur et tests sont identiques (contrôle à renouveler
  depuis le checkout GitHub indépendant).

## Qualification distincte et limites
- GitHub / PR / CI Windows : à vérifier à partir de la branche publiée.
- Portable / installateur V43.05 : ne pas déclarer construit sans artefacts CI.
- Microsoft Visio Desktop / fidélité de fichiers réels : non qualifié.
- Test interactif manuel Windows / captures : non réalisés.
- ZIP V43.4 historique original : absent, comparaison exhaustive impossible.
- Version interne historique 42.50.0 : non modifiée.

## Reproduction fonctionnelle
Dans un document avec deux équipements reliés par une liaison FC, placer un
cadre de groupe transparent couvrant les deux équipements et la liaison, en
dernière position dans `nodes`. Un clic dans l'intérieur du cadre doit sélectionner
l'équipement ou la liaison, jamais le groupe. Un clic sur le contour doit
sélectionner le groupe. À zoom réduit, l'intérieur reste transparent.
