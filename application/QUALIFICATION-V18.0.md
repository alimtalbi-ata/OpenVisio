# OpenVisio v18.0 — Préqualification interface Windows

Auteur : Abdelhalim Talbi.

## Réalisé
- Correction de l'étiquette de version obsolète dans le HTML visible.
- Tests automatisés des éléments essentiels : canevas SVG, calques, actions JSON/SVG, inspecteur, bibliothèque, diagnostic et scripts Windows.
- Conservation du code et de la documentation des versions précédentes.

## Recette manuelle Windows à exécuter
1. Extraire l'archive dans un dossier local ; lancer `OpenVisio-Windows.bat` et vérifier l'affichage `v18.0`.
2. Insérer serveur, stockage et switch SAN ; vérifier la sélection, le déplacement, le redimensionnement et l'inspecteur.
3. Relier les formes, déplacer un obstacle et vérifier visuellement le routage et la lisibilité des liens.
4. Tester Annuler, Enregistrer JSON, Ouvrir JSON et Exporter SVG.
5. Ouvrir `Diagnostic rendu`, déplacer plusieurs formes, relever moyenne/P95/max.
6. Tester 100, 500 et 1 000 équipements, consigner FPS, latences et défauts de rendu.
7. Construire l'EXE sur Windows avec `Build-Windows-EXE.cmd` puis valider l'exécutable.
8. Prendre des captures réelles datées des vues accueil, édition, connexions, inspecteur et diagnostic.

## Limites
- Tentative Chromium headless Linux interrompue sans PNG ; aucune capture v18.0 authentifiée.
- Aucun essai Windows natif ni compilation EXE réalisé dans cet environnement.
- Tests HTML statiques et Node.js ne remplacent pas une recette navigateur et Windows.
- Captures des anciennes versions conservées à titre historique seulement.
