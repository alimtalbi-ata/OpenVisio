# Qualification OpenVisio v16.9
Auteur : Abdelhalim Talbi

- 661/661 tests Node.js réussis.
- Syntaxe routing.js et renderer.js : valide.
- Benchmarks orthogonaux Node.js : voir BENCHMARK-V16.9.json.
- 100 nœuds / 99 liens : 22,51 ms ; 500 / 499 : 2,24 ms ; 1000 / 999 : 4,23 ms (une exécution, valeurs non garanties).
- Limite : les grands diagrammes ne font pas l'analyse exhaustive des croisements ; l'optimisation visuelle peut être moins bonne.
- Limite : aucun benchmark du DOM SVG ni des liens smart avec obstacles ; aucune mesure de réactivité Windows.
- Limite : aucun EXE Windows compilé ni capture réelle de l'interface v16.9. Les images historiques du dossier snapshots ne sont pas des captures de v16.9.
