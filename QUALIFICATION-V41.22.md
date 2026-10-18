OpenVisio v41.22 — Qualification du rendu SVG

Auteur : Abdelhalim Talbi

Périmètre

Version construite depuis le ZIP v41.21. Ajout de quatre tests du DOM SVG simulé : rendu répété, déplacement et undo/redo, suppression/restauration de câble, diagnostics du cache.

Résultats

Suite Node.js : 1 759 tests réussis sur 1 759. Tests spécifiques v41.22 : 4 sur 4.

Limites de qualification

Les tests utilisent un DOM JavaScript simulé : aucune preuve de fluidité Windows, de paint réel, de performance des obstacles complexes ou de qualité visuelle. Le benchmark SVG historique a été lancé, mais aucun résultat exploitable n’a été obtenu dans le délai disponible.

Reproduction

Depuis application : node --test tests/*.test.mjs ; node --test tests/svg-render-v4122.test.mjs

Prochaines étapes

Exécuter une campagne navigateur automatisée sur les vrais diagrammes SAN, avec captures réelles, mesures de latence et comparaison des géométries.