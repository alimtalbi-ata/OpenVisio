# Qualification OpenVisio v21.4

Auteur : Abdelhalim Talbi

Recette Chromium tentée : **NON VALIDÉE** — `net::ERR_BLOCKED_BY_ADMINISTRATOR` lors de la navigation localhost. Aucune capture réelle nouvelle.

Tests Node.js : voir résultats de qualification.

Tests navigateur renforcés : sauvegarde SHA-256 v2, import altéré, diagnostic, récupération.

Tests Node.js : **901/901 PASS**. `node --check src/main.js` : PASS. `python -m py_compile tests/browser-recovery.py` : PASS.
