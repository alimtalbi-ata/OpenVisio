# OpenVisio v31.5 — Import SAN et états du zoning

Auteur : Abdelhalim Talbi.

Depuis **Import configurations SAN**, charger un export texte hors ligne Brocade ou Cisco MDS. Le parseur identifie les sections explicites « Effective configuration » Brocade comme actives déclarées, les zones Cisco comme configurées, et conserve un état inconnu lorsque la preuve est insuffisante. Le rapprochement du zoning et des chemins reste non destructif. Vérifier systématiquement le contexte de la commande et la complétude de l’export.

Aucune connexion aux équipements, ni validation effective du zoning en production.
