## V43.22 candidate — static VSDX waypoints with geometry-safe fallback (25 October 2026)

- The external VSDX importer preserves static bend coordinates only for the constrained public, formula-free orthogonal connector format it can verify; it does not evaluate arbitrary Visio formulas, dynamic glue or unsupported coordinate frames.
- Each preserved `visio_route` records a schema version, endpoint geometry snapshots and bounded waypoints. Moving/resizing either endpoint or introducing an intersecting obstacle invalidates the stored route and delegates to the regular obstacle-avoiding router.
- Parallel SAN paths retain their individually imported routes rather than being collapsed to one cached route. Malformed, diagonal, non-finite or overlong route records are rejected by the normal document validation contract.
- CI runs the full Python test suite and targeted static-route regressions, then builds and smoke-tests Windows x64 portable/installable binaries and a cumulative archive from the exact checkout. Microsoft Visio Desktop round-trip remains explicitly NOT TESTED.
- Build scripts: `02-Compilation/Build-Windows-V43.22-Candidate.ps1`; workflow: `.github/workflows/openvisio-v43.22-windows-candidate.yml`. All generated binaries must come from this workflow, not be represented by local stubs.
- Author: Abdelhalim Talbi.

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

