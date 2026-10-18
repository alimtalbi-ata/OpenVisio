## OpenVisio v27.8 — Recommandations SAN déterministes

- Ajout de `src/san-recommendations.js`, moteur déclaratif en lecture seule pour classer les corrections et expliciter leurs dépendances.
- Détection des conflits de corrections sélectionnées, prérequis manquants/non sélectionnés, blocages et cycles de dépendances.
- Gains estimatifs limités aux corrections sélectionnées et admissibles ; valeurs négatives, non finies ou invalides ramenées à zéro.
- Ordre des prérequis déterministe ; export CSV protégé contre les formules de tableur.
- Tests dédiés : sélection, conflits, dépendances, cycles, déterminisme, données invalides, absence de mutation et CSV.
- Portée : moteur de recommandation exportable/testable ; aucune exécution de correction SAN ni découverte active des équipements.
- Qualification Windows réelle et nouvelles captures non exécutées dans cet environnement ; snapshots historiques conservés et signalés comme tels.
- Auteur : Abdelhalim Talbi.

