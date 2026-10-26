# OpenVisio — cumulative source and Windows candidate

## V43.23 combined candidate — static VSDX waypoints + canonical private-part protection (26 October 2026)

- Integrates static waypoint preservation for a constrained, public, formula-free orthogonal VSDX connector representation with the V43.22 private payload case guard.
- Each preserved route records a schema version, endpoint geometry signatures and bounded page-space points. The routing scene accepts the stored path only when both endpoints remain unchanged and no unrelated equipment rectangle is crossed; otherwise it invokes the normal obstacle-avoiding router.
- Preserves routes per edge, including parallel SAN links. Invalid schemas, non-finite/out-of-range coordinates, duplicate points, diagonal segments, excessive points and unsupported/formula-driven connector geometries are not trusted.
- The reserved private package entries `openvisio/document.json` and `openvisio/manifest.json` retain strict canonical case; this prevents a casing alias from silently falling back to lossy public geometry.
- The source and test trees are byte-identical mirrors. A separate Windows workflow pins important Git blobs, starts from an independent checkout, runs the full test suite and targeted regressions, builds and smoke-tests portable/installable Windows x64 outputs, generates Word/PDF, and audits the extracted cumulative ZIP.
- **Scope limit:** fixtures are synthetic; Microsoft Visio Desktop import/export round-trip is not tested. No manual Windows UI acceptance or real OpenVisio screenshot is claimed. The original V43.4 ZIP was not available for a new binary comparison in this run; prior audit findings are recorded in PR #54.
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

