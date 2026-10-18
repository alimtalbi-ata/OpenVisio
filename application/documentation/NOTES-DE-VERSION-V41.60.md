OpenVisio v41.60 - Qualification des livrables Windows

Auteur : Abdelhalim Talbi

Le pipeline produit un rapport JSON dont le nom suit la version courante du projet.

Le pipeline valide le manifeste binaire et recalcule les SHA256 des deux exécutables avant les tests de démarrage.

Le script Windows reste à exécuter sur une machine Windows; aucun exécutable natif compilé n’est livré dans cette archive.

Commande Windows : Qualify-Release-Windows.cmd (sur un hôte Windows équipé des prérequis).

La validation Node.js est une qualification statique et fonctionnelle, pas une preuve de lancement Windows.
