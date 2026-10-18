# Audit v36.9 — intégrité du cache portable

Auteur : Abdelhalim Talbi.

## Correction
La version précédente ne comparait que l'empreinte de l'archive embarquée à un marqueur `.complete`, sans revérifier les fichiers extraits. Le cache pouvait donc être altéré après publication.

La v36.9 relit chaque entrée du ZIP embarqué et compare taille et SHA-256 au fichier correspondant dans le cache, avant réutilisation. Les chemins sont bornés au répertoire du cache et les empreintes sont comparées en temps constant.

## Limites
Le contrôle est plus coûteux au démarrage pour un grand nombre de ressources. Les caches historiques restent conservés pour ne pas interrompre une autre instance. Les fichiers additionnels non référencés dans l'archive ne sont pas supprimés. Une compilation C# sur Windows reste nécessaire.
