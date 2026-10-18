# OpenVisio v36.6 — Audit distribution portable

Auteur : Abdelhalim Talbi.

## Correction
Le shell Windows attendait `wwwroot` à côté de l’exécutable, rendant impossible une distribution portable mono-EXE. La publication portable intègre maintenant une archive de ressources web dans l’assembly .NET, puis les extrait dans `%LOCALAPPDATA%/OpenVisio/assets/36.6` au premier lancement. Le shell pointe vers ce cache. Le paquet installable continue d’utiliser `wwwroot` externe.

## Limites et risques
- **Pas de compilation Windows réalisée ici** : le build PowerShell et .NET doit être exécuté sur Windows.
- WebView2 Runtime reste requis, et n’est pas incorporé dans l’EXE portable.
- Un mono-EXE publié par .NET peut extraire des bibliothèques natives dans son cache au lancement ; il ne signifie pas une exécution sans fichiers temporaires.
- L’extraction n’est pas transactionnelle face aux lancements concurrents ; la prochaine itération devra utiliser un verrou et des contrôles d’intégrité des assets.
- La taille du binaire final est à mesurer sur Windows.
