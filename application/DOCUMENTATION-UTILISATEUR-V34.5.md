# OpenVisio v34.5 — Guide utilisateur

Auteur : Abdelhalim Talbi.

## Interface
Le bouton **? Aide** dans le ruban et la touche **F1** ouvrent une fenêtre des raccourcis clavier. Fermez-la avec le bouton Fermer ou Échap. Les raccourcis d'ouverture et d'enregistrement dépendent du contexte de lancement.

## Installation Windows
Sur un poste Windows x64 connecté à Internet, exécuter `Build-OpenVisio-Windows.cmd` depuis les sources pour préparer le SDK .NET 8, Inno Setup et WebView2 puis construire l'installateur. Ce script nécessite `winget` et des droits appropriés pour installer Inno Setup. Le SDK est nécessaire uniquement au poste de construction, pas à l'utilisateur final.

## Qualification
La suite Node vérifie les fonctions JS et les contrats statiques. La compilation native .NET, l'installation et les captures Windows réelles n'ont pas été effectuées dans cet environnement Linux.
