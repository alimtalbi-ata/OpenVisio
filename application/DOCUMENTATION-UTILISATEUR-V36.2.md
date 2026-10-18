# OpenVisio v36.2 — Guide utilisateur

Auteur : Abdelhalim Talbi.

## Architecture SAN double Fabric

La recette contient un jeu de données **synthétique** avec serveur ESXi multipath, deux switches Fabric A/B, baie et quatre liens. Le test vérifie les chemins redondants, les attributs WWPN, VSAN, zonesets, zoning et LUN. Le jeu de données sert aux tests du comparateur, pas à une démonstration de rendu de l’interface.

## Construction Windows

Depuis Windows x64 : `Build-OpenVisio-Windows.cmd`. Pour qualifier : `Qualify-OpenVisio-Windows-Functional.cmd`. Les prérequis .NET, Inno Setup et WebView2 doivent être vérifiés sur une vraie machine Windows.
