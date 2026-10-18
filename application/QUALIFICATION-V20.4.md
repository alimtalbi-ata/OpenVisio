# Qualification OpenVisio v20.4
Auteur : Abdelhalim Talbi

## Résultats
- `npm test` : **858 réussis / 858** (Node.js, environnement Linux).
- Trois nouveaux tests : restauration du diagramme et des zones SAN, refus des extras SAN invalides, compatibilité des instantanés antérieurs.
- Archive ZIP : test d’intégrité exécuté.

## Limites
- Aucun test GUI Windows exécuté.
- Aucun exécutable Windows compilé.
- Les captures déjà incluses dans `snapshots/` sont historiques, non représentatives d'une recette Windows v20.4.
- Les données SAN sont validées avant restauration ; la persistance localStorage reste best-effort.
