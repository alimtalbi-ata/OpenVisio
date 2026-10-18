# OpenVisio v37.8 — guide complémentaire

Auteur : Abdelhalim Talbi.

Pour documenter les risques corrélés, renseigner sur les nœuds et liens SAN les champs optionnels `site`, `chassis`, `powerDomain`, `controller` ou `failureDomain` (chaînes de caractères). Deux composants partageant la même valeur dans le même champ appartiennent au même domaine de panne. L’analyse SAN produit `commonCriticalDomains` et marque `SHARED_RISK` si la perte simultanée du domaine coupe les deux Fabrics.

Exemple : deux commutateurs SAN différents partageant `powerDomain: "PDU-01"` peuvent être redondants en apparence mais dépendre d’une alimentation commune.

Construire sous Windows via `Build-OpenVisio-Windows.cmd`. Les exécutables ne sont pas inclus dans le ZIP source.
