# OpenVisio v38.2 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Contrôle de persistance SAN
Les domaines site, chassis, powerDomain, controller et failureDomain peuvent être associés aux équipements et connexions. La v38.2 ajoute deux API de validation de sauvegarde/réouverture JSON (`serializeSanDiagram`, `deserializeSanDiagram`) dans `src/zoning-document.js`. Ces API sont vérifiées par tests automatisés, mais ne sont pas encore raccordées à toutes les actions de sauvegarde de l’interface.

## Construction Windows
Exécuter `Build-OpenVisio-Windows.cmd` sur un hôte Windows x64. Le ZIP est un paquet de sources, pas un exécutable précompilé.
