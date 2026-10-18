OpenVisio v39.6 — Addendum utilisateur et technique

Auteur : Abdelhalim Talbi

Nouveau : Ctrl/Cmd+S pour enregistrer en JSON, Ctrl/Cmd+O pour ouvrir, Ctrl/Cmd+N pour créer un diagramme.

Les commandes déclenchent les actions existantes et leurs confirmations. Aucun raccourci n’intercepte un dialogue modal ouvert.

Compilation Windows : exécuter Build-OpenVisio-Windows.cmd avec le SDK .NET 8, WebView2 et Inno Setup selon les prérequis du manuel.

Architecture : module src/primary-shortcuts-v395.js importé dans src/main.js ; les raccourcis sont mappés vers les identifiants des boutons.

Qualification : tests Node.js ; compilation et captures réelles Windows non effectuées.