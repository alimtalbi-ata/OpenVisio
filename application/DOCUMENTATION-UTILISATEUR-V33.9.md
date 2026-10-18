# OpenVisio v33.9 — Guide Windows
Auteur : Abdelhalim Talbi

## Construction
Sur Windows x64, lancer `Build-OpenVisio-Windows.cmd` dans le dossier racine. Une connexion Internet est requise pour .NET SDK 8, Inno Setup et WebView2. Le script produit `dist\installer\OpenVisio-Setup-v33.9-x64.exe` en cas de réussite.

## Installation
Exécuter l’installateur en administrateur. L'application est publiée en .NET self-contained ; le SDK .NET n'est pas requis chez l'utilisateur final. L'installateur embarque le runtime WebView2 et le lance en mode silencieux lorsqu'il n'est pas détecté.

## Limites de qualification
Le build Windows, la signature du livrable et l'installation complète ne sont pas testés dans l'environnement Linux de production de cette archive. Les tests Node ne prouvent pas la compatibilité Windows.
