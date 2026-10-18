# OpenVisio v41.44 — Audit initial et correctifs de livraison Windows
Auteur : Abdelhalim Talbi

## Constats vérifiés
- `package.json`, `windows/native/OpenVisio.csproj`, l'installateur Inno Setup et les scripts de build portaient encore v41.0 malgré l'archive v41.43.
- `Build-Windows-Installer.cmd` relançait une seconde chaîne d'assemblage après le build complet, avec recherche d'ISCC dans le PATH uniquement.
- La page principale affichait encore v41.0.
- La chaîne Windows utilise .NET 8, WinForms/WebView2, Inno Setup et un exécutable portable autonome .NET; WebView2 demeure un prérequis système.

## Correctifs réalisés
- Synchronisation des versions v41.44.0 dans les métadonnées, le projet .NET et Inno Setup.
- Synchronisation des noms d'installateur et de la version visible dans l'interface.
- Script de contrôle `windows/Check-Release-Version.ps1` exécuté avant la compilation.
- Script `Build-Windows-Installer.cmd` réduit à un appel unique au build Windows complet.
- Deux tests automatisés nouveaux, tous deux PASS.

## Qualification et limitations
Suite complète Node : 1796 tests, 1779 PASS, 17 FAIL. Plusieurs échecs sont des tests historiques qui figent les anciennes versions; ces échecs ne doivent pas être masqués. Un test documentaire échoue également. Le correctif ne peut donc pas être déclaré qualifié. Aucun binaire Windows ni installateur n'a été compilé dans cet environnement Linux. Aucune capture réelle Windows n'est fournie.

## Plan de remédiation
1. Centraliser la version et remplacer les assertions historiques figées par des invariants de cohérence, sans supprimer les tests métier.
2. Réparer et revalider le contrôle documentaire.
3. Qualifier sur Windows le build, l'installation silencieuse, la désinstallation, le lancement portable et les prérequis WebView2.
4. Réaliser un audit ergonomique navigateur avec captures réelles et parcours utilisateur.
