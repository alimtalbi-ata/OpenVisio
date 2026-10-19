# OpenVisio 42.5 — migration Python natif

Auteur : Abdelhalim Talbi.

Nouvelle base native Python 3.12 + Tkinter, sans Java, JavaScript, Node.js, .NET ni WebView2 à l'exécution.
Éditeur initial : création et déplacement de nœuds, connexions, suppression, ouverture/enregistrement JSON atomique.
Lancement en développement : `cd python && python -m openvisio`.
Tests : `cd python && python -m unittest discover -s tests -v`.
Compilation Windows : `Build-Windows.cmd`. Le fichier `binary/OpenVisio-v42.5-Windows-x64-Portable.exe` sera généré uniquement après compilation sur Windows.

**État :** socle de migration, non-parité fonctionnelle avec v41.77. Le moteur SAN, l'import Visio, les bibliothèques de formes, les formats avancés et l'installateur restent à porter. Ne pas diffuser comme version complète avant qualification sur PC Windows vierge. Les sources historiques sont conservées temporairement sur cette branche pour comparaison et migration, sans être nécessaires à l'exécution du nouveau programme Python.

## Livraison Windows obligatoire

Le script `Build-Windows.cmd` prépare la compilation PyInstaller puis Inno Setup, génère les guides Word/PDF et vérifie l'archive cumulative. Les deux binaires sont regroupés dans `python/binary/`, avec un manifeste SHA256. Les documents sont intégrés dans `dist/OpenVisio-v42.5-Windows-Cumulative.zip` ; aucune documentation séparée n'est requise pour la distribution.

Le workflow `.github/workflows/python-windows.yml` exécute la construction sur Windows et publie l'archive. La réussite du workflow ne remplace pas une qualification sur un autre PC Windows. Les captures réelles ne sont pas encore disponibles ; aucune image simulée n'est présentée comme preuve.

**Important :** les sources JavaScript et .NET historiques restent présentes dans le dépôt comme référence de migration, mais la nouvelle édition Python n'en dépend pas à l'exécution. Leur suppression ne sera envisagée qu'après récupération et validation des fonctionnalités correspondantes.
