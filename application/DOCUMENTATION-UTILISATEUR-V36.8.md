# OpenVisio v36.8 — Windows

Auteur : Abdelhalim Talbi.

Construire avec `Build-OpenVisio-Windows.cmd` sur Windows x64. La version portable embarque les ressources et les extrait dans `%LOCALAPPDATA%\OpenVisio\assets\36.8`. Un mutex interprocessus sérialise la publication et une empreinte SHA-256 de l’archive intégrée invalide le cache lorsque son contenu change. Le runtime WebView2 reste nécessaire.

Les exécutables Windows ne sont pas fournis dans cette archive source.
