# Audit v36.8

Correction du cache portable : marqueur de version insuffisant, risque de concurrence entre instances. Nouveau mutex nommé, empreinte SHA-256 de l’archive embarquée, staging unique, restauration en cas d’échec. Limites : empreinte globale ne vérifie pas individuellement chaque fichier extrait après publication ; tests natifs Windows nécessaires.
