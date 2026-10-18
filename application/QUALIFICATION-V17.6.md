# Qualification OpenVisio v17.6
Auteur : Abdelhalim Talbi

- Tests Node.js : 701/701 PASS (voir commande `npm test`).
- Syntaxe JS : `node --check src/spatial-routing.js` PASS.
- Benchmark synthétique : `node tests/benchmark-v176.mjs` ; résultats dans BENCHMARK-V17.6.json. Le benchmark mesure seulement des recherches spatiales et pas la fluidité SVG ou Windows.
- Index cache WeakMap : les routes doivent être fournies dans une nouvelle Map lorsqu’elles changent, sinon l’index serait périmé.
- Compilation EXE Windows : non réalisée.
- Captures d'écran réelles v17.6 : non réalisées. Les snapshots historiques ne sont pas des captures de cette version.
