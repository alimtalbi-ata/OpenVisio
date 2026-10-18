# Audit approfondi OpenVisio v36.5
Auteur : Abdelhalim Talbi

## Constats confirmés par lecture du code
1. L’application est un shell WinForms .NET 8 + WebView2 qui charge les ressources web depuis `wwwroot`. `PublishSingleFile=true` fusionne les assemblies .NET, **pas** les fichiers HTML/JS/CSS de `wwwroot` : un unique EXE portable n’est donc pas garanti.
2. La construction dépend de l’accès réseau à dotnet-install, NuGet, Inno Setup via winget et au runtime WebView2. Les signatures du runtime sont vérifiées, mais la disponibilité réseau et le succès du setup Windows doivent être testés sur une VM Windows.
3. L’éditeur HTML et les modules SAN restent fortement couplés aux IDs DOM. Les vues d’analyse sont ajoutées au dialogue existant ; risque de régression à chaque réorganisation.
4. Le shell accepte une liste de formats dans la boîte d’ouverture, mais ne traite nativement que JSON et OVJSON : incohérence UX à corriger.
5. Les contrôles de sauvegarde/export reposent sur les événements clavier simulés et les téléchargements WebView2 ; nécessité de tester les parcours réellement sous Windows.
6. Le runtime WebView2 reste une dépendance externe, y compris pour une distribution portable. Le ZIP portable est sans installation de l’application, mais nécessite WebView2 présent sur la machine.

## Actions v36.5
- Ajout d’un vrai packaging portable à partir de la sortie `dotnet publish`, avec vérification des fichiers critiques.
- Exécution automatique du packaging après construction de l’installateur ; échec bloquant si portable absent.
- Correction de la liste de formats dans la boîte de dialogue native pour éviter les formats non pris en charge.
- Ajout de tests de cohérence et d’un manifeste de limitations.

## Priorités suivantes
- Éliminer le couplage au DOM dans les modules SAN et tester les interactions via navigateur réel.
- Définir un contrat stable de sérialisation / ouverture / export et de compatibilité Visio.
- Étudier l’incorporation de `wwwroot` dans une ressource .NET extraite au premier lancement pour approcher le portable mono-EXE, sans masquer les dépendances.
- Qualification native obligatoire sur Windows x64 : build, démarrage, WebView2, import, export, installer et désinstallation.
