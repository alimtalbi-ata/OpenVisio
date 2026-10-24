# OpenVisio V42.89 — external VSDX inspector/importer parity

Author: Abdelhalim Talbi. 2026-10-24. Source candidate, not a Microsoft Visio fidelity certificate.

The external-package inspector no longer reports success for an empty ZIP, invalid OPC page relation, wrong XML root, or DTD-containing page. It now uses the same supported-geometry import path as the actual VSDX importer and reports page count and known fidelity warnings. Five synthetic regressions reproduced 4 failures and 1 error before correction; 5/5 pass after. The historical six-test inspector suite is restored to both source mirrors, with its external fixture corrected to use the Visio namespace.

Local cumulative Linux tests: 779 run, 41 skipped, 0 failures. The source and test mirrors pass `python verify_source_parity.py`. Windows candidate CI must independently validate a GitHub checkout before claiming Windows qualification.

Reproduce: `PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q`.
The app internal version remains 42.50.0 due to historical Windows build contracts; V42.89 identifies the candidate. The original V43.4 ZIP and actual Microsoft Visio-produced files are not available. Do not merge to main automatically.
