# OpenVisio v28.7 — chemins FC de bout en bout

Auteur : Abdelhalim Talbi.

Module `src/san-path-explorer.js` : `exploreSanPaths({nodes,edges})` retourne les chemins serveur/hôte → switch(s) → stockage, la Fabric déclarée, les identifiants des liens et un bilan par couple serveur/stockage.

La redondance A/B n’est considérée documentée que si des chemins A et B sans switch ni lien partagé sont trouvés. Les chemins inconnus ou traversant plusieurs fabrics ne sont pas certifiés. Les données ne sont pas modifiées.

Limites : aucune interrogation du SAN, aucun contrôle des zones/masking réel, ni garantie de multipathing. Les chemins sont limités en profondeur et en nombre pour protéger l’interface. Le module n'est pas encore branché au canvas principal.

## Tests
`npm test` ; tests ciblés `node --test tests/san-path-explorer-v287.test.mjs`.
