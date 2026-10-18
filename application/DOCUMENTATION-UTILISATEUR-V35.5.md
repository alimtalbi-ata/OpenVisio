# OpenVisio v35.5 — Qualification Windows

Auteur : Abdelhalim Talbi.

1. Sur Windows x64, extraire le ZIP dans un dossier local accessible en écriture.
2. Lancer `Build-OpenVisio-Windows.cmd` pour préparer les dépendances et compiler l’application et l’installateur.
3. Ouvrir un terminal administrateur, puis lancer `Qualify-OpenVisio-Windows.cmd`.
4. Lire `dist/qualification/qualification-summary.json` et `installer-e2e-result.json`.
5. Le code de sortie 0 signifie PASS, 1 FAIL et 2 PARTIAL. Ne pas distribuer un build non PASS.

Le présent environnement Linux ne permet pas de valider la compilation .NET Windows, le démarrage de WebView2 ou l’installation réelle.
