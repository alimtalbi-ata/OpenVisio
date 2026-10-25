# OpenVisio - cumulative source and Windows candidate

## V43.21 candidate (25 October 2026)

This branch adds canonical raw ZIP-member validation to both VSDX importer mirrors and to the cumulative release archive validator. It is a source candidate, not a production release, and it is not certified against Microsoft Visio Desktop. The internal application version remains 42.50.0 for legacy build compatibility.

- Source: 03-Sources/openvisio and python/openvisio; core model.py, vsdx.py, render.py, routing.py and parallel_geometry.py are included.
- Tests: 04-Tests/tests and python/tests; V43.21 coverage rejects path traversal aliases, dot/empty segments, Windows colon syntax and case-insensitive duplicate OPC members.
- Build: 02-Compilation/Build-Windows-V43.21-Candidate.ps1 and the dedicated GitHub Actions workflow; the final cumulative ZIP is created only after Windows portable/installer smoke and archive-integrity validation pass.
- Documentation: 05-Documentation/V43.21-CANONICAL-PATHS.md and its SVG diagram; the CI-generated release kit includes Word/PDF qualification briefs and PDF page-render QA.
- Evidence boundary: no real Microsoft Visio Desktop round-trip or manual interactive Windows application screenshot is claimed.

The historical V43.4 archive is not copied over the current engine. Its partial manifest and missing mirrors/dependencies are described in the V43.21 branch qualification report.

## Historical release notes

OpenVisio v41.15 — livraison cumulative. Auteur : Abdelhalim Talbi. Voir QUALIFICATION-V41.15.md.


## v41.16
Voir QUALIFICATION-V41.16.md : raccordement transactionnel du rendu, 1747 tests PASS.

## v41.18
Benchmark comparatif synthétique du cache et tests de conservation des routes non invalidées. Voir QUALIFICATION-V41.18.md.

