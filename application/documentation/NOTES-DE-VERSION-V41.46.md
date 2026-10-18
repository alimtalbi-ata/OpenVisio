OpenVisio v41.46 — Stabilisation de la livraison Windows
Auteur : Abdelhalim Talbi

Correctifs : version npm, projet .NET, script Inno Setup et titre de l’éditeur synchronisés en 41.46.0 ; le script de build supprime désormais le ZIP portable du même numéro avant reconstruction au lieu de bloquer immédiatement. Le script de contrôle compare les métadonnées.

Limites : les anciens tests qui exigent des numéros historiques fixes ne sont pas tous compatibles avec la progression des versions. Aucun exécutable Windows n’a été compilé sous Windows dans cet environnement Linux. Aucune capture Windows réelle n’est disponible.

Mode opératoire Windows : extraire le ZIP ; ouvrir application ; exécuter Build-Windows-Installer.cmd ; consulter dist/installer et dist/portable ; vérifier les journaux et les empreintes SHA256. Connexion réseau, outils et droits adaptés requis.

Qualification : les tests Node.js et le manifeste documentaire sont lancés sous Linux. Ne pas assimiler ces contrôles à une recette de l’installateur Windows.
