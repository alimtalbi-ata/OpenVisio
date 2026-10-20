# OpenVisio V42.5 — Service documentaire unifié

Auteur : Abdelhalim Talbi.

## Objectif
Séparer les opérations de persistance de la fenêtre Tkinter afin de limiter les effets de bord et faciliter la qualification sans interface graphique.

## Réalisation
Le module `openvisio.document_service` expose `open_document(path)`, `save_document(path, document)` et `restore_previous(path)`. Il délègue la validation, l'écriture atomique et les sauvegardes précédentes aux modules de modèle et de récupération existants. L'éditeur utilise désormais cette frontière de service pour ouvrir, enregistrer et restaurer.

## Qualification
Tests automatisés : lecture/écriture aller-retour, lecture de version précédente, conservation du fichier d'origine lors d'une sauvegarde invalide, transactions annulables, intégrité du graphe. La CI Windows compile l'exécutable portable et l'installateur, génère Word/PDF et ZIP cumulatif et réalise des tests de démarrage et d'installation silencieuse.

## Livrable unique
`OpenVisio-v42.5-Windows-Cumulative.zip` contient `01-Application`, `02-Compilation`, `03-Sources`, `04-Tests`, `05-Documentation`, `06-Historique` et `07-Manifestes`. Les captures graphiques réelles restent à produire sur un poste qualifié ; aucune simulation n'est présentée comme capture.

## Limites et suite
Le service ne gère pas encore un journal de reprise des modifications non enregistrées. V42.6 : modèles et bibliothèques d'équipements ; V42.7 : contrôle de fidélité import/export ; V42.8 : performance sur grands diagrammes ; V42.9 : navigation clavier et tests ergonomiques Windows.
