# OpenVisio v41.50 — Qualification Windows

Auteur : Abdelhalim Talbi.

## Modifications
- Manifest de livraison commun aux deux binaires (installateur et portable) avec tailles et SHA256 indépendants.
- Échec bloquant si un artefact est absent, trop petit ou ne commence pas par la signature MZ.
- Remplacement contrôlé du portable existant et affichage de son empreinte SHA256.
- Contrôles de régression statiques sur la chaîne de livraison.

## Limites
Les vérifications MZ ne constituent ni une validation Authenticode ni un test d'exécution. La compilation, l'installation et la recette graphique Windows doivent être effectuées sur une machine Windows.

## Exécution Linux
- npm test: code retour 1.
- node windows/verify-release.mjs: code retour 0.
