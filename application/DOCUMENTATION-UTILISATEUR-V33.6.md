# OpenVisio v33.6 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Inspecteur
Sélectionner un objet, puis utiliser « Propriétés de la sélection » pour replier ou déplier les champs. Le repli ne supprime aucune donnée et la préférence est conservée localement. Le bouton Propriétés de la barre d’outils permet de déplier à nouveau. Les filtres Essentiel / Toutes les propriétés et la recherche restent disponibles.

## Construction Windows
Exécuter `Build-OpenVisio-Windows.cmd` sur Windows avec accès Internet. Le script prépare le SDK .NET, Inno Setup et le prérequis WebView2, puis produit l’installateur dans `dist/installer/`. Une recette réelle sur Windows reste nécessaire.

## Limites
Aucune compilation Windows ni capture réelle n’a été effectuée dans cet environnement Linux. Les tests automatisés JavaScript ne qualifient pas l’installateur.
