# OpenVisio — synchronisation des développements

Dépôt de référence : https://github.com/alimtalbi-ata/OpenVisio

## Workflow convenu (à partir de v41.77)

1. Partir de la branche `main` la plus récente et comparer les changements déjà intégrés aux archives cumulatives.
2. Développer sur une branche dédiée `develop/openvisio-vXX-YY`, sans remplacer ni forcer `main`.
3. Exécuter la suite Node.js, les contrôles de cohérence Windows et les vérifications documentaires avant pull request.
4. Ouvrir une pull request comprenant les modifications, les résultats réels des tests, les limitations et la liste des livrables.
5. Après revue et fusion, générer le ZIP cumulatif documenté correspondant ; ne pas inclure de binaires Windows fictifs.
6. Générer l’installateur et le portable via Windows CI lorsque disponibles ; conserver leurs empreintes SHA256 et preuves d’exécution.

## État initial vérifié

Au 18 octobre 2026, `main` pointe sur `2875ac4df30a29de1673b137a07f05ad252a6d72` (« Integrate V41.72 and retain tested fixes »). Les développements locaux v41.73 à v41.76 doivent être comparés à la branche GitHub avant intégration, sans supposer qu’ils y figurent déjà.

Auteur : Abdelhalim Talbi.
