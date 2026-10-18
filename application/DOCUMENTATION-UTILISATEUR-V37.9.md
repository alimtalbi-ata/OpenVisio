# OpenVisio v38.0 — Documentation utilisateur
Auteur : Abdelhalim Talbi

## Dépendances des connexions SAN
1. Ouvrir un diagramme puis sélectionner une connexion.
2. Dans l'inspecteur, renseigner la section **Résilience SAN — domaines de défaillance de la connexion**.
3. Utiliser des identifiants cohérents entre connexions et équipements : Site, Châssis, Domaine électrique / PDU, Contrôleur, Domaine personnalisé.
4. Enregistrer le diagramme, puis lancer le diagnostic de redondance SAN pour identifier les domaines critiques communs.

Ces attributs sont déclaratifs. Une analyse documentaire ne prouve pas la séparation physique des infrastructures.

## Construction Windows
Exécuter `Build-OpenVisio-Windows.cmd` sur Windows x64 avec les prérequis de compilation. Les EXE ne sont pas fournis dans cette archive source.
