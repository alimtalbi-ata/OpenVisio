# OpenVisio v41.13 — Mutation reconciliation
Auteur : Abdelhalim Talbi

## Changes
- Detect newly added edges as well as updated and deleted edges.
- Expose a snapshot-isolated mutation session for editor commands, including undo/redo.
- Preserve existing LRU routing cache; no parallel cache introduced.

## Limitations
- Full editor command centralization not yet proven.
- Windows binary compilation and actual Windows screenshots not performed.
- No comparative benchmark on real SAN diagrams in this release.
- Historical Word/PDF guides are retained, not comprehensively refreshed.

## Test evidence
`npm test`: PASS (executed on Linux, Node.js).
