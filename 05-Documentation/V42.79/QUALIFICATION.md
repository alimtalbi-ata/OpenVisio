# OpenVisio V42.79 — VSDX OPC directory compatibility

Author: **Abdelhalim Talbi**. Candidate branch; no production release.

## Functional change
Schema-3 VSDX integrity now ignores explicit ZIP directory entries (for example `visio/` and `openvisio/`), which are container metadata rather than OPC package parts. Previously, adding harmless directory markers caused `inspect()` to report `modified` and `import_vsdx()` to reject an unchanged drawing. New real parts (including masters and relationships) are still detected; unsafe ZIP traversal entries remain rejected; schema-3 manifest entries ending in `/` are invalid.

## Evidence and qualification
- **Before patch:** 2 of 3 new targeted tests failed (false modification).
- **After patch:** 3 of 3 targeted tests passed.
- **Linux cumulative:** 736 tests executed, 41 skipped, 0 failures.
- **Mirror parity:** 57 Python engine files and 154 test files in the local cumulative candidate.
- **Remote Git blob verification:** `model.py`, `vsdx.py`, `render.py`, `vsdx_consistency.py` in both engine paths plus both test mirrors match local candidate Git hashes (12/12).
- **Historical regression recovered:** `test_vsdx_page_gap_v4261.py` in both test mirrors.
- **Windows V42.79 CI:** not observed yet; no Windows V42.79 binaries are claimed.
- **Real Microsoft Visio fidelity:** not tested; synthetic VSDX fixtures only.
- **Screenshots:** no new real Windows captures; no simulated screenshot is represented as real.
- **V43.4:** source ZIP unavailable for comparison; GitHub cumulative tests still incomplete.
- **Internal app version:** `42.50.0`, separate from source candidate number V42.79.

## Reproducibility
Run `PYTHONPATH=python python verify_source_parity.py` then `PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q` from the repository root. Native Windows candidate build recipe: `02-Compilation/Build-Windows-V42.79-Candidate.ps1`; CI workflow: `.github/workflows/openvisio-v42.79-windows-candidate.yml`. Build success must be established by an actual GitHub Actions run before distributing V42.79 executables.

## Remaining work
Synchronize the 57 remaining historical test files; qualify a complete GitHub Windows checkout and build; normalize versioning; run Microsoft Visio desktop round-trip on real VSDX fixtures. Draft PR only, never merge automatically.
