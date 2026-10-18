# OpenVisio v33.0 — Guide Windows
Auteur : Abdelhalim Talbi

## Construire l'installateur
Sur Windows x64 avec Internet, double-cliquer `Build-OpenVisio-Windows.cmd`. Le script prépare .NET SDK 8, Inno Setup 6 via winget et le runtime WebView2, puis compile l'application et l'installateur. Le résultat attendu est `dist\installer\OpenVisio-Setup-v33.0-x64.exe`. La compilation requiert des droits suffisants pour installer Inno Setup ; `winget` doit être disponible. Aucun exécutable précompilé n'est livré dans cette archive source.

## Installer
Exécuter le setup sur Windows x64. Le setup demande les droits administrateur et installe WebView2 silencieusement si absent. La réussite de cette procédure reste à qualifier sur un vrai poste Windows.

## Utiliser
Barre principale : fichier/édition et analyse/export. Ruban : sélection, formes, affichage. En bas à droite, « Espaces spécialisés » donne accès aux recommandations SAN, projection et simulation avant/après.
