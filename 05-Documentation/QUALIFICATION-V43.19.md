# OpenVisio V43.19 — Lossless equipment labels

**Author:** Abdelhalim Talbi  
**Candidate branch:** `develop/v43.19-no-label-truncation-20261025`  
**Base:** V43.18 commit `4ddeb5f0eb1b893a8a873240995770d65bdf7f65`.

## Correction

The Tk renderer previously sliced equipment labels to 40 characters, silently hiding the remainder while leaving the saved model unchanged. V43.19 removes that truncation and wraps long labels against the node width. The SVG exporter applies the same deterministic width estimate and emits positioned text spans. Explicit CRLF/CR/LF breaks, blank lines, spaces, WWPNs, and long unbroken tokens remain visible in the rendered result. Wrapping affects only presentation; the model is not rewritten.

## Local qualification before publication

- Targeted V43.19 tests: 6 passed after correcting a wrapping-boundary assertion found during test development.
- Full Python suite: 666 tests, 28 skipped, 0 failures.
- Source mirror parity: 60 engine modules and 149 test files.
- Windows build: pending the V43.19 hosted candidate workflow.
- Synthetic renderer tests only; not a Microsoft Visio Desktop fidelity test.

## Historical ZIP reconciliation

The original local cumulative V43.4 ZIP was not present in the runtime. The authentic GitHub Actions checkout artifacts for V43.04 and V43.18 were retrieved and compared independently: the V43.04 checkout contained 2,415 files, the V43.18 checkout contained 2,514, 99 were newly added, 30 existing files had changed content, and no V43.04 files were removed. These are GitHub snapshot-to-snapshot statistics, **not** a bit-for-bit comparison with the missing local ZIP. The source mirrors 03-Sources/openvisio and python/openvisio plus test mirrors 04-Tests/tests and python/tests are checked by verify_source_parity.py and the Windows workflow.

## Qualification limits

No Microsoft Visio Desktop round-trip test or manual end-user Windows session is claimed by these synthetic tests. Hosted Windows CI qualifies the build pipeline, not every end-user PC.
