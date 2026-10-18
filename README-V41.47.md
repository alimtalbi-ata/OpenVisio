# OpenVisio v41.47 — Fiabilisation de la livraison Windows

Auteur : Abdelhalim Talbi.

## Évolutions
- Synchronisation 41.47.0 : npm, projet .NET, script CMD, Inno Setup.
- `node windows/verify-release.mjs` contrôle les métadonnées avant publication.
- `Build-Windows-Installer.cmd` délègue à la chaîne unique de compilation.
- Le portable est produit par `windows/Build-Portable-Windows.ps1` lors du build Windows.

## Limites de qualification
La suite Node.js peut être exécutée sous Linux. Cela ne démontre ni la compilation ni l'installation sur Windows.
Les tests historiques à numéros de versions figés demeurent en échec ; ils ne sont pas supprimés.
Aucun exécutable Windows ni capture d'écran réelle n'est fourni.

## Commandes
`cd application && node windows/verify-release.mjs`
`cd application && npm test`
Sur Windows : `application\Build-Windows-Installer.cmd`
