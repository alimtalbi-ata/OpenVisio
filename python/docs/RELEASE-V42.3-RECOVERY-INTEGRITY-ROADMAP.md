# OpenVisio V42.3 — Recovery, Integrity & Architecture

**Auteur : Abdelhalim Talbi.** Date : 2026-10-19.

## Livrables et objectifs
Version cumulative Windows 64 bits : éditeur natif Tkinter, exécutable portable PyInstaller, installateur Inno Setup, sources, tests, documentation Word/PDF générée, manifeste SHA-256. La validation sur un PC Windows tiers reste à effectuer ; les captures réelles ne sont pas simulées.

## Modifications implémentées
1. **Sauvegarde précédente** : chaque écrasement réussi d'un fichier existant crée `nom.ovjson.bak` à partir des octets de la version sur disque. L'écriture de la sauvegarde utilise un fichier temporaire, `fsync` et remplacement atomique. Si elle échoue, l'enregistrement est interrompu et le document original reste inchangé. Première sauvegarde : aucun `.bak`.
2. **Récupération assistée** : menu Fichier > Restaurer la sauvegarde précédente. Validation JSON avant proposition de restauration ; confirmation explicite ; pas de remplacement automatique du fichier principal. L'utilisateur enregistre ensuite le document récupéré.
3. **Intégrité du graphe** : importation et validation refusent deux liaisons orientées identiques, même avec des identifiants différents. Les sens opposés restent autorisés.
4. **Interactions** : suppression, annulation/rétablissement, création de liaison et touche Échap nettoient leurs états temporaires. Messages de résultat et barre d'état séparés.
5. **Tests** : sauvegarde et restauration, échec de validation sans écrasement, doublons de liens, opérations de sélection et historique sans fenêtre graphique.

## Risques et limites
- La sauvegarde `.bak` est une version précédente unique et non un historique multi-versions. Une deuxième sauvegarde écrase la précédente.
- En cas d'erreur de disque, de permission ou de sauvegarde, le message d'erreur doit être pris en compte ; aucune réussite n'est présumée.
- Un diagramme très volumineux reste limité par le rendu Tkinter et l'historique de snapshots mémoire.
- Les tests CI Windows et les tests de démarrage ne prouvent pas l'ergonomie sur tous les postes Windows.
- La restauration ne fusionne pas les versions et ne récupère pas des modifications jamais enregistrées.

## Plan d'architecture
- **V42.4 — Services de document** : extraire ouverture, sauvegarde, récupération, session et erreurs de `app.py` ; injection des dialogues pour tests unitaires.
- **V42.5 — Bibliothèque de formes** : équipement infrastructure, ports, ancres et modèles SAN/NAS/virtualisation ; versionnement des modèles.
- **V42.6 — Interopérabilité** : import/export avec validation et rapports de fidélité ; aucune promesse de compatibilité VSDX native avant tests.
- **V42.7 — Performance** : index spatial, rendu incrémental, métriques de latence et diagrammes volumineux.
- **V42.8 — Accessibilité** : navigation clavier, raccourcis contextualisés, contrastes et tests humains documentés.
- **V42.9 — Qualification Windows** : matrices OS, installation propre, signatures et vérification des dépendances.

## Critères de qualification
- `python -m unittest discover -s tests -v` depuis `python/`.
- Compilation du portable et de l'installateur Windows.
- Contrôle des artefacts et du manifeste, démarrage portable hors dépôt, installation/désinstallation silencieuses.
- Aucune capture d'écran ne sera présentée comme réelle si elle n'a pas été obtenue par un test graphique effectif.
