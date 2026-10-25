# OpenVisio V43.11 — neutral switch identity / VSDX export guard

Author: **Abdelhalim Talbi**. Based on V43.10 commit `949f15e27000c3c222f547e82f9d566d9230ef7d`.

## Functional fix

- Historical `shape="switch"` is a **neutral switch**, distinct from `san-switch` and `network-switch`; no inferred SAN identity.
- Public VSDX XML exports the exact `OpenVisio switch` shape name; the external importer can recover that category without the private OpenVisio JSON payload.
- Unknown custom shapes remain valid in native `.ovjson` files but now raise `UnsupportedVsdxShapeError` **before** creating an output folder or replacing an existing VSDX. The error identifies the node and asks for an explicit supported shape. No silent conversion to a server.
- A dedicated neutral pictogram is shared by Tk and SVG.

## Reproduction and tests

Baseline V43.10: exporting a synthetic document containing `shape="switch"` fails with `PublicVsdxFidelityError: Catégorie de forme VSDX modifiée`.

Linux local qualification: **618 tests, 28 skipped, 0 failures**; 7 new tests exercise native save, neutral/SAN/LAN classification, public XML import, 2 parallel FC links, rejection of unknown kinds and atomic output protection.

```bash
python verify_source_parity.py
PYTHONPATH=python python -m unittest discover -s python/tests -p 'test_*.py' -q
```

## Limits

The public VSDX fidelity audit is synthetic and **does not** certify interoperability with Microsoft Visio Desktop, masters, rotations, formulas, multi-page fidelity, or manual Windows interaction. Windows CI, PyInstaller and Inno Setup must be evaluated separately. Historical V43.4 ZIP was not available for full reconciliation. No change to main; PR must remain draft.
