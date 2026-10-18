# OpenVisio v32.4 — Application Windows
Auteur : Abdelhalim Talbi

## Installation
Sur Windows x64, installer le SDK .NET 8 pour compiler et le runtime WebView2 pour exécuter. Lancer `Build-Windows-EXE.cmd` puis `Build-Windows-Installer.cmd` avec Inno Setup 6. L’utilisateur final n’a pas besoin du SDK lorsque l’application a été publiée en mode autonome.

## Commandes Windows
Fichier > Ouvrir (Ctrl+O) ouvre le dialogue Windows et remet le document au premier champ d’import de la page. Fichier > Enregistrer/Exporter (Ctrl+S) transmet le raccourci à l’éditeur ; lorsqu’un téléchargement est produit, une boîte de dialogue Enregistrer sous Windows permet de choisir la destination. La liste des fichiers récents ne conserve que les documents ouverts pendant la session.

## Limites
L’intégration d’import dépend de l’existence d’un input[type=file] dans l’éditeur et de son gestionnaire de changement ; les formats reconnus dépendent du moteur web. Les fichiers sont limités à 20 Mo. La persistance des récents et l’association .ovisio restent à développer. Aucun EXE Windows compilé ni capture réelle n’a été obtenu dans cet environnement Linux.
