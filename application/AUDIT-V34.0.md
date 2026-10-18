# OpenVisio v34.2 — Audit de livraison Windows

Auteur : Abdelhalim Talbi.

## Défaut bloquant identifié
Le workflow Windows v33.9 invoquait `Build-Windows-EXE.cmd` puis Inno Setup sans télécharger le prérequis WebView2 inclus par `[Files]` dans le script Inno. Le pipeline pouvait échouer à compiler l’installateur même si la compilation de l’application réussissait. De plus, le workflow ne réutilisait pas le script unique de construction demandé.

## Correction
Le workflow exécute désormais `Build-OpenVisio-Windows.cmd` comme seule entrée de compilation, contrôle le prérequis signé Microsoft, vérifie l’installateur versionné, puis publie les deux artefacts. Le script reste soumis aux contraintes de connectivité et d’installation des outils Windows.

## Risques résiduels
- Le téléchargement du SDK .NET et d’Inno Setup nécessite Internet, `winget` et les permissions nécessaires.
- Le bootstrapper WebView2 est empaqueté mais la réussite de son installation silencieuse n’a pas été vérifiée sur Windows.
- Aucun test d’installation/désinstallation de bout en bout n’a été exécuté ici.
- L’interface nécessite encore une recette visuelle réelle.
- Les tests Node vérifient des invariants et des modules JS ; ils ne démontrent pas la compilation C# ou Inno Setup.
