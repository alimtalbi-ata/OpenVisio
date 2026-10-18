# Audit v37.1

- Suppression du détour export/import pour le diagnostic de redondance SAN : réutilisation du contrat d’événements `openvisio:san-snapshot-request` déjà implémenté dans `src/main.js`.
- Le panneau n’analyse les événements snapshot qu’après demande explicite, évitant les interactions parasites avec d’autres modules.
- Le moteur reste déclaratif et en lecture seule.
- Dette restante : grand dialogue HTML monolithique, qualification graphique et compilation Windows non exécutées.
