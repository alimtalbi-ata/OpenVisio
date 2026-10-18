# OpenVisio v41.1 — Audit architectural et plan de rationalisation

Auteur : Abdelhalim Talbi

## Périmètre réel
Analyse statique de la base v41.0, sans suppression automatique. 120 modules JS directement dans src/, 120 fichiers JS au total, 172 relations d'import relatif détectées, 26 entrées script/éditeur relevées, 11 modules src/ non atteints par les imports statiques depuis ces entrées. **Non atteignable ne signifie pas inutilisé** : import dynamique, événements et chargement indirect restent possibles.

## Constats et décisions
1. `src/main.js` est un point de concentration à décomposer progressivement en commandes, modèle, rendu et persistance.
2. Les modules suffixés par version doivent être fusionnés dans des modules canoniques après cartographie des appels et comparaison comportementale, jamais supprimés sur leur nom seul.
3. Le routage spatial doit recevoir une révision de graphe explicite et des tests différentiels avant toute optimisation du cache.
4. Les styles CSS doivent être audités pour les collisions de sélecteurs et consolidés dans des composants documentés.
5. Les tests historiques restent utiles comme filet de sécurité, mais peuvent être regroupés par domaine après suppression des redondances démontrées.

## Ordre d'exécution
- v41.1 : cartographie et règles d'architecture (présente livraison).
- v41.2 : modèle documentaire et commandes transactionnelles.
- v41.3 : index spatial versionné, cache invalidé correctement.
- v41.4 : moteur de placement et routage avec métriques de croisements.
- v41.5 : interface simplifiée, inspection et bibliothèque consolidées.
- v41.6 : interopérabilité et fidélité de conversion.
- v41.7 : bibliothèque métier SAN et validation des modèles.
- v41.8 : sauvegarde atomique et récupération.
- v41.9 : benchmark et accessibilité.
- v42.0 : Windows portable/installateur et qualification native.

## Critères de remplacement
Tests fonctionnels équivalents ou meilleurs, compatibilité des documents JSON existants, comparaison de performance reproductible, aucune duplication de logique et rollback documenté.

## Limites
Pas de capture Windows, pas de compilation native, pas de preuve de code mort. Les modules candidats à l'isolement sont répertoriés dans le JSON de l'audit.
