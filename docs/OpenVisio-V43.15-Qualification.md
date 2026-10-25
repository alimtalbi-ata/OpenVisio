# OpenVisio V43.15 — public VSDX orthogonal routing intent

Author: Abdelhalim Talbi. Source branch: `develop/v43.15-public-orthogonal-routing-20261025`.

## Functional change
The external VSDX importer now recognizes a verifiable, static, axis-aligned
multi-segment Visio connector as an **orthogonal routing preference**. It retains
separate FC parallel links, connector captions and page-layer associations.
The original Visio bend coordinates are **not** retained: OpenVisio recomputes
obstacle-safe routes, and the importer adds a visible fidelity warning and a
counter in `metadata.orthogonal_connector_routes_approximated`.

Unsupported curves, formulas, diagonals, and geometry with inconsistent local
endpoints are not guessed into orthogonal links. This is **not** a claim of
Microsoft Visio Desktop fidelity.

## Actual local tests
- Before fix: 7 new regression tests, 4 errors against V43.14.
- After fix: 644 Python tests, 28 skipped, zero failures (Linux headless).
- Linux Tk/Xvfb: 644 tests, zero failures.
- New synthetic OPC/VSDX tests: 7 passed.
- Native Windows, Inno Setup and Microsoft Visio Desktop: not yet qualified
  at the time this note was written; check the CI run for the current commit.

## Provenance and release rules
No change to main; no automatic merge. Historical V43.4 original archive was
not available for full forensic reconciliation. The V43.14 baseline critical
engine blobs were compared with GitHub after CRLF/LF normalization.
