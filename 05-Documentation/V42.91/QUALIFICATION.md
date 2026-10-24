# OpenVisio V42.91 — qualification du modèle SAN multipath

Auteur : Abdelhalim Talbi — 24 octobre 2026.
Branche GitHub : develop/v42.91-san-multipath-template-20261024.
PR en brouillon : https://github.com/alimtalbi-ata/OpenVisio/pull/24.
Commit GitHub de la qualification Windows : 646d44404dd7d1e5d6372d45a7e62c299a4e38cf.

## Amélioration métier

Un nouveau modèle « SAN multipath FC (2 fabrics) » est disponible dans le menu Modèles. Il produit 5 équipements, 2 calques Fabric A/B et 12 liens FC distincts. Chaque liaison est qualifiée par un couple de ports physiques illustratifs, une fabric, une étiquette et un calque. Les 6 corridors sont chacun constitués de 2 liens parallèles. Les identifiants d'équipement et de liaison sont renouvelés à chaque création.

## Qualification locale Linux (réellement exécutée)

6/6 tests ciblés PASS. Suite cumulative : 788 tests exécutés, 41 ignorés, 0 échec. Vérification bidirectionnelle des miroirs : 57/57 modules moteur, 166/166 fichiers de tests. Le vrai éditeur Tk a chargé le modèle sous Linux/Xvfb ; une capture d'écran réelle est jointe et explicitement étiquetée Linux/Xvfb.

## Séparation des preuves

Unitaires : validation, identités de ports et fabrics, lanes parallèles, isolation de modèles, undo/redo.
Intégration : sauvegarde/rechargement natif OVJSON et export/import VSDX embarqué, tous synthétiques.
Microsoft Visio Desktop : aucun round-trip réel, aucune qualification de fidélité indépendante.
Windows natif : CI GitHub Actions run 40059258102 SUCCESS sur HEAD 646d44404dd7d1e5d6372d45a7e62c299a4e38cf ; 492 tests, 16 ignorés, PyInstaller x64 et Inno Setup, smoke portable/installé PASS. Artefact 12545809512, SHA-256 des deux exécutables vérifiés.
UI : capture réelle Linux/Xvfb, aucune capture Windows V42.91.

## Limites et actions restantes

Le ZIP V43.4 historique n'est pas disponible. Les 49 fichiers de tests historiques absents du checkout GitHub V42.90 ne sont pas rétablis par cette version. Version interne 42.50.0 inchangée ; V42.91 est un candidat de code et non une release Windows officiellement versionnée. Les formes Tk sont encore simplifiées, et certaines légendes des liens croisés peuvent flotter loin de leur chemin. Les ports sont fictifs ; le modèle n'est pas une source de zoning SAN réelle.

Aucun secret ni modification de production. Aucun merge vers main.
