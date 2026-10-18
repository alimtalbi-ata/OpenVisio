# OpenVisio v33.5 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Inspecteur contextuel
Sélectionnez une forme ou une connexion. Dans le panneau Inspecteur, choisissez **Essentiel** (propriétés courantes) ou **Toutes les propriétés** (inclut les attributs SAN avancés). Le champ **Filtrer** recherche les propriétés par nom. Les propriétés sont uniquement masquées : aucune donnée n’est supprimée. Les modifications continuent à passer par les commandes existantes de l’éditeur. Le mode d’affichage est mémorisé localement.

## Construction Windows
Depuis un poste Windows connecté à Internet, exécutez `Build-OpenVisio-Windows.cmd`. Le script prépare .NET 8, Inno Setup et WebView2, puis tente de créer `dist\installer\OpenVisio-Setup-v33.5-x64.exe`. Vérifiez les journaux et réalisez un test d’installation avant diffusion.

## Limites
La compilation et la recette native Windows n’ont pas été exécutées dans l’environnement de génération. Aucun EXE précompilé n’est fourni.
