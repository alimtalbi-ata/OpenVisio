# OpenVisio V43.09 — SAN routing respects layer locks

Author: **Abdelhalim Talbi**. Candidate branch only; never merge automatically.

## Functional correction

`set_edge_routing()` could change a protected Fibre Channel link despite a locked
layer. The GUI filtered locked links, but headless commands did not. The
shared `assert_link_editable()` guard now protects the link and both endpoints
in both routing and metadata edits. Unlocked parallel links remain independently
routable. No destructive mutation occurs on refusal.

## Executed local qualification (Linux)

- V43.08 baseline: 597 tests, 26 skipped, 0 failures.
- New regression before fix: 7 tests, 4 failures.
- V43.09 after fix: 605 tests, 27 skipped, 0 failures.
- V43.09 full suite with `OPENVISIO_GUI_TESTS=1` under Xvfb: 605 tests, 0 failures.
- New focused Tk/Xvfb test: 8 tests, 0 failures.
- Mirrored source/test trees: 59/139 files identical.

## Windows build and independent checkout

Workflow `.github/workflows/openvisio-v43.09-windows-candidate.yml` runs on
Windows 2022 after a branch push, checks independent GitHub checkout and Git
blob SHA for core modules, runs tests and builds portable PyInstaller and Inno
Setup artifacts. These binaries must **not** be described as built or qualified
until the CI run and artifact hashes have actually been inspected.

## Limits

- Historical original V43.4 ZIP not available: historical parity not proven.
- Microsoft Visio Desktop real-file fidelity not tested.
- Interactive manual Windows acceptance test not performed.
- App internal version remains `42.50.0` (legacy build contract).
- No production deployment, no main modification.
