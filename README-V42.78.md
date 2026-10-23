# OpenVisio V42.78 — VSDX inspector/importer payload parity

Author: Abdelhalim Talbi. Candidate sources only; internal app version remains 42.50.0.

## Business defect
A valid SHA-256 digest in a schema-3 VSDX manifest did not mean the embedded OpenVisio document could be opened. The inspector reported "consistent" for malformed JSON, duplicate keys, duplicate node IDs and invalid links, whereas import_vsdx rejected the same archive.

## Fix
After confirming the payload checksum, vsdx_consistency.inspect() now invokes the same bounded strict load_bytes() validator as import_vsdx(). Invalid embedded diagrams raise a ValueError. A checksum mismatch still reports "corrupted_payload"; valid schema-1 archives remain "legacy".

## Qualification
- 4 regression cases reproduced on V42.77, 5/5 tests pass after patch.
- Local Linux cumulative: 733 tests, 41 skipped, 0 failures.
- Windows CI workflow is configured for the dedicated branch; verify the actual run and binary provenance before claiming Windows success.
- No Microsoft Visio desktop fidelity qualification or new Windows UI screenshots.
- Historical test synchronization from V42.77 remains incomplete (58 tests absent from remote before this release); this patch adds 1 test file per mirror, not the missing historical suite.

## Safe release process
Never merge automatically into main. Preserve source mirrors and run verify_source_parity.py, targeted regression, cumulative tests, Windows PyInstaller/Inno Setup and smoke tests. Build scripts are source candidates, not a production release.
