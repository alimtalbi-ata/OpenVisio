# OpenVisio V43.07 — SAN fabric property lock enforcement

**Author:** Abdelhalim Talbi  
**Status:** Candidate; draft PR; do not merge automatically.

## Business defect and correction

The editor UI already excluded locked SAN fabric layers from editable hit-tests, but
the headless property commands could still change equipment labels, shape dimensions,
FC ports, and fabric metadata. This allowed scripts and stale GUI dialogs to bypass
a locked layer. The commands now reject changes to:

1. Equipment on a locked layer.
2. A connection assigned to a locked layer.
3. A connection on an otherwise editable layer when either endpoint is locked.

Changes to unrelated unlocked fabrics still succeed. Input documents are not mutated
on refusal. The policy matches the existing `project_editable()` projection.

## Reproduced and executed

- Before patch: 3 failures in 5 new headless regression tests.
- After patch: 590 Python tests on Linux, 24 skipped, 0 failures.
- Actual Tk/Xvfb GUI: 7 new regression tests passed; SAN parallel-link dialog
  tested separately with 5 tests passed.
- Local mirrored source parity: 58 Python engine modules, 137 test modules.
- Exact Git blobs on the dedicated branch:
  - `property_commands.py` (both copies): `91cc907da51e7e8d102c5215e6be480badf5fd3d`
  - `test_property_layer_lock_v4307.py` (both copies): `4fddda4cb29e27bd891d87f1022e6859e21f839b`

## Independent checkout and Windows

The V43.07 workflow includes a clean GitHub clone, pinned SHA checks for
`model.py`, `vsdx.py`, `render.py`, `property_commands.py` and mirrored
tests, Python tests, PyInstaller portable build, Inno Setup installer and
functional smoke tests. These are **planned CI steps, not passed evidence** until
a completed workflow run is observed. Windows native V43.07 binaries must not
be inferred from the V43.06 artifacts.

## Qualification boundaries

- Unit/integration: qualified locally as described above.
- GUI: Tk on Linux/Xvfb, not a physical Windows desktop.
- Microsoft Visio: no real Desktop round-trip qualification.
- Historical V43.4: original ZIP not available; exhaustive comparison pending.
- Main branch: unchanged. No production changes.

## Next step

Complete an independent GitHub checkout and Windows CI, then exercise a
multipath SAN topology in the actual Windows portable and installed GUI.
