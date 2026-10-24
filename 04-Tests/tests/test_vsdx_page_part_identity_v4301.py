"""V43.01: duplicate VSDX OPC page-part references are rejected.

Synthetic regression, not Microsoft Visio desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_external import V, R, OR
from openvisio.vsdx_consistency import inspect


class PagePartIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "san-pages.vsdx"
        export_vsdx(self.path, {"nodes": [
            {"id": "san-a", "shape": "san-switch", "x": 120, "y": 150}], "edges": []})

    def make_two_pages(self, second_target):
        with ZipFile(self.path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()
                     if not name.startswith("openvisio/")}
        pages = ET.fromstring(parts["visio/pages/pages.xml"])
        first = pages.find(f"{{{V}}}Page")
        second = ET.fromstring(ET.tostring(first))
        second.set("ID", "2")
        second.set("Name", "Fabric B")
        second.find(f"{{{V}}}Rel").set(f"{{{OR}}}id", "rId2")
        pages.append(second)
        parts["visio/pages/pages.xml"] = ET.tostring(pages)
        rels = ET.fromstring(parts["visio/pages/_rels/pages.xml.rels"])
        first_rel = rels.find(f"{{{R}}}Relationship")
        new_rel = dict(first_rel.attrib)
        new_rel.update({"Id": "rId2", "Target": second_target})
        ET.SubElement(rels, f"{{{R}}}Relationship", new_rel)
        parts["visio/pages/_rels/pages.xml.rels"] = ET.tostring(rels)
        parts["visio/pages/page2.xml"] = parts["visio/pages/page1.xml"]
        with ZipFile(self.path, "w", ZIP_DEFLATED) as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)

    def test_duplicate_target_rejected_by_import(self):
        self.make_two_pages("page1.xml")
        with self.assertRaisesRegex(ValueError, "réutilisée"):
            import_vsdx(self.path)

    def test_duplicate_target_rejected_by_inspector(self):
        self.make_two_pages("page1.xml")
        with self.assertRaisesRegex(ValueError, "réutilisée"):
            inspect(self.path)

    def test_distinct_targets_preserve_two_layers(self):
        self.make_two_pages("page2.xml")
        result = import_vsdx(self.path)
        self.assertEqual(result["metadata"]["page_count"], 2)
        self.assertEqual(len(result["layers"]), 2)
        self.assertEqual(len(result["nodes"]), 2)


if __name__ == "__main__":
    unittest.main()
