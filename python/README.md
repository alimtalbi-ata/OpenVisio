# OpenVisio 42.0 — migration Python natif

Auteur : Abdelhalim Talbi.

Nouvelle base native Python 3.12 + Tkinter, sans Java, JavaScript, Node.js, .NET ni WebView2 à l'exécution.
Éditeur initial : création et déplacement de nœuds, connexions, suppression, ouverture/enregistrement JSON atomique.
Lancement en développement : `cd python && python -m openvisio`.
Tests : `cd python && python -m unittest discover -s tests -v`.
Compilation Windows : `Build-Windows.cmd`. Le fichier `binary/OpenVisio-v42.0-Windows-x64-Portable.exe` sera généré uniquement après compilation sur Windows.

**État :** socle de migration, non-parité fonctionnelle avec v41.77. Le moteur SAN, l'import Visio, les bibliothèques de formes, les formats avancés et l'installateur restent à porter. Ne pas diffuser comme version complète avant qualification sur PC Windows vierge. Les sources historiques sont conservées temporairement sur cette branche pour comparaison et migration, sans être nécessaires à l'exécution du nouveau programme Python.
