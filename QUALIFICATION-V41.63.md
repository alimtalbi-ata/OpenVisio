# OpenVisio v41.63 — Qualification de restauration

Auteur : Abdelhalim Talbi

La restauration vérifie désormais les noms distincts, les en-têtes MZ et les empreintes SHA256, puis revalide le dossier restauré. En cas d’échec, le point de restauration est remis en place si possible.

Ces tests statiques Node.js ne constituent pas une exécution de PowerShell sur Windows. Les binaires précompilés ne sont pas disponibles.
