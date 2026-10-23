# OpenVisio V42.83 — SAN endpoint integrity and CI trigger

Auteur : Abdelhalim Talbi — 23 octobre 2026.

## Correction métier
L'importeur VSDX externe refusait les IDs de connecteurs dupliqués, mais ignorait silencieusement une ligne Connects BeginX/EndX pointant vers une feuille inexistante. Un chemin SAN incomplet pouvait donc disparaître du diagramme importé sans erreur. Le correctif refuse les extrémités SAN absentes. Les feuilles existantes mais non importables (groupes sans géométrie valide) conservent la politique conservatrice d'omission antérieure.

## Preuves locales
- Avant correction : 2/3 tests synthétiques ciblés en échec.
- Après correction : 3/3 tests ciblés PASS.
- Suite cumulative locale Python 3.13/Linux : 750 tests, 41 ignorés, 0 échec.
- Miroirs moteur et tests comparés localement avant livraison.

## Windows
Le workflow V42.82 précédent ciblait un nom de branche inexistant ; sa référence a été corrigée sur la branche V42.82 dans le commit ef637fa9bac0f21e7d3d67cccb9b4071255cd298. V42.83 possède son propre workflow déclenché par sa branche, un script PowerShell et une recette Inno Setup. Le statut Windows V42.83 doit être contrôlé séparément ; ne pas assimiler la présence des scripts à une compilation réussie.

## Périmètre non certifié
Le ZIP V43.4 historique est absent. La fidélité réelle Microsoft Visio et les captures d'interface Windows restent non qualifiées. La version interne de l'application reste 42.50.0. Aucun secret ni déploiement en production.
