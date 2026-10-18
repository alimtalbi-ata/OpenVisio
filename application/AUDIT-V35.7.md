# Audit v35.7
Tests Node : exécutés sur Linux. La recette Chromium fonctionnelle est intégrée mais doit être exécutée sur Windows pour valider le déploiement. Les opérations de sauvegarde/réouverture/export/SAN nécessitent encore des scénarios dédiés. Le build .NET, Inno Setup et WebView2 ne sont pas qualifiés nativement ici. Auteur : Abdelhalim Talbi.

## Exécution locale Linux
Le scénario Playwright a été tenté avec `/usr/bin/chromium` : échec de navigation `net::ERR_BLOCKED_BY_ADMINISTRATOR` sur `127.0.0.1`. Ce résultat est un blocage de l'environnement de test, et non une preuve de fonctionnement ou de dysfonctionnement de l'application. Les preuves d'échec ont été conservées dans le rapport d'audit; aucune capture réelle n'a été obtenue.
