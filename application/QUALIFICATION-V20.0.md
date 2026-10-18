# Qualification OpenVisio v20.0
Auteur : Abdelhalim Talbi

## Portée
Consolidation transactionnelle de l'inspecteur : validation préalable des ports, propriétés SAN et champs simples, sans mutation ni entrée Annuler/Rétablir pour les valeurs identiques ou invalides. Les connexions utilisant un port supprimé restent protégées.

## Résultats
- `npm test` : **836/836 PASS** (tests Node.js).
- Six nouveaux tests `tests/v200.test.mjs` vérifient le refus de suppression de port connecté, l'application atomique, les opérations sans changement, le rejet d'entrées invalides et les refus d'application.
- Historique des tests antérieurs conservé.

## Limites
- Aucune validation interactive sous Windows ni compilation EXE réalisée ici.
- Les captures incluses dans `snapshots/` sont historiques : aucune nouvelle capture réelle v20.0.
- La qualification end-to-end de l'inspecteur dans le navigateur et la synchronisation visuelle SVG restent à réaliser.
