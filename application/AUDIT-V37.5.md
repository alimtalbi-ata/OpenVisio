# OpenVisio v37.5 — Alternatives et éléments critiques SAN

Le diagnostic cherche des chemins alternatifs en supprimant tour à tour les éléments de la route la plus courte de chaque Fabric. Un élément est critique pour une Fabric si sa suppression rend le stockage inaccessible sur cette Fabric. Les boutons « Critiques A/B » mettent en évidence ces éléments. Il ne s’agit que de topologie déclarative, sans état réel des équipements, zoning, masking ni multipathing. Le nombre de routes alternatives découvertes est un nombre de variantes distinctes, pas une énumération exhaustive.

Auteur : Abdelhalim Talbi.
