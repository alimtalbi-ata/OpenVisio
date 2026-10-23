"""V42.79: OPC directory markers are not Visio document parts.

Synthetic ZIP interoperability checks only; no Microsoft Visio desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import export_vsdx, import_vsdx, VsdxExternalChangesError
from openvisio.vsdx_consistency import inspect


class VsdxDirectoryEntriesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "network.vsdx"
        self.document = {"nodes": [{"id": "switch1", "x": 40, "y": 60}], "edges": []}
        export_vsdx(self.path, self.document)

    def _append(self, name, content=b""):
        with ZipFile(self.path, "a", ZIP_DEFLATED) as archive:
            archive.writestr(name, content)

    def test_added_zip_directories_do_not_invalidate_unchanged_diagram(self):
        self._append("visio/")
        self._append("visio/pages/")
        self._append("openvisio/")
        self.assertEqual(inspect(self.path)["status"], "consistent")
        self.assertEqual(import_vsdx(self.path), self.document)

    def test_added_real_opc_part_still_detected(self):
        self._append("visio/masters/")
        self._append("visio/masters/master1.xml", b"<Master />")
        self.assertEqual(inspect(self.path)["changed_parts"], ["visio/masters/master1.xml"])
        with self.assertRaises(VsdxExternalChangesError):
            import_vsdx(self.path)

    def test_directory_traversal_still_rejected(self):
        self._append("../unsafe/")
        with self.assertRaisesRegex(ValueError, "non sûre"):
            import_vsdx(self.path)
        with self.assertRaisesRegex(ValueError, "non sûre"):
            inspect(self.path)


if __name__ == "__main__":
    unittest.main()
