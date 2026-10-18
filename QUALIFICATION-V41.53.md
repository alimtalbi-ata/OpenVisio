# OpenVisio v41.53 — Chaîne de qualification Windows

Auteur : Abdelhalim Talbi.

Nouveau point d’entrée : `application/Qualify-Release-Windows.cmd`. Il compile via le script Windows existant, vérifie la cohérence de version, contrôle l’artefact portable, teste le démarrage natif et portable et lance le test de l’installateur. Un rapport JSON est produit dans `dist/qualification/pipeline-v41.53.json`, même en cas d’échec.

Options : `-SkipBuild`, `-SkipInstallerE2E`, `-SkipStartup`, `-RunGraphicSmoke`. Les contrôles ignorés donnent un statut `PARTIAL` et un code retour 2 ; un échec donne `FAIL` et un code retour 1.

**Limite** : tests Node.js exécutables sous Linux ; aucune compilation ou exécution de binaires Windows ne peut être attestée dans cet environnement. La recette Windows nécessite une machine Windows avec PowerShell, Node, .NET 8 et Inno Setup.

## Tests exécutés
Suite Node.js complète : 1809 / 1809 PASS, 0 FAIL.
Contrôle des exécutables Windows : NON EXÉCUTÉ ; aucun binaire Windows qualifié.
