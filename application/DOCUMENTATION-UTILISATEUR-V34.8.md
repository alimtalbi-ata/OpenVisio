# OpenVisio v34.9 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Comparateur SAN
Ouvrir **Analyse SAN > Comparaison**. Le bandeau de catégories permet de sélectionner **Tout**, **Comparer**, **Connectivité** ou **Applications**. Les résultats restent dans le document : les catégories filtrent seulement les raccourcis de navigation. La recherche de section reste disponible.

## Compilation Windows
Sur Windows x64, lancer `Build-OpenVisio-Windows.cmd` à la racine. La construction exige une connexion réseau pour les prérequis. L'EXE attendu se trouve sous `dist\installer\OpenVisio-Setup-v34.9-x64.exe`. Le script doit encore être validé sur un poste Windows réel.

## Limites
Aucune compilation .NET ni installation réelle Windows n'a été exécutée dans cet environnement. Les analyses SAN sont déclaratives et ne pilotent pas les équipements.
