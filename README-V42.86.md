# OpenVisio V42.86 — External VSDX root identity and source checkout

Author: **Abdelhalim Talbi**. Candidate only; internal app version remains 42.50.0.

## Functional fix

External Visio VSDX XML parts must have their expected root QNames:
- `visio/pages/pages.xml`: Visio `Pages`
- `visio/pages/_rels/pages.xml.rels`: OPC `Relationships`
- `visio/pages/pageN.xml`: Visio `PageContents`

Previously, a syntactically valid but wrong page root could silently import zero nodes and edges. V42.86 fails closed with a clear error. XML DTD and resource-limit protections remain in place.

## Evidence and limits

Before patch: four failures among five new synthetic regression tests. After patch: five pass. Local Linux cumulative Python suite: **762 tests, 41 skipped, 0 failures**. Existing engine mirrors are identical; core module Git blob SHA values checked. One historical test file restored per GitHub test mirror (nested parallel SAN connector captions); the existing page-gap test was reverified. GitHub now contains 108 tests per mirror versus 161 locally, leaving 53 historical test files absent. Windows CI is configured to build a **V42.86 source candidate**, not a production release; do not claim its result until the Actions run completes.

No real Microsoft Visio desktop interoperability validation. No Windows V42.86 UI screenshots at the time of this commit. The historical V43.4 ZIP is unavailable, so complete parity with it cannot be claimed. Remaining historical tests on GitHub must be audited and restored. Never merge to main automatically.
