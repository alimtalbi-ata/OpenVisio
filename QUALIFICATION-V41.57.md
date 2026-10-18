# OpenVisio v41.58 — Audit du pipeline Windows

Auteur : Abdelhalim Talbi

## Chemins effectifs avant correction
- Application native : `application/dist/windows-x64/OpenVisio.exe`
- Installateur Inno Setup : `application/dist/installer/OpenVisio-Setup-v41.58-x64.exe`
- Portable mono-EXE : `application/dist/portable/OpenVisio-v41.58-Windows-x64-Portable.exe`

## Nouveau répertoire de distribution
- `application/binary/` reçoit les deux EXE uniquement après compilation réussie, vérification taille et en-tête MZ, puis calcule leurs SHA256 dans `manifest.json`.
- Un échec de compilation bloque la livraison, sans créer de faux exécutables.
- Commande unique : `application/Build-OpenVisio-Windows.cmd` sur Windows.

## Limites
Aucun binaire `.exe` compilé sur cet hôte Linux (absence de SDK .NET, Inno Setup et Windows). Aucune recette Windows réelle exécutée. Le répertoire `binary` contient seulement un README explicatif.
