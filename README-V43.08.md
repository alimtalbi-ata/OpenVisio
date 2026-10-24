# OpenVisio V43.08 — Protected SAN connector geometry

Author: Abdelhalim Talbi. Base: V43.07, branch `develop/v43.08-locked-san-geometry-20261024`.

## Functional correction
A Fibre Channel connector on a locked layer was previously rerouted when an otherwise unlocked endpoint was dragged, aligned, resized or given a different shape. The new `geometry_lock.assert_geometry_editable` guard rejects indirect changes to the geometry of locked links and links touching a locked endpoint. The editor calls the guard before drag and alignment/distribution; `property_commands.update_equipment` calls it only for geometry-affecting changes. Label/metadata edits and independent fabric edits remain available.

## Reproduction and tests (local Linux)
- Before: 5 of 7 V43.08 tests failed under Tk/Xvfb.
- After: 597 Python tests, 26 skipped, 0 failures; 7 targeted tests passed under Tk/Xvfb.
- Source mirror parity: 59 Python engine modules and 138 Python test modules in each tree.
- These are synthetic tests, not Microsoft Visio Desktop fidelity certification.

## GitHub checkout and Windows
New V43.08 workflow fixes the prior V43.07 push-branch mismatch, verifies a fresh checkout and critical Git object IDs, and runs the native Windows build and smoke checks. CI and Windows binary status must be checked from actual GitHub Actions run artifacts; no Windows result is inferred from Linux tests.

## Historical V43.4 reconciliation
The original V43.4 ZIP was not available among mounted archives or retrieved Library results. The V43.07 source baseline is present on GitHub, and critical `model.py`, `vsdx.py`, `render.py` blobs match the V43.07 local ZIP after CRLF normalization. This does not certify historical V43.4 parity.

## Limits
No Microsoft Visio Desktop test corpus or interactive Windows manual acceptance test is available. No change to main and no automatic merge.
