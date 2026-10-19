# OpenVisio V42.4 — Transactions documentaires et livraison cumulative

**Auteur : Abdelhalim Talbi.**

## Livrable unique
L'archive `OpenVisio-v42.4-Windows-Cumulative.zip` contient :
- `01-Application/binary/` : exécutable Windows portable et installateur Inno Setup ;
- `02-Compilation/` : scripts et dépendances de compilation Windows ;
- `03-Sources/` : sources Python et point d'entrée ;
- `04-Tests/` : tests unitaires et scripts de recette Windows ;
- `05-Documentation/` : guides DOCX/PDF générés et notes techniques ;
- `06-Historique/` : provenance et références GitHub ;
- `07-Manifestes/` : empreintes SHA-256 et tailles des binaires.

## Changements V42.4
La récupération d'une version antérieure devient une transaction réversible. `document_transactions.replace_document` valide les deux versions, conserve les changements courants dans l'historique puis applique une copie indépendante du document récupéré. La lecture de sauvegarde est encapsulée dans `document_recovery`, ce qui permet des tests sans interface graphique.

## Contrôles
Les tests couvrent la réversibilité, l'absence d'aliasing, les sauvegardes atomiques, l'intégrité des liaisons et la cohérence de la sélection. GitHub Actions Windows construit les deux exécutables, les documents, le ZIP cumulatif et effectue des smoke tests de l'application portable et de l'installation silencieuse.

## Limites
Le `.bak` reste une sauvegarde précédente unique. La restauration n'est pas une fusion. Les tests automatisés ne remplacent pas une qualification ergonomique sur un PC Windows tiers. Ne jamais utiliser une illustration fictive comme capture réelle.

## Prochaines versions
V42.5 : service documentaire complet et erreurs injectables ; V42.6 : bibliothèque d'équipements infrastructure et modèles ; V42.7 : import/export avec rapport de fidélité ; V42.8 : rendu incrémental et performance ; V42.9 : accessibilité, navigation clavier et qualification Windows approfondie.
