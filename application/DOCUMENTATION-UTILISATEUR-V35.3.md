# OpenVisio v35.3 — Guide Windows

Auteur : Abdelhalim Talbi.

Extraire le ZIP sur Windows x64 puis exécuter `Build-OpenVisio-Windows.cmd`. Le script contrôle les fichiers, les versions, la syntaxe PowerShell et les références locales HTML avant téléchargement des dépendances. Il prépare .NET 8, Inno Setup et WebView2, puis compile l’application et son installateur.

Livrables attendus : `dist/windows-x64/OpenVisio.exe` et `dist/installer/OpenVisio-Setup-v35.3-x64.exe`. Vérifier ensuite sur Windows installation, ouverture, édition, enregistrement, export et désinstallation.

Les tests JavaScript ne remplacent pas une qualification Windows native.
