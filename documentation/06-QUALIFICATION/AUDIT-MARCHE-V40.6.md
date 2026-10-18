# Audit comparatif OpenVisio v40.6 — 17 octobre 2026
Auteur : Abdelhalim Talbi.

## Références et méthode
Comparaison fonctionnelle des sources locales v40.5 et des documentations officielles Visio 2024, diagrams.net et yEd. Ce document n'est **pas** un benchmark chronométré, un test UX auprès d'utilisateurs ni une certification de compatibilité.

Sources officielles :
- Microsoft Visio 2024 : https://support.microsoft.com/fr-fr/visio/what-s-new-in-visio-2024
- Microsoft comparatif : https://www.microsoft.com/fr-fr/microsoft-365/visio/visio-plans-and-pricing-one-time-purchase
- diagrams.net : https://www.drawio.com/docs/features/
- yEd : https://www.yworks.com/products/yed/applicationfeatures

## Matrice de maturité (évaluation qualitative, non mesurée)
| Domaine | Référence | OpenVisio v40.5 | Priorité |
|---|---|---|---|
| Bibliothèques et recherche | Visio / diagrams.net | Présentes, ergonomie graphique non qualifiée | P1 |
| Alignement et placement automatique | yEd | Écart probable sur algorithmes et routage | P1 |
| Import/export et interopérabilité | Visio / diagrams.net | JSON et SVG ; fidélité VSDX non démontrée | P0 |
| Sauvegarde native | Visio / diagrams.net | API navigateur conditionnelle, validation WebView2 absente | P0 |
| Récupération | OpenVisio | Empreinte SHA256 et restauration explicite, limites à durcir | P0 |
| Navigation et accessibilité | Visio / yEd | Raccourcis partiels, qualification clavier complète absente | P1 |
| Édition de grands graphes | yEd | Tests automatisés existants, mesures comparables absentes | P1 |
| Validation SAN A/B et SPOF | Spécialité OpenVisio | Fonctionnalités métier présentes, tests terrain à mener | Atout |
| Packaging Windows | Visio / diagrams.net | Sources et scripts, EXE non qualifiés | P0 |

## Correctifs v40.6
1. Rejeter les sauvegardes dont le payload dépasse 25 Mio **avant** SHA256 et JSON.parse.
2. Refuser les dates de création invalides dans les enregistrements vérifiés.
3. Interdire la création de sauvegardes dépassant 25 Mio.
4. Ajouter trois tests ciblés et maintenir les tests existants.

## Feuille de route
P0 : build Windows natif reproductible, tests E2E ouverture/sauvegarde/restauration, validation du format de documents et de la récupération.
P1 : optimisation du rendu et du routage, navigation clavier et accessibilité, bibliothèque contextuelle.
P2 : interopérabilité Visio documentée, liaison de données, fonctions de collaboration selon besoin.

## Limites et preuves
Aucune mesure de temps d'ouverture, de FPS, de consommation mémoire ou de taux de réussite utilisateur n'a été effectuée. Aucun écran Windows réel n'a été capturé. Les sorties CLI illustratives ne constituent pas des preuves.
