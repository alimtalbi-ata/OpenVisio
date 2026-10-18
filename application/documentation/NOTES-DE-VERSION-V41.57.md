# Notes v41.58

OpenVisio v41.58 : distribution binaire Windows. Les sorties de compilation restent dans dist/windows-x64, dist/installer et dist/portable. Le nouveau script Stage-Binaries.ps1 copie les deux vrais EXE dans application/binary et produit un manifeste SHA256, uniquement apres compilation et controles. Aucun EXE compile ici : hote Linux sans SDK .NET ni Inno Setup. Auteur : Abdelhalim Talbi.
