# OpenVisio v32.5 — Windows Desktop
Auteur : Abdelhalim Talbi

## Installer et ouvrir
Sur Windows x64, installer .NET 8 SDK pour compiler et Inno Setup 6 pour générer le programme d’installation. Exécuter `Build-Windows-EXE.cmd`, puis `Build-Windows-Installer.cmd`. Le runtime Microsoft Edge WebView2 est nécessaire sur la machine cible.

## Documents
Le menu Fichier > Ouvrir un document utilise le champ JSON principal de l’éditeur, plutôt que le premier champ fichier arbitraire. Seuls les documents `.json` et `.ovjson` sont ouverts depuis ce menu; pour les autres formats, utiliser les fonctions d’import spécialisées de l’éditeur. La taille maximale est 20 Mo. Les documents récents sont conservés dans `%LOCALAPPDATA%\OpenVisio\recent.json` et filtrés si le fichier a été supprimé.

L’installateur enregistre l’extension `.ovjson` pour le compte courant et accepte l’ouverture par double-clic. Le packaging embarque les pages HTML additionnelles.

## Limites
Compilation et recette graphique Windows non exécutées dans cet environnement. Les tests JavaScript ne garantissent pas la compatibilité WebView2 ni la réussite du packaging Inno Setup.
