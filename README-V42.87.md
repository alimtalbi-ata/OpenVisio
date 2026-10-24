# OpenVisio V42.87 — Locked-layer command integrity

Author: Abdelhalim Talbi. Candidate only; internal application version 42.50.0.

## Functional change
Editing commands now reject deletion of equipment and links protected by locked layers, including incident links to locked endpoints. Connection creation to locked equipment is rejected at the command boundary, not only by the GUI hit-test. Unrelated unlocked edits remain supported with undo/redo.

## Evidence and qualification
Five assertions were reproduced failing before the patch; all six new tests passed locally after the patch. Linux cumulative tests: 768 executed, 41 skipped, 0 failures (local V42.86 ZIP plus this patch). Historical test_layers_v426.py is restored to both GitHub test mirrors (10 historical tests). CI Windows V42.87 is configured, not yet verified at this commit. No real Microsoft Visio interoperability test. No new real Windows UI screenshot.

## Source provenance and limits
The V42.86 baseline GitHub blob SHAs for model.py, vsdx.py, render.py and vsdx_external.py matched the V42.86 local cumulative ZIP exactly. This PR updates commands.py in both engine mirrors and includes tests, a Windows source candidate workflow and scripts. The historical V43.4 ZIP is unavailable; complete V43.4 parity cannot be certified. Never merge automatically to main.
