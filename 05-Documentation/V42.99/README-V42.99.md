# OpenVisio V42.99 — SVG XML 1.0 integrity

**Author:** Abdelhalim Talbi  
**Date:** 2026-10-24  
**Status:** source candidate; Windows native CI pending.

## Functional correction

SVG export previously emitted forbidden XML control characters and unpaired Unicode surrogates from imported equipment and connector captions/identifiers. These produced XML parsing errors or a UTF-8 encoding exception. The SVG serializer now replaces XML 1.0 forbidden code points with U+FFFD while preserving valid Unicode and without modifying the original OpenVisio document.

Both `python/openvisio/export.py` and `03-Sources/openvisio/export.py` contain the identical fix. New tests exist in both test trees.

## Evidence from this development environment

- Three regression tests reproduced failures on V42.98 before the correction.
- Linux Python 3.13: 550 tests, 22 skipped, 0 failures, after the correction.
- Mirrored source/tests: 550 tests, 22 skipped, 0 failures.
- Real Microsoft Visio Desktop round-trip: **not tested**.
- Interactive Windows UI: **not tested here**.
- Windows portable and installer V42.99: **must be compiled and qualified by GitHub Actions**; no unbuilt binary is included as V42.99.

## Architecture / data flow

`Validated diagram -> routing and labels -> XML 1.0 character normalization -> XML escaping -> SVG -> atomic file publication`

The normalization applies only to SVG output. It does not rewrite model JSON, Visio imports, labels in the editor, or undo/redo history.

## Reproducible GitHub checkout

The V42.99 Windows workflow runs `02-Compilation/Verify-GitHub-Checkout-V42.99.ps1`, checks the exact GitHub commit, critical engine blob hashes, mirror parity, and Python tests before compiling. Branch: `develop/v42.99-svg-xml10-integrity-20261024`. No automatic merge to `main`.

## Outstanding historical parity

The original V43.4 ZIP is unavailable in this execution. The V42.98 candidate source is confirmed to match GitHub engine blobs after CRLF/LF normalization for `model.py`, `vsdx.py`, `render.py`, and `export.py`; this is **not** a V43.4 reconciliation certificate.

## Screenshots

No new real Windows UI screenshots were captured during this Linux run. No simulated screenshot is presented as evidence.
