# OpenVisio v41.23 — Qualification navigateur
Auteur : Abdelhalim Talbi

## Périmètre
Base : archive cumulative v41.22. Aucune modification du moteur de rendu n'est revendiquée dans cette livraison de qualification.

## Preuves exécutées
- `cd application && node --test tests/*.test.mjs` : 1759/1759 PASS (voir TEST-RESULT-V41.23.txt).
- `python3 tests/browser-san-performance.py --chromium /usr/bin/chromium --port 18765 --screenshot ../CAPTURE-CHROMIUM-V41.23.png --report ../BROWSER-QUALIFICATION-V41.23.json` : FAIL, `net::ERR_BLOCKED_BY_ADMINISTRATOR` sur localhost.
- Aucune capture Chromium valide créée. Aucune qualification Windows effectuée.

## Interprétation
Le blocage intervient avant le chargement de la page. Il ne démontre ni une régression du rendu ni son bon fonctionnement. Le benchmark de rendu réel, les obstacles, les ports multiples et Undo/Redo natif restent non qualifiés.

## Reprise de recette
Sur un poste autorisant Chromium et les connexions HTTP loopback : exécuter `python3 application/tests/browser-san-performance.py --chromium <chemin-chromium> --report BROWSER-QUALIFICATION-V41.23.json --screenshot CAPTURE-CHROMIUM-V41.23.png` depuis la racine de la distribution. Conserver les résultats et captures uniquement si le script réussit.

## Jalons suivants
1. Refaire la recette Chromium et recueillir des captures réelles.
2. Comparer le rendu SVG sur topologies SAN et obstacles.
3. Mesurer les temps de rendu avec répétitions et conditions contrôlées.
4. Qualifier l'application et le packaging Windows.
5. Réviser les sept guides Word/PDF historiques : non réactualisés ici.
