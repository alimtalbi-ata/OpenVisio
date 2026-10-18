# Audit OpenVisio v34.5

Auteur : Abdelhalim Talbi.

- L’interface HTML conserve une forte densité de commandes, notamment le dialogue de comparaison SAN. Le travail doit progressivement extraire ces modules sans rompre leurs identifiants DOM.
- Ajout d'une aide des raccourcis accessible par F1 et bouton dédié, sans mutation du document.
- La construction .NET/WinForms et le runtime WebView2 ne peuvent pas être validés par les tests Node.
- L’installateur WebView2 dépend de la disponibilité du téléchargement Microsoft et de droits administrateur.
- Priorité suivante : vraie compilation Windows, recette graphique et extraction du dialogue SAN monolithique.
