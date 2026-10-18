# Qualification OpenVisio v26.7

Auteur : Abdelhalim Talbi

- Node.js : 1175/1175 tests réussis.
- Comparaison v26.5/v26.7 : trois fixtures avec géométrie identique après correction de la marge spatiale (8 px).
- Benchmark : 25 itérations par moteur et par fixture, après 5 échauffements.
- Mesures indicatives, dépendantes de la machine ; ne prouvent pas un gain universel.
- Qualification Windows graphique : non exécutée.
- Captures : historiques uniquement, aucune nouvelle capture Windows.

## Résultats comparatifs (médianes en ms)

- sparse: ancien 1.642, nouveau 1.464, ratio 1.12x
- multiwall: ancien 1.005, nouveau 0.867, ratio 1.16x
- dense: ancien 1.170, nouveau 0.993, ratio 1.18x
