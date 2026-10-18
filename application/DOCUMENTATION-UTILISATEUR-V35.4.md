# OpenVisio v35.4 — Guide Windows

Auteur : Abdelhalim Talbi.

1. Extraire le ZIP dans un chemin local Windows.
2. Lancer `Build-OpenVisio-Windows.cmd` pour préparer les dépendances et générer l’exécutable et l’installateur.
3. Ouvrir un terminal **PowerShell administrateur** et exécuter `Qualify-OpenVisio-Windows.cmd` pour tester le préflight, le serveur natif, l’installation, le démarrage et la désinstallation.
4. Lire `dist/qualification/qualification-summary.json` et `dist/qualification/installer-e2e-result.json`. Un statut `PASS` nécessite tous les contrôles ; `PARTIAL` signale des étapes ignorées.

**Attention :** l’exécution de la qualification installe puis désinstalle une instance OpenVisio de test. Ne pas lancer sur un poste de production sans préparation. Les tests natifs Windows et les captures réelles ne sont pas exécutables dans l’environnement Linux de construction de cette archive.
