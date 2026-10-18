# Audit OpenVisio v37.0
Auteur : Abdelhalim Talbi

## Architecture
L'application demeure un shell WinForms .NET 8 et WebView2 autour d'une interface web monolithique. Les modules SAN sont partiellement découplés, mais le dialogue principal et la coordination des états sont encore complexes.

## Anomalie corrigée
Le moteur de redondance construisait un `Map` des nœuds sans signaler les identifiants dupliqués. Le dernier nœud écrasait silencieusement les précédents. Désormais les IDs de nœuds absents/dupliqués et les IDs de liens dupliqués sont diagnostiqués; les auto-boucles sont averties.

## Risques résiduels
- Le diagnostic sur JSON importé n'est pas automatiquement relié au document actif.
- Les tests Node ne prouvent ni la compilation C# ni le bon fonctionnement WebView2.
- Le portable mono-EXE dépend du runtime WebView2 et peut extraire ses ressources en cache.
- Les scripts de build Inno Setup/.NET doivent être exécutés sur Windows et les rapports conservés.

## Captures
Aucune capture réelle Windows produite dans cet environnement. Ne pas interpréter les schémas conceptuels comme captures.
