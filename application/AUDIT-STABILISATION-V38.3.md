# OpenVisio v38.3 — Audit de stabilisation

Auteur : Abdelhalim Talbi.

## Correctif confirmé
Le script `windows/Build-Portable-Windows.ps1` produisait un fichier nommé v36.8 quelle que soit la version du projet. Le nom de sortie est maintenant dérivé de `<Version>` dans `windows/native/OpenVisio.csproj`. Deux tests de régression ont été ajoutés.

## Limites de qualification
- Tests Node.js : à consulter dans le rapport de recette.
- Compilation .NET et exécution Windows : non réalisées dans cet environnement.
- Captures d'écran réelles : indisponibles, aucune capture fictive.
- La validation de sauvegarde demeure répartie entre plusieurs chemins. Aucun raccordement complet non vérifié n'est revendiqué.

## Recette Windows à réaliser
Exécuter `Build-OpenVisio-Windows.cmd` sur Windows x64, vérifier l'installateur et le portable, puis tester création, sauvegarde, réouverture, diagnostic SAN et désinstallation.
