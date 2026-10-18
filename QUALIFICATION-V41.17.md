# OpenVisio v41.17 — Géométrie et invalidation

Auteur : Abdelhalim Talbi.

Le rendu invalide les connexions incidentes aux équipements modifiés avant le recalcul. Snapshot sérialisé pour détecter les mutations en place. Les changements d’obstacles restent protégés par la signature des clés du cache.

Limites : pas de compilation Windows ni de captures réelles ; benchmark comparatif SAN non exécuté.
