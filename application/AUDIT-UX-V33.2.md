# Audit UX v33.2 — OpenVisio

## Constats vérifiés dans les sources
- La page principale concentre les contrôles d’édition, les diagnostics SAN et de nombreux panneaux de rapport dans un DOM volumineux.
- La recherche de commandes v33.1 améliore la découverte mais ne réduit pas la densité visuelle.
- Les analyses SAN sont actuellement des sections extensibles mêlées à l’espace d’édition.

## Mesures v33.2
- Navigation par modes Édition / Analyse SAN / Outils avancés, avec préférence persistante.
- Masquage visuel non destructif des principaux panneaux SAN en mode Édition.
- Les commandes SAN du lanceur changent automatiquement d’espace avant l’action.
- Préservation des ID et de la logique métier existante pour limiter les régressions.

## Limites / dette technique
- La page HTML demeure monolithique et nécessite une refactorisation par composants.
- La navigation avancée n’est pas encore un espace dédié complet.
- L’EXE et le setup n’ont pas été compilés sur Windows ici.
- Les captures Windows réelles sont indisponibles.
