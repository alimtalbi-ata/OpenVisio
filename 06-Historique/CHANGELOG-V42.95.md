# OpenVisio V42.95 — SAN fabric layer preservation

Author: Abdelhalim Talbi. 2026-10-24. Source candidate; no production merge.

## Functional defect and fix

Duplicating a SAN connector with the GUI **Add parallel path** action silently discarded the original connector's `layer`. This caused a newly created physical FC path to remain visible when its fabric layer was hidden. `connect_equipment` now supports an explicit, validated `layer` argument; the GUI forwards the selected connector's layer. Creation on unknown or locked layers is rejected.

## Qualification categories

- Unit: new tests for fabric assignment, layer visibility and rejection of locked/unknown layers.
- Integration: native save/reopen and undo/redo; real Tk dialog exercised under Linux/Xvfb.
- Synthetic VSDX: not added in this version; earlier suites retained.
- Microsoft Visio Desktop fidelity: NOT QUALIFIED (no real Visio execution).
- Windows native: CI workflow prepared; no V42.95 binary may be claimed before successful build, smoke and artifact hash verification.
- GitHub checkout: independent clone on the candidate branch and critical Git blob checks; local bundle replay is not proof of remote checkout.

## Remaining gaps

The historical V43.4 ZIP is not available for byte-for-byte comparison. Historic test parity between local cumulative ZIP and GitHub is not complete. Internal application version remains 42.50.0. No production change or merge.
