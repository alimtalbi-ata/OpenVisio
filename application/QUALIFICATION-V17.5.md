# Qualification OpenVisio v17.5

Auteur : Abdelhalim Talbi

- Test de collision segment/rectangle (Liang-Barsky), évitant les faux positifs du seul rectangle englobant.
- 7 tests supplémentaires (`tests/v175.test.mjs`).
- Benchmark synthétique : `BENCHMARK-V17.5.json`, 25 itérations par taille.
- Résultat : l'analyse spatiale est PLUS LENTE que le recalcul direct dans ces scénarios orthogonaux très simples ; aucun gain utilisateur n'est revendiqué. Le calcul incrémental est surtout pertinent si le routage global coûte davantage.
- Le benchmark exclut le navigateur, le DOM SVG, les heuristiques globales et la fluidité du glisser-déposer.
- Aucun exécutable Windows compilé dans cet environnement.
- Aucune capture réelle v17.5 : les images historiques conservées ne sont pas des preuves de qualification graphique v17.5.
- Documentation utilisateur et Windows mise à jour.
