# OpenVisio V42.88 — Protected SAN group operations (source candidate)

Author: **Abdelhalim Talbi**. Date: 2026-10-24.

## Functional correction

`group_commands.py` now rejects grouping/ungrouping of equipment on locked layers and rejects resizing a group when its descendants are locked or when resizing would move endpoints of a locked SAN link. The input document remains untouched on refusal. Unprotected grouping, resizing and undo/redo remain available.

## Evidence

- Baseline V42.86: 4 failures among 6 new targeted tests.
- Patched V42.88 local: 6/6 targeted tests PASS.
- Local cumulative Linux suite: 774 tests, 41 skipped, 0 failures.
- Bidirectional source mirror parity: 57/57 engine files and 163/163 test files.
- Historical tests restored to GitHub: `test_vsdx_audit_v426.py` (2 tests), `test_connector_labels_unlabelled_obstacles_v4247.py` (3 tests).

## Qualification boundaries

Unit/integration tests are synthetic and are **not** proof of Microsoft Visio fidelity. Windows native V42.88 build, smoke and CI must be evaluated independently on the published commit; previous V42.86 executables do not qualify V42.88. The original local V43.4 ZIP is not available for a complete comparison. Internal app version remains `42.50.0`. No actual Windows V42.88 screenshot is available at source-package creation.

## Reproduce

From a fresh GitHub checkout of `develop/v42.88-locked-san-group-operations-20261024`:

```sh
python verify_source_parity.py
PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q
```

Windows CI uses `.github/workflows/openvisio-v42.88-windows-candidate.yml` and `02-Compilation/Build-Windows-V42.88-Candidate.ps1`. No merge to `main` and no production changes.
