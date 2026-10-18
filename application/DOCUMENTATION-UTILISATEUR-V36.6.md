# OpenVisio v36.6 — Windows
Auteur : Abdelhalim Talbi.

Lancer `Build-OpenVisio-Windows.cmd` sur Windows x64 pour produire l’installateur et la version portable `dist\portable\OpenVisio-v36.6-Windows-x64-Portable.exe`. Le portable requiert WebView2 Runtime sur le poste et extrait les ressources dans `%LOCALAPPDATA%\OpenVisio\assets\36.6` au premier démarrage. L’installateur utilise une publication séparée et continue de livrer les assets sous `wwwroot`. Aucun binaire Windows n’a été compilé dans l’environnement Linux de préparation.
