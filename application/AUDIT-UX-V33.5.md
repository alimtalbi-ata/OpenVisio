# Audit ciblé v33.5
Le module `src/inspector.js` recrée les champs à chaque rendu; la v33.5 ajoute un filtre non destructif déclenché après `openvisio:canvas-painted`, sans modifier le modèle de données ni les gestionnaires de mise à jour. La page index.html reste monolithique et devra être découpée ultérieurement. Le pipeline Windows demeure non qualifié nativement.
