# OpenVisio V43.13 — Master precedence & Windows CI

**Auteur : Abdelhalim Talbi.** Version candidate sur branche dédiée, sans fusion dans main.

## Correction fonctionnelle
L'import VSDX externe résout une ambiguïté des stencils SAN : une forme NameU=Sheet.N ou Switch.N et légende générique Switch pouvait être reclassée en LAN malgré un Master Brocade G720 ou Cisco MDS 9148. Le nom spécifique SAN du Master l'emporte désormais sur les libellés génériques. Les identités explicitement OpenVisio network-switch et Network Switch restent protégées.

## Tests
7 régressions synthétiques : 4 échecs sur V43.12, 7 succès après correctif. Suite Python Linux : 631 tests, 28 ignorés, 0 échec. Parité des deux moteurs : 59 fichiers ; parité tests : 143 fichiers. Ces résultats sont locaux et ne certifient pas Microsoft Visio Desktop.

## CI et packaging
Nouveau workflow Windows V43.13 déclenché sur la branche exacte. Le vérificateur clone indépendamment GitHub, contrôle les SHA Git du moteur et des tests, puis lance la suite. Le build PyInstaller + Inno Setup n'est déclaré qualifié que si GitHub Actions réussit. Ne pas recycler les exécutables V43.11/V43.12.

## Limites
L'archive originale V43.4 n'est pas disponible ; la réconciliation historique exhaustive est impossible. Le corpus de VSDX réels, la recette interactive Windows et la fidélité Visio Desktop restent à qualifier.
