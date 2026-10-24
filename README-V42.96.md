# OpenVisio V42.96 — SVG Fabric visibility

Author: Abdelhalim Talbi. Candidate, not a production release.

## Functional change
SVG export now uses the same non-destructive visible-layer projection as the Tk editor. Hidden SAN Fabric paths, hidden equipment and incident links are excluded. The native OpenVisio document keeps every hidden object. Call `to_svg(document, include_hidden_layers=True)` or `export_svg(path, document, include_hidden_layers=True)` to explicitly export the complete topology.

## Evidence
Synthetic regression: 6 headless tests, 1 real Tk/Xvfb integration test. The CI workflow builds Windows portable and Inno Setup candidates only after source parity and tests pass. No claim of Microsoft Visio Desktop fidelity. Internal version remains 42.50.0.

## Source provenance and limits
Based on PR #28 head aab91ebb75ab0603f135f29fcf72002f3cf663c0. Mirrored engine files in 03-Sources/openvisio and python/openvisio are updated together. The original V43.4 ZIP is unavailable for direct comparison; remaining historical tests are not claimed synchronized. No merge to main.
