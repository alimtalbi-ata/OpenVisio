# OpenVisio v32.2 — Application de bureau Windows
Auteur : Abdelhalim Talbi

## Nouveauté
Le programme .NET est désormais une fenêtre Windows WinForms autonome utilisant WebView2 intégré. Il ne lance plus de serveur HTTP et n’ouvre plus le navigateur externe. Les sources de l’éditeur existant restent inchangées.

## Construction sur Windows
Prérequis de compilation : SDK .NET 8, accès au paquet NuGet Microsoft.Web.WebView2. Lancer `Build-Windows-EXE.cmd`.
Le binaire est généré dans `dist/windows-x64/OpenVisio.exe` avec le dossier `wwwroot` contenant les ressources. Ne pas déplacer l’EXE sans ses ressources.

## Exécution
Windows x64 avec Microsoft Edge WebView2 Runtime installé. Le .NET runtime n’est pas nécessaire pour la publication self-contained. Double-cliquer `OpenVisio.exe`. Menus natifs Fichier, Édition, Affichage, Aide. L’éditeur est affiché dans une fenêtre Windows dédiée.

## Limites
Cette archive fournit le code de l’application native et le script de compilation, **pas un EXE déjà compilé**. Aucun SDK .NET ni environnement Windows n’est disponible dans l’environnement de génération, donc ni compilation Windows ni captures réelles n’ont été effectuées. Les menus d’édition déclenchent des événements clavier et leur comportement dépend des raccourcis pris en charge par l’éditeur. La persistance et les dialogues natifs doivent être qualifiés sur Windows.
