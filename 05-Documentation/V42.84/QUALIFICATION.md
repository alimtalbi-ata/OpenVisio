# OpenVisio V42.84 — XML VSDX encodé, refus des DTD

Auteur : Abdelhalim Talbi

## Anomalie et correctif
Le contrôle précédent recherchait `<!DOCTYPE` dans les octets bruts. En UTF-16, la séquence contient des octets NUL : une DTD et des entités internes étaient acceptées par ElementTree. La préanalyse Expat interdit maintenant les déclarations DOCTYPE et les entités quelle que soit la représentation XML reconnue par le parseur, avant toute construction de l'arbre.

## Qualification locale observée (23 octobre 2026)
- Avant correction : 4 tests ciblés, 2 échecs reproduits.
- Après correction : 4 tests ciblés réussis.
- Suite Python 3.13 Linux cumulative : 754 tests, 41 ignorés, aucun échec.
- Deux miroirs du moteur et deux miroirs des tests modifiés.
- Données d'essai VSDX synthétiques, pas de qualification Microsoft Visio.

## Windows
Le workflow Windows natif, le script PyInstaller et le fichier Inno Setup sont adaptés à V42.84. L'exécution Windows doit être confirmée dans GitHub Actions avant de qualifier le binaire. Numéro interne historique : 42.50.0.

## Écarts et réserves
ZIP historique V43.4 indisponible. Tests historiques locaux encore non publiés dans le dépôt distant. Aucune capture Windows V42.84 réelle à cette étape. Aucune modification de main ni fusion automatique.
