# OpenVisio V42 — Audit de fiabilité et recentrage produit
Auteur : Abdelhalim Talbi. Date : 2026-10-19.

## Portée de l'audit
Inspection statique des modules app.py, history.py, viewport.py, model.py, validation.py, render.py, properties.py et du pipeline Windows. Il ne s'agit pas d'une recette manuelle sur un PC tiers.

## Constats prioritaires
| Priorité | Constat | Risque | Action |
|---|---|---|---|
| P0 | Sélection rectangle avec Maj : la sélection existante était effacée dès le clic sur fond vide | Perte de sélection | Sauvegarder la sélection initiale avant le clic et faire l'union à la fin |
| P0 | Ouvrir un document et rétablir laissaient des IDs de sélection de l'ancien document | État incohérent / suppression inattendue | Réinitialiser selected_nodes et link_start à l'ouverture ; effacer la sélection au redo |
| P1 | Commandes majeures dispersées dans les menus | Découverte difficile | Barre d'actions persistante : fichier, historique, ajouter, relier, propriétés, chercher, ajuster |
| P1 | L'éditeur Tkinter concentre UI, commandes et état dans app.py | Régression difficile à isoler | Extraire contrôleur d'édition, état de sélection et actions transactionnelles |
| P1 | Validation des liens et schéma encore peu stricts | Incohérences métiers SAN | Contrôles protocole/fabric/ports, tests de compatibilité |
| P1 | Liaisons et noeuds affichés avec des rectangles et lignes simples | Lisibilité limitée à grande échelle | Routage orthogonal, collisions, couches, palette catégorisée |
| P2 | Étiquettes de liaison peuvent chevaucher les noeuds | Perte de lisibilité | Algorithme de placement d'étiquettes |
| P2 | Les tests d'interface sont principalement des smoke tests | Couverture fonctionnelle insuffisante | Tests de parcours utilisateur sur Windows, tests de régression GUI |

## Invariants de qualité
1. Une action d'édition produit au maximum une entrée d'historique, annulable et rétablissable.
2. Aucune liaison orpheline après suppression d'un équipement.
3. Une sélection ne contient que des identifiants du document courant.
4. Les sauvegardes sont atomiques ; aucun fichier partiellement écrit n'est considéré valide.
5. Le build produit un installateur et un EXE portable exécutables sans sources sur Windows.
6. Les rapports distinguent les tests réellement exécutés, les simulations et les validations restant à faire.

## Plan des prochaines versions
- **V42.x stabilisation** : corriger les états de sélection, les erreurs de focus clavier et les commandes de sauvegarde ; ajouter tests d'intégrité et tests GUI.
- **V43 cœur d'édition** : séparer commandes, état, document et vue ; définir API transactionnelle d'édition ; uniformiser undo/redo.
- **V44 expérience utilisateur** : panneau latéral de propriétés, bibliothèque de formes catégorisée, barre d'outils compacte et accessible, recherche non modale.
- **V45 diagrammes d'infrastructure** : connecteurs orthogonaux, ports typés, validation SAN/NAS et rapports d'audit.
- **V46 compatibilité** : import/export documenté avec tests sur corpus, sans promettre une compatibilité Visio non démontrée.

## Critères de sortie
CI verte, tests fonctionnels documentés, ZIP cumulatif avec binaires et docs à jour, manifeste SHA256, aucune capture simulée présentée comme réelle, et qualification sur Windows indépendant avant certification de déploiement.
