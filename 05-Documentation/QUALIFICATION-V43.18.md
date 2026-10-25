# OpenVisio V43.18 - Multiline diagram labels in SVG

**Author:** Abdelhalim Talbi  
**Candidate branch:** `develop/v43.18-svg-multiline-labels-20261025`  
**Implementation commit:** `d35881cc0aa6cb99ca1630f9e01c79329b9c3bd7`  
**Review:** [PR #52](https://github.com/alimtalbi-ata/OpenVisio/pull/52), draft, not merged.

## Correction

Equipment names and SAN connector captions containing explicit line breaks now export as separate SVG `tspan` rows instead of relying on literal newlines, which SVG normally collapses in ordinary text. Connector-label collision boxes reserve the full multiline height and use the longest line for width, so label placement better matches the visible text. Single-line SVG labels retain the existing plain-text output.

## Tests and qualification results

- Before correction: 3 of 4 new regression tests failed; single-line compatibility passed.
- After correction: 4 of 4 new regression tests passed.
- Full Python suite on Linux: 660 tests, 28 skipped, 0 failures.
- Independent Windows 2022 / Python 3.12 checkout: 660 tests, 24 skipped, 0 failures.
- Source mirror parity: 59 engine modules and 148 test files.
- Windows regression set, frozen executable IO/Tk startup smoke, Inno Setup compilation, silent install and installed-executable smoke: PASS.
- Successful implementation qualification: [GitHub Actions run 40177965587](https://github.com/alimtalbi-ata/OpenVisio/actions/runs/40177965587), commit `d35881cc0aa6cb99ca1630f9e01c79329b9c3bd7`.
- PyInstaller emits a non-fatal warning that `api-ms-win-core-path-l1-1-0.dll` could not be resolved. The build and smoke checks nevertheless succeeded.

## Qualification limits

These are automated synthetic SVG/model tests, not Microsoft Visio Desktop fidelity tests. No real Visio corpus or manual interactive Windows acceptance was available in this run. The Windows build took place on a hosted CI runner; compatibility on a separate end-user Windows installation remains to be confirmed.

The original local V43.4 ZIP was not found in the runtime or in the OpenVisio Library ZIP inventory. A development branch named `develop/v43.04-clickable-san-connector-captions-20261024` exists, but it is not the missing archive and does not certify historical V43.4 equivalence. Obtain the original ZIP before making that claim.

`main` remains unchanged; no merge was performed.
