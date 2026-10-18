# Audit UX OpenVisio v38.6
Auteur : Abdelhalim Talbi

## Défaut corrigé
En v38.5, le mode « Essentiel » masquait les champs avancés même lorsqu’une recherche ciblait explicitement ces champs. Le filtrage a été corrigé pour rendre la recherche prioritaire.

## Améliorations
Raccourci SAN et remise à zéro explicite, sans supprimer les propriétés avancées. Aucun mécanisme de sauvegarde supplémentaire.

## Risques restant ouverts
Le HTML principal reste volumineux et contient de grands panneaux spécialisés. Les tests Node.js ne valident pas le rendu WebView2 ni la compilation Windows. Le raccourci SAN dépend des identifiants/labels des champs de l’inspecteur et doit être testé visuellement.
