# OpenVisio V43.03 — Identité SAN des stencils VSDX à double nom

Auteur : Abdelhalim Talbi. Branche de développement uniquement ; aucune fusion automatique.

## Correction métier

Les formes Visio peuvent exposer `NameU=Sheet.42` et `Name=Brocade G720` ou `Name=Cisco MDS 9710`. L'importeur V43.02 privilégiait `NameU` et classait alors ces commutateurs FC comme serveurs. V43.03 examine les deux noms sans déduire l'identité matérielle du texte de légende. Le texte explicite conserve la priorité pour l'étiquette affichée ; à défaut, un `NameU` générique laisse place au nom visible.

## Vérifications réalisées dans l'environnement Linux

- Défaillance reproduite avant correction : deux tests échouent sur quatre.
- Suite Python V43.03 après correction : 564 tests, 22 ignorés, zéro échec.
- Parité miroir : 58 modules moteur et 132 fichiers de tests, contrôlés.
- Quatre nouveaux tests couvrent `Name`, `NameU`, priorité de la légende et absence de faux positif.

## Reproductibilité et limites

Le script `02-Compilation/Verify-GitHub-Checkout-V43.03.ps1` vérifie un clone GitHub indépendant, les empreintes Git des modules critiques et la suite de tests. Le workflow Windows construit un portable PyInstaller et un installateur Inno Setup et exécute des tests automatisés ; seuls les artefacts d'une exécution CI réussie peuvent être annoncés comme binaires V43.03.

Les VSDX utilisés par les nouveaux tests sont synthétiques. Aucune qualification de fidélité dans Microsoft Visio Desktop ni essai manuel interactif Windows n'est revendiqué. Le ZIP historique V43.4 n'a pas été fourni : la réconciliation exhaustive reste impossible. `main` ne doit pas être modifiée sans revue.
