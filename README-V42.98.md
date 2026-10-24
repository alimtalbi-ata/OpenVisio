# OpenVisio V42.98 — Export SVG transactionnel

Auteur : Abdelhalim Talbi. Branche de développement indépendante issue de V42.97.

## Correction métier
L'export SVG ne doit pas tronquer un fichier existant en cas d'échec de rendu ou d'écriture. La nouvelle fonction export_svg écrit d'abord dans un fichier temporaire du même répertoire, synchronise les octets puis publie par remplacement atomique. Les options require_absent et expected_sha256 empêchent un écrasement non voulu. Le résultat est le SHA-256 des octets publiés.

## Limites
La sérialisation est garantie entre instances OpenVisio coopérantes seulement. Un processus externe ignorant le verrou peut écrire pendant l'export. Le retour de os.replace/os.link ne garantit pas la durabilité du répertoire après coupure brutale. Les tests synthétiques SVG ne prouvent pas la fidélité Microsoft Visio. Le code d'application interne reste en version 42.50.0 et la compilation est un candidat Windows, non une release certifiée.

## Vérification
PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_svg_atomic_export_v4298.py' -v
PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q
python verify_source_parity.py

## Références
Base GitHub : develop/v42.97-svg-dimension-integrity-20261024, commit d26b4f2c7b74c0a7b09db78a31e9283fe4719585.
Fichiers modifiés : python/openvisio/export.py, 03-Sources/openvisio/export.py, tests miroir, scripts Windows et CI.
