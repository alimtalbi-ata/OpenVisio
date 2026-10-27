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
        self, formula_cell=None, formula_expression="GUARD(ThePage!PageWidth*0.5)",
        rename_cell_to=None,
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
            if rename_cell_to is not None:
                candidate.set("N", rename_cell_to)
            parts[page_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        with ZipFile(self.path, "w", ZIP_DEFLATED) as target:
            for name, payload in parts.items():
                target.writestr(name, payload)

    def _duplicate_shape_cell(self, name="PinX", duplicate_name=None):
        duplicate_name = duplicate_name or name
        with ZipFile(self.path) as source:
            parts = {
                part: source.read(part)
                for part in source.namelist()
                if not part.startswith("openvisio/")
            }
        page_name = "visio/pages/page1.xml"
        root = ET.fromstring(parts[page_name])
        candidate = None
        for shape in root.findall(f".//{{{V}}}Shape"):
            cells = shape.findall(f"./{{{V}}}Cell")
            names = {cell.get("N") for cell in cells}
            if {"PinX", "PinY"}.issubset(names):
                candidate = next((cell for cell in cells if cell.get("N") == name), None)
                if candidate is not None:
                    index = list(shape).index(candidate)
                    duplicate = ET.fromstring(ET.tostring(candidate))
                    duplicate.set("N", duplicate_name)
                    shape.insert(index + 1, duplicate)
                    break
        if candidate is None:
            raise AssertionError("No eligible shape cell found: " + name)
        parts[page_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with ZipFile(self.path, "w", ZIP_DEFLATED) as target:
            for part, payload in parts.items():
                target.writestr(part, payload)

    def test_duplicate_direct_shape_cell_is_rejected_before_dict_overwrite(self):
        self._duplicate_shape_cell("PinX", "PinX")
        with self.assertRaisesRegex(ValueError, "Duplicate ShapeSheet cell name"):
            import_vsdx(self.path)

    def test_case_variant_duplicate_direct_shape_cell_is_rejected(self):
        self._duplicate_shape_cell("PinX", "pinx")
        with self.assertRaisesRegex(ValueError, "Duplicate ShapeSheet cell name"):
            import_vsdx(self.path)

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

    def test_explicit_inch_literal_is_evaluated_in_strict_mode(self):
        self._convert_to_external_vsdx("PinX", "GUARD(12 in)")
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertEqual(len(imported["nodes"]), 1)
        self.assertAlmostEqual(imported["nodes"][0]["x"], 12 * 96.0, places=2)
        metadata = imported["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_evaluated_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 0)

    def test_explicit_metric_width_is_evaluated_before_geometry_validation(self):
        self._convert_to_external_vsdx("Width", "GUARD(120 mm)")
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertEqual(len(imported["nodes"]), 1)
        self.assertAlmostEqual(imported["nodes"][0]["width"], (120.0 / 25.4) * 96.0, places=2)
        metadata = imported["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_evaluated_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 0)

    def test_unsupported_formula_reports_cached_value_fallback(self):
        self._convert_to_external_vsdx("PinX", "GUARD(UnsupportedCell*0.5)")
        metadata = import_vsdx(self.path)["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 1)
        self.assertEqual(len(metadata["formula_driven_geometry_examples"]), 1)
        self.assertTrue(any(
            "could not be evaluated safely" in warning
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
        self.assertEqual(imported["metadata"]["formula_driven_geometry_unresolved_shapes"], 1)
        with self.assertRaisesRegex(VsdxFidelityError, "formula-driven geometry"):
            import_vsdx(self.path, strict_fidelity=True)

    def test_supported_formula_with_invalid_geometry_uses_cache_instead_of_dropping_shape(self):
        self._convert_to_external_vsdx("Width", "0")
        imported = import_vsdx(self.path)
        metadata = imported["metadata"]
        self.assertEqual(len(imported["nodes"]), 1)
        self.assertEqual(metadata["formula_driven_geometry_evaluated_shapes"], 0)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 1)
        self.assertTrue(any("invalid evaluated geometry" in item
                            for item in metadata["formula_driven_geometry_unresolved_examples"]))
        self.assertTrue(any("cached cell values were used" in warning
                            for warning in metadata["fidelity_warnings"]))
        with self.assertRaisesRegex(VsdxFidelityError, "formula-driven geometry"):
            import_vsdx(self.path, strict_fidelity=True)


    def test_mixed_case_page_reference_is_imported_in_strict_mode(self):
        self._convert_to_external_vsdx("PinX", "gUaRd(tHePaGe!pAgEwIdTh*0.5)")
        with ZipFile(self.path) as archive:
            root = ET.fromstring(archive.read("visio/pages/pages.xml"))
        sheet = root.find(f"./{{{V}}}Page/{{{V}}}PageSheet")
        page_width = float(next(cell.get("V") for cell in sheet.findall(f"./{{{V}}}Cell")
                                if cell.get("N") == "PageWidth"))
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertAlmostEqual(imported["nodes"][0]["x"], page_width * 96.0 * 0.5, places=2)
        self.assertEqual(imported["metadata"]["formula_driven_geometry_unresolved_shapes"], 0)

    def test_mixed_case_geometry_cell_name_is_normalized_before_formula_detection(self):
        # ShapeSheet formula lookup is case-insensitive. The public-page importer
        # must not discard the shape before the bounded evaluator sees pinx.
        self._convert_to_external_vsdx(
            "PinX", "gUaRd(tHePaGe!pAgEwIdTh*0.5)", rename_cell_to="pinx")
        with ZipFile(self.path) as archive:
            root = ET.fromstring(archive.read("visio/pages/pages.xml"))
        sheet = root.find(f"./{{{V}}}Page/{{{V}}}PageSheet")
        page_width = float(next(cell.get("V") for cell in sheet.findall(f"./{{{V}}}Cell")
                                if cell.get("N") == "PageWidth"))
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertEqual(len(imported["nodes"]), 1)
        self.assertAlmostEqual(imported["nodes"][0]["x"], page_width * 96.0 * 0.5, places=2)
        metadata = imported["metadata"]
        self.assertEqual(metadata["formula_driven_geometry_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_evaluated_shapes"], 1)
        self.assertEqual(metadata["formula_driven_geometry_unresolved_shapes"], 0)

    def test_mixed_case_cached_cell_reference_is_imported_in_strict_mode(self):
        self._convert_to_external_vsdx("PinX", "gUaRd(wIdTh*0.5)")
        imported = import_vsdx(self.path, strict_fidelity=True)
        self.assertEqual(imported["metadata"]["formula_driven_geometry_evaluated_shapes"], 1)
        self.assertEqual(imported["metadata"]["formula_driven_geometry_unresolved_shapes"], 0)
        self.assertGreater(imported["nodes"][0]["x"], 0)


if __name__ == "__main__":
    unittest.main()
