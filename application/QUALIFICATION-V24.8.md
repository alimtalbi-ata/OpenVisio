# OpenVisio v24.8 — Qualification

Auteur : Abdelhalim Talbi.

Nouveautés : scénario de sélection native, annulation/rétablissement de connexion SAN ; comparaison pixel des captures Chromium avec baseline réelle et seuil configurable.

Commandes : `npm test`, `python -m py_compile tests/browser-san-performance.py`, `powershell -ExecutionPolicy Bypass -File windows/Run-Graphic-Qualification.ps1 -VisualBaseline C:\\baseline.png`.

**Limite** : tests Chromium/Windows non exécutés ici ; les captures historiques ne sont pas des captures v24.8. Une comparaison de pixels n'est pas une preuve sémantique du bon routage.
