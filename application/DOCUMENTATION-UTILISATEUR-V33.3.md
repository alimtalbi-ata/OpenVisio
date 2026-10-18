# OpenVisio v33.3 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Espaces de travail
Édition : priorité au diagramme. Analyse SAN : diagnostics et panneaux SAN. Avancé : toutes les commandes.

## Accès rapide
Le bandeau propose Créer, SPOF SAN, Zoning, Tous les outils. Ctrl+K reste disponible pour rechercher une commande.

## Compilation Windows
Sur Windows x64, exécuter `Build-OpenVisio-Windows.cmd`. Le script requiert Internet pour télécharger .NET 8, Inno Setup (via winget) et WebView2. Résultat attendu : `dist/installer/OpenVisio-Setup-v33.3-x64.exe`. Le SHA256 est affiché. Le SDK .NET sert uniquement à construire ; l'EXE est publié en self-contained.

## Limitations
La compilation Windows et les tests graphiques n'ont pas été exécutés dans cet environnement. Le résultat est une archive source et non un EXE précompilé.
