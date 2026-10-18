OpenVisio v41.40 — Diagnostic géométrique intégré

Auteur : Abdelhalim Talbi

Portée : qualification des routes finales du rendu SVG, sans modification du tracé ni des alertes de câblage.

Implémentation : renderer.js importe inspectRouteClearance ; chaque connexion valide sa route finale contre les équipements autres que ses deux extrémités.

API : lastRouteClearanceDiagnostics(svg) retourne une copie indépendante contenant checked, invalid et edges avec les anomalies par segment.

Limites : les segments d’ancrage physiques peuvent être non orthogonaux ; une intersection géométrique n’est pas toujours une anomalie métier. Aucun marquage visuel automatique.

Tests : 1785/1785 tests Node.js réussis, dont quatre tests v41.40. DOM simulé, pas de validation navigateur ni Windows.

Qualification future : obstacles tangents, ports physiques, faux positifs, cas de chemins impossibles, captures réelles Windows.
