# Audit technique v33.1 — Abdelhalim Talbi

## Constats vérifiés
- `index.html` contient une quantité importante de panneaux et de dialogues de simulation, dont certains ont des tableaux profondément imbriqués. Un découpage progressif est préférable à une réécriture brutale susceptible de casser les modules SAN.
- La v33.0 avait une erreur structurelle dans `OpenVisio.iss` : les lignes `Filename` de WebView2 et de lancement de l’application se trouvaient sous `[Registry]` et non sous `[Run]`. Corrigé dans cette version.
- Le script de construction ne vérifiait pas la présence effective de l’EXE d’installation après Inno Setup. Corrigé.
- L’interface principale ne disposait pas de lanceur de commandes transversal. Ajout d’un lanceur accessible au clavier (Ctrl+K), filtrage local, Esc, retour de focus, sans suppression de fonctions historiques.

## Risques résiduels
- Aucun SDK Windows ni compilateur Inno Setup disponible dans l’environnement de qualification ; compilation native non vérifiée.
- Le runtime WebView2 et les téléchargements SDK/winget requièrent une connexion réseau à la construction.
- Les actions du lanceur qui n’existent pas dans la page sont signalées indisponibles ; la couverture de toutes les commandes sera élargie après audit des événements.
- La validation HTML et la recette d’accessibilité au clavier restent à réaliser dans Windows.
