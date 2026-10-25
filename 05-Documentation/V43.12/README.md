# OpenVisio V43.12 — External Visio master identity (candidate)

**Author:** Abdelhalim Talbi. **Base:** V43.11 / commit `80c3d2782a7e4aaca2baa30aa67b24d5e75b6057`.

## Business defect and scope

A Microsoft Visio stencil may store its device identity in `visio/masters/masters.xml` while the placed page shape carries only `NameU=Sheet.42` and a `Master` reference. V43.11 defaulted such FC switches to a server, losing their SAN shape identity in an external VSDX import.

V43.12 resolves public master IDs and conservatively classifies named vendor stencils (e.g. Brocade G720 and Cisco MDS 9148). Explicit `OpenVisio` types take precedence. Free-form captions never determine hardware identity. Duplicate master IDs are rejected. Parallel connectors and labels remain separate. No master geometry, styling, formulas or dynamic glue are claimed.

## Test evidence and limits

- Before fix: 6 new synthetic VSDX tests, **3 failed** (classification and duplicate master identity).
- After fix: 6 new tests passed. Full Linux Python suite: **624 run, 28 skipped, 0 failures**.
- Full Linux Tk/Xvfb suite: **624 run, 0 failures**.
- Windows build/CI: **not qualified until a completed GitHub Actions run is inspected**.
- Real Microsoft Visio Desktop fidelity and manual Windows UI acceptance: **not qualified**.
- Original historical V43.4 ZIP: **unavailable**, so exact V43.4 reconciliation remains open.

## Windows reproducibility

`openvisio-v43.12-windows-candidate.yml` checks out the exact GitHub branch, runs a separate independent clone, verifies critical Git blob SHAs and source/test mirrors, executes tests, builds a PyInstaller portable EXE and Inno Setup installer, then runs frozen smoke tests. Only binaries from a successful run may be called Windows-qualified.

This PR does not modify `main` and must not be auto-merged.
