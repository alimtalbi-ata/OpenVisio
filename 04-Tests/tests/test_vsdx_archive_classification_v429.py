"""Ensure arbitrary ZIPs are not classified as external Visio documents. Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx_consistency import inspect

class ArchiveClassificationTests(unittest.TestCase):
    def test_unrelated_zip_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.vsdx"
            with ZipFile(p, "w") as z:
                z.writestr("readme.txt", "unrelated archive")
            with self.assertRaisesRegex(ValueError, "sans page Visio"):
                inspect(p)

    def test_empty_zip_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "empty.vsdx"
            with ZipFile(p, "w"):
                pass
            with self.assertRaisesRegex(ValueError, "sans page Visio"):
                inspect(p)
