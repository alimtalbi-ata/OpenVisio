# OpenVisio v39.1 — Livraison documentaire reproductible

Auteur : Abdelhalim Talbi

## Nouveauté
Ajout d’un générateur de manifeste SHA256 générique et d’un contrôle de cohérence des documents. Le manifeste référence les documents inclus et permet de vérifier leur intégrité.

## Procédure de livraison
1. Mettre à jour les sources et les tests.
2. Actualiser le manuel complet si les procédures ont changé.
3. Rédiger les notes de version et l’addendum Word/PDF.
4. Exécuter `node scripts/generate-release-manifest.mjs`.
5. Exécuter `node scripts/verify-release-docs.mjs`.
6. Exécuter `npm test`, puis créer le ZIP cumulatif.

## Qualification
Les exécutables Windows et les captures natives ne sont pas produits dans cet environnement Linux. Les diagrammes existants sont explicatifs et ne sont pas des captures de l’application Windows.
