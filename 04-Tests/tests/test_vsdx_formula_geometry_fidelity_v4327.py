"""V43.27: never present cached, formula-driven shape geometry as lossless.

Synthetic OPC fixtures exercise the external importer only; they do not certify
Microsoft Visio Desktop fidelity.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import VsdxFidelityError, export_vsdx, import_vsdx
from openvisio.vsdx_external import V


class FormulaDrivenVsdxGeometryFidelityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "formula-geometry.vsdx"
        export_vsdx(self.path, {
            "nodes": [{"id": "storage-a", "x": 80, "y": 72, "label": "Array"}],
            "edges": [],
        })
        self._convert_to_external_vsdx()

    def _convert_to_external_vsdx(
        self, formula_cell=None, formula_expression="GUARD(ThePage!PageWidth*0.5)"
    ):
        with ZipFile(self.path) as source:
            parts = {
                name: source.read(name)
                for name in source.namelist()
                if not name.startswith("openvisio/")
            }

        if formula_cell is not None:
            page_name = "visio/pages/page1.xml"
            root = ET.fromstring(parts[page_name])
            candidate = None
            for shape in root.findall(f".//{{{V}}}Shape"):
                cells = shape.findall(f"./{{{V}}}Cell")
                names = {cell.get("N") for cell in cells}
                if {"PinX", "PinY"}.issubset(names):
                    candidate = next(
                        (cell for cell in cells if cell.get("N") == formula_cell),
                        None,
                    )
                    if candidate is not None:
                        break
            if candidate is None:
                raise AssertionError("No eligible shape cell found: " + formula_cell)
            # Keep cached V unchanged; only the bounded formula allowlist is evaluated.
            candidate.set("F", formula_expression)
            parts[page_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        with ZipFile(self.path, "w", ZIP_DEFLATED) as target:
            for name, payload in parts.items():
                target.writestr(name, payload)

    def test_numeric_geometry_without_formula_remains_eligible_for_strict_mode(self):
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertEqual(imported["metadata"]["formula_driven_geometry_shapes"], 0)
        self.assertNotIn("fidelity_warnings", imported["metadata"])

    def test_supported_page_formula_is_evaluated_in_strict_mode(self):
        self._convert_to_external_vsdx("PinX")
        with ZipFile(self.path) as archive:
            root = ET.fromstring(archive.read("visio/pages/pages.xml"))
        page = root.find(f"./{{{V}}}Page")
        sheet = page.find(f"./{{{V}}}PageSheet")
        page_width = float(next(
            cell.get("V") for cell in sheet.findall(f"./{{{V}}}Cell")
            if cell.get("N") == "PageWidth"
        ))
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertAlmostEqual(imported["nodes"][0]["x"], page_width * 96.0 * 0.5, places=2)
        metadata = imported["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_evaluated_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_cells_evaluated"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 0)

    def test_unsupported_formula_reports_cached_value_fallback(self):
        self._convert_to_external_vsdx("PinX", "GUARD(UnsupportedCell*0.5)")
        metadata = import_vsdx(self.path)["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 1)
        self.assertEqual(len(metadata["formula_driven_geometry_examples"]), 1)
        self.assertTrue(any(
            "outside the supported scalar subset" in warning
            and "cached cell values were used" in warning
            for warning in metadata["fidelity_warnings"]
        ))

    def test_strict_mode_rejects_formula_driven_pin_geometry(self):
        self._convert_to_external_vsdx("PinX", "GUARD(UnsupportedCell*0.5)")
        with self.assertRaisesRegex(VsdxFidelityError, "formula-driven geometry"):
            import_vsdx(self.path, strict_fidelity=True)

    def test_formula_driven_dimensions_are_not_silently_accepted(self):
        self._convert_to_external_vsdx("Width", "UnsupportedFunction(2)")
        imported = import_vsdx(self.path)
        self.assertEqual(imported["metadata"]["formula_driven_geometry_shapes"], 1)
        with self.assertRaisesRegex(VsdxFidelityError, "formula-driven geometry"):
            import_vsdx(self.path, strict_fidelity=True)


if __name__ == "__main__":
    unittest.main()
