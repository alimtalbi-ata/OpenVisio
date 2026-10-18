# OpenVisio v28.6 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

1. Démarrer `OpenVisio-Windows.bat`.
2. Sélectionner un objet ou une connexion du canvas.
3. Dans l’inspecteur SAN, consulter les liens déclarés, ports FC et WWPN lorsque renseignés.
4. Filtrer Fabric A/B ; seules les lignes explicitement associées à la fabric sont retenues.
5. Cliquer sur « Voir … » pour sélectionner un équipement adjacent.

Les ports proviennent des champs `port`, `fcPort`, `wwpn`, `portWwpn` du JSON. Les WWPN sont validés au format octets séparés par deux-points. Le diagnostic ne découvre pas les équipements et n'établit pas le multipathing réel. Aucune modification automatique des connexions.
