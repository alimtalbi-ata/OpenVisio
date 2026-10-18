# OpenVisio v41.18 — Qualification comparative du cache
Auteur : Abdelhalim Talbi

La comparaison mesure des opérations de cache **synthétiques**, et non le rendu Windows. Les modes full-clear et targeted-delete ne font pas le même travail : le second conserve 50 % des routes. Leurs temps ne constituent donc **pas** une mesure de gain de rendu équivalent. Les topologies SAN réelles, les captures Windows et la comparaison géométrique restent non qualifiées.

Exécuter `npm test` et `npm run benchmark:cache-comparison` dans application/. Les résultats d'une exécution sont conservés dans `BENCHMARK-CACHE-V41.18.json`.

Résultat de la suite complète : 1751 tests réussis / 1751 (Node.js v22.16.0). Le package.json conserve la version historique 41.0.0 pour compatibilité avec les tests de synchronisation ; dette de versionnement à traiter.
