# OpenVisio v41.65 — Qualification des scénarios de restauration

Auteur : Abdelhalim Talbi.

Le script `application/windows/Test-Binary-Recovery-Scenarios.ps1` produit désormais un rapport JSON durable via `-ReportPath`, en dehors du répertoire temporaire supprimé. Les scénarios échoués entraînent un code de sortie non nul. Trois tests Node.js couvrent ces invariants.

**Limite :** PowerShell Windows, compilation native, installation et lancement réels non exécutés dans cet environnement Linux. Les fichiers `.exe` ne sont pas fournis.
