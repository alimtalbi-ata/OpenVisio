# OpenVisio V42.97 — SVG finite dimension validation

Author: Abdelhalim Talbi. Candidate source branch only; main unchanged.

Functional change: `to_svg` rejects NaN, infinity, booleans, negative margins and invalid width/height before emitting malformed SVG. Zero margin remains supported. Both source mirrors are updated.

Reproducible qualification: `PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q`; on Windows use `02-Compilation/Verify-GitHub-Checkout-V42.97.ps1`. CI Windows compiles PyInstaller portable and Inno Setup installer only after tests pass.

Local full-suite baseline: 823 tests, 43 skipped, 0 failures. CI Windows and Microsoft Visio Desktop fidelity are separate gates, not claimed by this document.

The historical V43.4 ZIP is unavailable. Therefore complete reconciliation with that original artifact is not certified. No automatic merge into main.
