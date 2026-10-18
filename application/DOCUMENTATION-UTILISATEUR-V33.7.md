# OpenVisio v33.7 — guide utilisateur
Auteur : Abdelhalim Talbi

## Interface
Dans l'inspecteur, **Tout afficher** développe les propriétés, sélectionne le niveau complet et efface la recherche. Le mode Essentiel et le repli restent disponibles.

## Construction Windows
Double-cliquer `Build-OpenVisio-Windows.cmd` sur Windows avec accès Internet. Le script prépare .NET 8 localement, cherche Inno Setup (y compris dans PATH), télécharge le runtime WebView2, publie WinForms et compile l'installateur dans `dist/installer`. Le SDK est un prérequis de construction, non de l'utilisateur final. L'installateur doit être qualifié sur Windows avant diffusion.

## Sécurité
Ne distribuer que les exécutables construits depuis une source vérifiée. Vérifier SHA-256 et tester l'installation, la désinstallation et l'ouverture d'un document.
