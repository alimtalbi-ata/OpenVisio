# Audit ciblé v33.7
- L'interface HTML historique reste monolithique et contient des panneaux SAN complexes ; la commande contextuelle est une amélioration incrémentale, pas une refonte totale.
- Le script Windows recherche maintenant ISCC dans PATH et supprime l'ancien installateur avant construction, évitant un faux positif de succès.
- Le SDK .NET et Inno Setup nécessitent un environnement Windows et un accès réseau ; la compilation native n'est pas vérifiable ici.
- La validation de l'installation silencieuse WebView2 et les captures réelles restent à faire sur une VM Windows.
