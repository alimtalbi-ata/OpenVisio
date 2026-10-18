# OpenVisio v33.8 — Guide Windows
Auteur : Abdelhalim Talbi

1. Extraire le ZIP sur un poste Windows x64 disposant d’Internet.
2. Lancer `Build-OpenVisio-Windows.cmd`. Le script télécharge .NET SDK 8 dans `dist/build-tools`, cherche/installe Inno Setup via winget, télécharge le runtime WebView2 et compile l’application.
3. Si la construction réussit, récupérer `dist/installer/OpenVisio-Setup-v33.8-x64.exe`.
4. Lancer l’installateur en tant qu’administrateur; il doit installer WebView2 si nécessaire.
5. Tester création, ouverture `.ovjson`, sauvegarde, export, menu SAN et désinstallation.

**Attention :** aucun installateur compilé ni recette native Windows n’est fourni dans ce ZIP source. Les téléchargements nécessitent une connexion Internet, et l’installation Inno Setup via winget peut dépendre des stratégies de l’entreprise.
