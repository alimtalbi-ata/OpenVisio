# OpenVisio V42.85 — Qualification et traçabilité

Auteur : **Abdelhalim Talbi**. Branche : `develop/v42.85-external-san-shape-identity-20261024`. PR #18 en brouillon, cible V42.84 ; aucune fusion sur `main`.

## Correction métier

Le moteur `vsdx_external._kind` classait des commutateurs SAN/FC provenant de VSDX externes en `network-switch`. La correction reconnaît explicitement les motifs SAN Switch/Fabric/Director, FC Switch/Fabric/Director et Fibre/Fiber Channel. `San Francisco Switch` et les commutateurs LAN restent `network-switch`. Deux miroirs moteur corrigés.

## Tests et publication

- Avant correction : 8 échecs d'assertion sur les trois nouveaux tests ciblés.
- Après correction : 2/2 tests unitaires ciblés, 1/1 intégration VSDX synthétique avec deux liens parallèles.
- Régression historique restaurée : `test_layers_persistence_v426.py` (6/6) et `test_vsdx_multipage_v426.py` (6/6).
- Linux Python 3.13 : **757 tests, 41 ignorés, 0 échec**. Miroirs locaux : 57 modules moteur, 160 fichiers de tests.
- GitHub : 57 modules moteur et 106 fichiers de tests par miroir, **54 tests historiques encore absents**.
- Les huit blobs Git du moteur, des nouveaux tests et des deux restaurations ont été comparés aux empreintes des sources cumulatives locales : correspondance exacte.
- Windows Actions `40036951473` sur le commit `6d139ceb99c5bb710db4e4f32c8e723cc82918e3` : **SUCCESS**, 439 tests, 16 ignorés, 0 échec ; PyInstaller x64, Inno Setup 6.7.1 et smoke portable/installation PASS. Artefact 12537082900, SHA-256 vérifiés après récupération.

## Limites

Aucun test de fidélité Microsoft Visio desktop sur fichiers réels. Aucun screenshot Windows V42.85 réel. ZIP historique V43.4 absent ; pas de comparaison exhaustive. Version interne de l'application : `42.50.0` (V42.85 est un candidat source). Tests unitaires et intégration mélangés dans le total cumulatif ; les résultats ciblés sont séparés. Pas de secrets ni changement de production.

## Suite

Restaurer les 54 tests historiques manquants, exécuter la suite complète dans un checkout GitHub Windows, constituer un corpus Visio réel et harmoniser la version interne.
