# OpenVisio v41.8 — 05 ARCHITECTURE

## 1. Le moteur de rendu utilise createRouteValueCache, un cache borné par une Map ordonnée en LRU.

## 2. get() actualise la récence et renvoie une copie profonde ; set() clone à l’entrée et à la sortie.

## 3. delete(key) permet une invalidation sélective sans purger les routes indépendantes.

## 4. stats() expose size, hits, misses, evictions, limit et hitRate.

## 5. La liaison transaction -> révision -> invalidation ciblée reste à terminer : les garanties de correction priment sur la performance.

Auteur : Abdelhalim Talbi.
