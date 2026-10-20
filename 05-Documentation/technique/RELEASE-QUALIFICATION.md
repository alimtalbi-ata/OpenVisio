# Qualification Windows v42.0

Auteur : Abdelhalim Talbi.

## Livrables obligatoires

- `binary/OpenVisio-v42.0-Windows-x64-Portable.exe` : mono-EXE PyInstaller avec interpréteur et interface embarqués.
- `binary/OpenVisio-Setup-v42.0-x64.exe` : installateur Inno Setup.
- `dist/OpenVisio-v42.0-Windows-Cumulative.zip` : archive contenant binaires, sources, tests, guides Word/PDF et manifestes SHA256.

## Vérification indépendante

Copier uniquement le portable sur un Windows 10/11 x64 sans Python ni sources, ouvrir l'application, créer deux équipements, les relier, sauvegarder un fichier .ovjson, fermer, relancer et rouvrir le document. Tester ensuite l'installateur sur une autre machine ou VM propre, le raccourci Bureau, la désinstallation et les associations .ovjson.

## Preuves

Les tests unitaires et la construction GitHub Actions ne prouvent pas à eux seuls la compatibilité sur un autre PC. Les captures doivent provenir d'une exécution réelle et être horodatées. Ne pas utiliser de maquettes comme preuves. Statut actuel : **qualification sur machine propre non exécutée**.
