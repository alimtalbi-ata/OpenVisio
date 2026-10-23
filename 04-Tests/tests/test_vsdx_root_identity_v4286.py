"""V42.86: reject mismatched Visio XML part roots before flattening.

Synthetic OPC fixtures only; no Microsoft Visio desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_external import V, R


class ExternalVsdxRootIdentityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "root-identity.vsdx"
        export_vsdx(self.path, {"nodes": [{"id": "storage-a", "x": 32, "y": 48}], "edges": []})

    def _external_rewrite(self, part, new_root):
        with ZipFile(self.path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()
                     if not name.startswith("openvisio/")}
        root = ET.fromstring(parts[part])
        root.tag = new_root
        parts[part] = ET.tostring(root)
        with ZipFile(self.path, "w", ZIP_DEFLATED) as archive:
            for name, content in parts.items():
                archive.writestr(name, content)

    def test_page_contents_wrong_namespace_must_not_silently_drop_storage(self):
        self._external_rewrite("visio/pages/page1.xml", "{urn:foreign}PageContents")
        with self.assertRaisesRegex(ValueError, "racine XML VSDX"):
            import_vsdx(self.path)

    def test_page_contents_wrong_element_must_not_silently_drop_storage(self):
        self._external_rewrite("visio/pages/page1.xml", f"{{{V}}}Other")
        with self.assertRaisesRegex(ValueError, "racine XML VSDX"):
            import_vsdx(self.path)

    def test_pages_manifest_wrong_root_rejected(self):
        self._external_rewrite("visio/pages/pages.xml", f"{{{V}}}NotPages")
        with self.assertRaisesRegex(ValueError, "racine XML VSDX"):
            import_vsdx(self.path)

    def test_rels_manifest_wrong_root_rejected(self):
        self._external_rewrite("visio/pages/_rels/pages.xml.rels", f"{{{R}}}NotRelationships")
        with self.assertRaisesRegex(ValueError, "racine XML VSDX"):
            import_vsdx(self.path)

    def test_valid_external_page_preserves_storage_node(self):
        self._external_rewrite("visio/pages/page1.xml", f"{{{V}}}PageContents")
        imported = import_vsdx(self.path)
        self.assertEqual(len(imported["nodes"]), 1)
        self.assertEqual(imported["nodes"][0]["id"], "visio-p1-s1")


if __name__ == "__main__":
    unittest.main()
