# OpenVisio v29.4 — Guide de la matrice SPOF
Auteur : Abdelhalim Talbi

Module `src/san-spof-priority.js` : `buildSpofRiskMatrix(document)` produit les risques P1–P4 par cible de défaillance documentaire. `spofRiskCsv(report)` exporte le résultat.

P1 : perte modélisée affectant une application ou au moins 3 couples ; P2 : autre perte ; P3 : dégradation seule ; P4 : aucune perte/dégradation démontrée. Ces seuils sont indicatifs et ne représentent pas une sévérité de production.

La matrice exploite les objets documentés et les simulations existantes ; aucune connexion aux équipements, aucune remédiation et aucune validation réelle du multipathing.

La fonction n'est pas encore câblée au panneau graphique : intégration UI à qualifier ultérieurement.

Snapshots : aucune nouvelle capture Windows réelle. Les captures historiques ne prouvent pas la qualification de cette version.
