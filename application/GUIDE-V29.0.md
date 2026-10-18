# OpenVisio v29.0 — rapport d’impact SAN
Auteur : Abdelhalim Talbi

Module `src/san-impact-report.js` : `buildSanImpactReport(document, {failedFabric: "A"})` ou `{failedNodeId: "switch-id"}`. Résultat : chemins perdus/conservés, paires serveur/baie impactées, avertissements de redondance, identifiants des liens à colorer. `sanImpactCsv(report)` exporte les paires impactées.

**Important** : les listes `visual` constituent des données de projection, pas une surbrillance automatiquement connectée au canvas. Les chemins documentaires ne prouvent pas le multipathing réel. Les résultats tronqués doivent être considérés comme incomplets. Aucune action SAN réelle.

## Captures
Aucune nouvelle capture Windows réelle réalisée. Aucun aperçu statique présenté comme capture. Qualification visuelle Windows à effectuer.
