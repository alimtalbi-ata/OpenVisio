# Audit v34.4

Constat : la recette v34.3 pouvait attendre indéfiniment un processus d’installation, accepter une désinstallation incomplète et ne conservait pas de rapport machine-readable.

Corrections : délais explicites, erreurs bloquantes, contrôle des ressources JS/CSS, vérification post-désinstallation, rapport JSON en CI.

Risque restant : sans runner Windows, ni compilation C# ni interface WebView2 ne sont validées.
