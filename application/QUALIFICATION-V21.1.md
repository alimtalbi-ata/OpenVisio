# Qualification OpenVisio v21.1

Auteur : Abdelhalim Talbi

- Nouvelle recette automatisée `tests/browser-recovery.py` utilisant Chromium via Playwright Python et un serveur local temporaire.
- Parcours : création de forme, export JSON SHA-256, nouveau diagramme, import avec confirmation, rechargement, corruption de clé principale, récupération depuis sauvegarde.
- **Limite de cet environnement :** Chromium s'ouvre, mais les navigations HTTP localhost et file:// sont bloquées par une politique administrateur (`net::ERR_BLOCKED_BY_ADMINISTRATOR`). Le scénario navigateur n'a donc **pas** été validé de bout en bout ici ; aucune nouvelle capture réelle n'est fournie.
- Qualification Windows native et EXE non réalisés.
- Captures antérieures du répertoire `snapshots/` conservées comme historiques, non comme recette v21.1.
