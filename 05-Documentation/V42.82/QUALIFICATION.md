# OpenVisio V42.82 — qualification du moteur SAN / VSDX

**Auteur : Abdelhalim Talbi — 23 octobre 2026.**

## Changement fonctionnel
Le parseur VSDX externe refuse désormais les identifiants de feuilles Visio dupliqués lorsqu'ils sont utilisés comme sources de connecteurs SAN dans les relations `Connects` (`BeginX` / `EndX`). Deux connecteurs partageant un ID pouvaient auparavant fusionner silencieusement leurs liens et légendes. Les liens parallèles avec des ID distincts restent préservés. Les doublons d'enfants de groupes non connecteurs conservent leur traitement historique.

## Exécutions locales vérifiées
- Avant correctif : **2/3 tests synthétiques ciblés échouaient**.
- Après correctif : **3/3 PASS**.
- Suite Python 3.13 Linux cumulative : **747 tests, 41 ignorés, 0 échec**.
- Parité bidirectionnelle locale : **57 modules moteur** et **157 fichiers de tests** dans chacun des deux miroirs.
- Les empreintes Git des deux copies du moteur modifié, des deux copies du nouveau test et du test historique restauré correspondent aux fichiers locaux.
- Les copies GitHub de `model.py`, `vsdx.py`, `render.py` ont des SHA Git identiques entre les deux miroirs.

## Publication
- Branche : `develop/v42.82-sanitize-duplicate-san-connectors-20261023`.
- PR : #15, **draft**, ciblant la branche V42.81 ; aucune fusion vers `main`.
- Moteur : `python/openvisio/vsdx_external.py` et `03-Sources/openvisio/vsdx_external.py`.
- Tests : `test_vsdx_duplicate_connector_sheet_v4282.py` dans les deux miroirs.
- Test historique restauré : `test_vsdx_conflicting_connections_v4263.py` dans les deux miroirs.
- **56 tests historiques** restent absents de GitHub par rapport au ZIP local.

## Qualification différenciée
| Domaine | État |
| --- | --- |
| Tests unitaires ciblés synthétiques | 3/3 PASS |
| Suite cumulative Linux (unitaires + intégration) | 747 tests, 41 ignorés, 0 échec ; pas de ventilation fiable |
| GitHub Actions Windows V42.82 | Workflow publié, résultat non encore vérifié |
| Compilation portable/installateur Windows V42.82 | Non exécutée localement, aucun nouveau binaire revendiqué |
| Microsoft Visio réel (import/export) | Non qualifié |
| Captures Windows V42.82 | Absentes ; aucun visuel simulé présenté comme capture réelle |

## Limites et prochaine étape
Le ZIP V43.4 historique est indisponible ; la comparaison exhaustive avec GitHub est bloquée. Le checkout GitHub distant complet n'a pas pu être cloné depuis Linux (DNS), même si des fichiers critiques ont été vérifiés directement sur GitHub. La version interne de l'application reste `42.50.0`. Priorités : CI Windows du HEAD, publication des 56 tests historiques, vraie fidélité Microsoft Visio, harmonisation du versionnement.
