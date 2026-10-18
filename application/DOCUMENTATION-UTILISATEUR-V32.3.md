# OpenVisio v32.3 — Application de bureau Windows
Auteur : Abdelhalim Talbi

## Construire
1. Sur Windows x64, installer le SDK .NET 8 et le runtime Microsoft Edge WebView2.
2. Lancer `Build-Windows-EXE.cmd` : sortie `dist/windows-x64/OpenVisio.exe` avec `wwwroot`.
3. Pour un installeur, installer Inno Setup 6, puis lancer `Build-Windows-Installer.cmd`.
4. Le package d'installation est écrit dans `dist/installer`.

## Utiliser
Lancer OpenVisio depuis le menu Démarrer ou l'exécutable. L'éditeur fonctionne dans une fenêtre Windows dédiée. Les fichiers exportés par le moteur web sont placés dans le dossier Téléchargements, avec renommage en cas de collision. Le menu Outils permet d'ouvrir les dossiers Documents et Téléchargements.

## Limites
Ce ZIP contient les sources et les scripts de construction, **pas** un exécutable ni un installateur précompilés. Les dialogues de fichiers internes de l'éditeur restent ceux de WebView2. WebView2 Runtime doit être installé sur le poste. Le moteur SAN est une analyse documentaire, pas une interrogation d'équipements.
