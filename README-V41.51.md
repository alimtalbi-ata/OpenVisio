# OpenVisio v41.51 — qualification des artefacts Windows

Auteur : Abdelhalim Talbi.

## Changements
- Vérification autonome du portable Windows : présence, taille minimale, en-tête MZ, cohérence du manifeste et SHA256.
- Le qualificateur Windows appelle cette vérification par défaut et autorise `-SkipPortableSmoke` pour les qualifications partielles.
- Trois tests Node.js vérifient l'intégration, la vérification d'intégrité et la sémantique PARTIAL.

## Commandes (à exécuter sur Windows)
```powershell
.\Build-OpenVisio-Windows.cmd
powershell -NoProfile -ExecutionPolicy Bypass -File .\windows\Qualify-Windows-Release.ps1 -RunGraphicSmoke -RunFunctionalSmoke
```
La qualification complète de l'installateur exige une session élevée. Les tests d'interface demandent les prérequis du navigateur. Les commandes ci-dessus sont des instructions, pas des preuves d'exécution.

## Limites
Aucun binaire Windows compilé dans l'environnement Linux de préparation. Aucune capture Windows réelle. Le test portable est un contrôle statique d'artefact, pas un test de lancement portable.
