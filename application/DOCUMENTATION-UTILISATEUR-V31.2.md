# OpenVisio v31.2 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Import SAN hors ligne
1. Ouvrir OpenVisio sous Windows via le lanceur livré.
2. Dans le canvas principal, développer **Import configurations SAN · v31.2**.
3. Choisir la détection automatique ou le constructeur, puis sélectionner un fichier texte ou le déposer dans la zone prévue.
4. Consulter la prévisualisation (zones, alias, chemins ESXi, lignes sources), les avertissements et exporter le CSV.
5. Utiliser les contrôles de résilience SAN existants séparément ; **aucune modification du diagramme ni comparaison automatique avec les objets du canvas n'est encore effectuée**.

Taille maximale 5 Mo. Le moteur v31.1 traite des extraits ciblés et ne prouve ni zoning actif ni masking/multipathing réel. Les exports partiels sont non concluants.

## Qualification
Tests Node.js automatisés ; recette Windows réelle non exécutée dans cet environnement.
