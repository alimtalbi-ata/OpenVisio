# Audit OpenVisio v37.8 — domaines de défaillance corrélés

Auteur : Abdelhalim Talbi.

Le moteur SAN simule désormais la perte simultanée de tous les éléments déclarés avec une même valeur de `site`, `chassis`, `powerDomain`, `controller` ou `failureDomain`. Les champs sont facultatifs et les résultats ne peuvent refléter que la topologie documentée. Les extrémités serveur et baie sont exclues du calcul d’indépendance des transits.

Limites : absence de découverte physique, de validation zoning/multipath, de compilation Windows et de captures natives dans cet environnement. Le diagnostic n'est pas une preuve d'indépendance réelle.
