"""VSDX import must reject oversized embedded content before parsing it."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from openvisio.vsdx import import_vsdx

class VsdxEmbeddedSizeTests(unittest.TestCase):
    def _assert_rejected(self, oversized_part, size):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.vsdx"
            with ZipFile(path, "w", ZIP_STORED) as archive:
                archive.writestr("openvisio/document.json", b"{}" if oversized_part != "openvisio/document.json" else b" " * size)
                archive.writestr("openvisio/manifest.json", b"{}" if oversized_part != "openvisio/manifest.json" else b" " * size)
            with self.assertRaisesRegex(ValueError, "trop volumineux|non sûre"):
                import_vsdx(path)

    def test_reject_large_embedded_document(self):
        self._assert_rejected("openvisio/document.json", 10_000_001)

    def test_reject_large_embedded_manifest(self):
        self._assert_rejected("openvisio/manifest.json", 1_000_001)
