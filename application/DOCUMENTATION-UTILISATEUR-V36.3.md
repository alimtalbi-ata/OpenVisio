# OpenVisio v36.3 — Diagnostic SAN redondant

Auteur : Abdelhalim Talbi.

Nouveau module de diagnostic en lecture seule `src/san-redundancy-v363.js` : vérification des chemins indépendants Fabric A et Fabric B, détection des liens orphelins, incohérences de Fabric et zoning incomplet.

Le module est une API de diagnostic testée sur une topologie synthétique, pas encore intégré au tableau de bord. Il ne remplace pas une validation de zoning réelle sur les commutateurs.

Sur Windows x64, lancer `Build-OpenVisio-Windows.cmd` pour tenter de construire l’application et l’installateur, puis `Qualify-OpenVisio-Windows-Functional.cmd` pour la recette. Les exécutables Windows ne sont pas construits dans cette livraison source.
