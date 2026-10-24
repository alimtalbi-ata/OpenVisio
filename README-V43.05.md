# OpenVisio V43.05 — Groupes Visio transparents

Auteur : Abdelhalim Talbi.

Correction : les groupes importés n'interceptent plus les clics dans leur intérieur. Les équipements et connexions SAN restent sélectionnables, le contour de groupe conserve son hit-test et la tolérance est bornée selon le zoom.

Qualification locale : 574 tests Python (22 ignorés), 0 échec. Six nouveaux tests de régression.

Les modules moteur `python/openvisio/render.py`, `python/openvisio/app.py` et leurs miroirs `03-Sources/openvisio` sont publiés sur la branche dédiée, avec les tests dans `python/tests` et `04-Tests/tests`.

CI Windows V43.05 : ne pas annoncer de succès avant résultat réel. Fidélité Microsoft Visio Desktop et recette interactive Windows non qualifiées. ZIP V43.4 original absent. Aucune fusion automatique.
