# OpenVisio V42.1 — Consolidation et feuille de route
Auteur : Abdelhalim Talbi — 19 octobre 2026.

## Périmètre livré
- Éditeur Python/Tkinter Windows x64 ; création, déplacement, sélection multiple, propriétés, connexions, suppression, copier/coller, historique, modèles, recherche, export SVG et JSON atomique.
- Protection des raccourcis dans les champs de saisie et les dialogues ; menu contextuel selon l'objet.
- Validation des identifiants, coordonnées et références de liaisons ; refus des auto-connexions ; migration déterministe des anciens liens sans identifiant.
- Sauvegarde atomique, restauration après échec de remplacement, tests de round-trip et de parcours métier.
- V42.1 : les notes multilignes conservent la touche Entrée ; Ctrl+Entrée valide le dialogue des propriétés.

## Audit fonctionnel et limites
| Composant | Utilité | Contrôle automatisé | Limite |
|---|---|---|---|
| Modèle/validation | Éviter les topologies corrompues | Tests unitaires et anciens formats | Formats Visio VSDX non pris en charge par ce moteur |
| Historique | Annuler/rétablir les modifications | Tests de séquences | Pas de journal d'audit persistant |
| Édition/liaisons | Construire des topologies | Tests de commandes et round-trip | Gestes graphiques non testés automatiquement |
| Sauvegarde | Éviter la perte de fichiers | Tests d'échec et relecture | Pas de récupération automatique des documents non enregistrés |
| Interface | Simplifier les actions fréquentes | Tests de politique de focus | Recette ergonomique humaine sur Windows à réaliser |
| Windows EXE/Setup | Déploiement sans sources Python | CI, smoke tests portable/installation | PC tiers vierge non certifié |

## Critères de sortie
La CI Windows doit réussir les tests, la compilation PyInstaller, Inno Setup, les smoke tests hors dépôt et la vérification du ZIP. Les captures d'écran réelles ne sont pas disponibles dans cette livraison : aucune maquette n'est présentée comme capture de recette.

## Prévision des versions suivantes
- **V42.2** : séparation contrôleurs UI / services document, tests des raccourcis et fenêtres, barre d'état enrichie.
- **V42.3** : récupération après interruption, journal de session local, stratégie de sauvegarde et restauration.
- **V42.4** : bibliothèques de formes et gabarits infrastructure, gestion des connecteurs et points d'ancrage.
- **V42.5** : import/export de formats interopérables, validation de fidélité des attributs et rapports de conversion.
- **V42.6** : optimisation grands diagrammes, index spatial, tests de performance et limites documentées.
- **V42.7** : accessibilité clavier, navigation, zoom et sélection, recette ergonomique documentée.
- **V42.8** : stabilisation Windows, sécurité packaging, signature optionnelle, qualification PC vierge.

Ces contenus sont prévisionnels, non des fonctionnalités livrées.
