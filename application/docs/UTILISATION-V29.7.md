# OpenVisio v29.7 — qualification SPOF et dépendances SAN

Auteur : Abdelhalim Talbi.

## Changements
- Correction de trois régressions de métadonnées et de contrôles historiques de version.
- Nouveau module `src/san-spof-dependencies.js` : identification déterministe des identifiants de composants partagés entre chemins Fabric A/B documentés.
- Les identifiants communs peuvent être normaux (par exemple hôte et baie terminaux) : une revue humaine doit confirmer un véritable SPOF.

## Exécution Windows
Installer Node.js, extraire l'archive, lancer `npm test` dans le répertoire racine. Pour l'éditeur, lancer `python -m http.server 8080`, puis ouvrir `http://localhost:8080`.

## Limites
Ce module d'analyse est disponible dans les sources mais n'est pas encore relié au panneau SPOF du canvas. Aucune découverte matérielle, modification SAN ou validation réelle du multipathing.
Aucune capture Windows réelle n'a été produite dans cet environnement.
