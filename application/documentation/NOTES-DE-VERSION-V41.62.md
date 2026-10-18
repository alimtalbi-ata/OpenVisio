# OpenVisio v41.62 — Diagnostic et reprise des publications binaires

Auteur : Abdelhalim Talbi

## Évolutions
- Ajout de `windows/Inspect-Binary-Recovery.ps1` : inspection non destructive par défaut des répertoires `binary`, `binary.previous` et `binary.pending`.
- Validation des deux artefacts, des tailles et des empreintes SHA256 du manifeste avant toute restauration.
- Restauration explicite uniquement avec `-RestorePrevious -ConfirmRecovery`, si la publication actuelle est absente, la sauvegarde valide et aucun staging résiduel présent.
- Rapport `binary-recovery-assessment.json` y compris en cas de refus.

## Limites
Tests Node.js sous Linux uniquement. Aucun exécutable Windows compilé, aucun scénario de récupération PowerShell exécuté sous Windows. Ne pas confondre les tests de présence de garde-fous avec un test d'interruption réelle.

## Commandes Windows (non exécutées ici)
`powershell -NoProfile -File windows\Inspect-Binary-Recovery.ps1`
`powershell -NoProfile -File windows\Inspect-Binary-Recovery.ps1 -RestorePrevious -ConfirmRecovery`
