# OpenVisio V43.19 — Lossless equipment labels

**Author:** Abdelhalim Talbi  
**Candidate branch:** develop/v43.19-no-label-truncation-20261025  
**Base:** V43.18 commit 4ddeb5f0eb1b893a8a873240995770d65bdf7f65.

## Correction

The Tk renderer previously sliced equipment labels to 40 characters, silently hiding the remainder while leaving the saved model unchanged. V43.19 removes that truncation and wraps long labels against the node width. A shared helper reduces font size only when necessary to fit the available shape height. When a label spans multiple lines, space is reserved for the equipment glyph at the upper-left so icon and text do not collide. SVG uses the same lossless wrapping and adaptive font estimate. Short single-line labels keep their previous SVG text-node form. Wrapping affects only presentation; the model is not rewritten.

## Local qualification of the final patch before publication

- Targeted V43.19 tests: 7 passed.
- Full Python suite: 667 tests, 28 skipped, 0 failures.
- Source mirror parity: 60 engine modules and 149 test files.
- Actual Tk widget screenshot under Linux/Xvfb captured and visually inspected; it demonstrates a synthetic SAN multipath diagram with long host, switch and storage labels. It is not a Windows screenshot.
- Hosted Windows native build is to be qualified by the branch-specific GitHub Actions workflow after this patch is pushed.
- Synthetic tests only; not a Microsoft Visio Desktop fidelity test.

## Historical ZIP reconciliation

The original local cumulative V43.4 ZIP was not present in the runtime. The authentic GitHub Actions checkout artifacts for V43.04 and V43.18 were retrieved and compared independently: the V43.04 checkout contained 2,415 files, the V43.18 checkout contained 2,514, 99 were newly added, 30 existing files had changed content, and no V43.04 files were removed. These are GitHub snapshot-to-snapshot statistics, not a bit-for-bit comparison with the missing local ZIP. The source mirrors 03-Sources/openvisio and python/openvisio plus test mirrors 04-Tests/tests and python/tests are checked by verify_source_parity.py and the Windows workflow.

## Qualification limits

No Microsoft Visio Desktop round-trip test or manual end-user Windows session is claimed. Hosted Windows CI qualifies the build pipeline, not every end-user PC.
