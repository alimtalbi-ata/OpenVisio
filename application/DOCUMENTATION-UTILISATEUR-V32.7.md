# OpenVisio v32.7 — Application Windows
Auteur : Abdelhalim Talbi

## Correctif principal
L’ouverture d’un document passé en argument (double-clic .ovjson) attend désormais que la navigation WebView2 soit terminée, avec une limite de 20 secondes. Le rechargement de la page réinitialise le signal de disponibilité. Le statut indique les erreurs de chargement.

## Construire sur Windows
Exécuter `Build-Windows-EXE.cmd` avec le SDK .NET 8, puis `Build-Windows-Installer.cmd` avec Inno Setup 6. Le runtime WebView2 est requis sur la machine cible.

## Limites de qualification
Tests JavaScript réalisés sous Linux. Aucune compilation .NET ni exécution graphique Windows dans cet environnement ; aucun EXE ni installateur compilé fourni.
