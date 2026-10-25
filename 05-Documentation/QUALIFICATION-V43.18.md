# OpenVisio V43.18 - Multiline diagram labels in SVG

**Author:** Abdelhalim Talbi  
**Candidate branch:** `develop/v43.18-svg-multiline-labels-20261025`  
**Baseline:** V43.17 source checkout `47cf8ec55081f231c83436592360395b1b0775d0`

## Correction

Equipment names and SAN connector captions containing explicit line breaks now export as separate SVG `tspan` rows instead of relying on literal newlines, which SVG normally collapses in ordinary text. Connector-label collision boxes reserve the full multiline height and use the longest line for width, so label placement better matches the visible text. Single-line SVG labels retain the existing plain-text output.

## Local tests executed

- Before correction: 3 of 4 new regression tests failed; single-line compatibility passed.
- After correction: 4 new regression tests passed.
- Full Python suite on the V43.17 GitHub source checkout plus this patch: 660 tests, 28 skipped, 0 failures.
- `verify_source_parity.py`: 59 mirrored engine modules and 148 mirrored test files matched.
- A real SVG file was generated from a synthetic SAN diagram and parsed by `xml.etree.ElementTree`.

## Qualification limits

These are synthetic SVG/model tests, not Microsoft Visio Desktop fidelity tests. Windows build and installer qualification must be recorded only after the V43.18 GitHub Actions workflow completes successfully. The original local V43.4 ZIP was not found in the current working directory or OpenVisio Library inventory, so historical V43.4 equivalence remains unverified.
