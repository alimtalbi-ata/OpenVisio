# OpenVisio v37.8 — Guide utilisateur
Auteur : Abdelhalim Talbi

## Domaines de défaillance
1. Ouvrir un diagramme et sélectionner un équipement.
2. Dans l'inspecteur, remplir **Résilience SAN — domaines de défaillance** : site, châssis, domaine électrique/PDU, contrôleur, domaine personnalisé.
3. Employer un même identifiant pour les équipements dépendant d'une ressource commune. Les modifications sont intégrées au document et sont annulables via l'historique de l'éditeur.
4. Ouvrir le diagnostic SAN et choisir **Analyser le diagramme ouvert**.
5. Dans les résultats, développer **Domaines critiques** pour consulter le type et l'identifiant de la dépendance, puis cliquer sur **Localiser** pour surligner les éléments concernés.

Les domaines sont purement documentaires : absence de détection automatique et aucune preuve d'indépendance physique. Les liens possèdent déjà des attributs de domaine dans le modèle SAN, mais cette version ajoute l'édition graphique uniquement aux équipements.

## Windows
Lancer `Build-OpenVisio-Windows.cmd` depuis un poste Windows x64 équipé des prérequis du script. L'archive source ne contient aucun EXE précompilé.
