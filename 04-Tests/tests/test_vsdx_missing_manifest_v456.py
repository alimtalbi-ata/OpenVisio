"""A VSDX containing an embedded document without its manifest is invalid."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx import import_vsdx

class MissingVsdxManifestTests(unittest.TestCase):
    def test_missing_manifest_reports_value_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing-manifest.vsdx"
            with ZipFile(path, "w") as archive:
                archive.writestr("openvisio/document.json", '{"nodes":[],"edges":[]}')
            with self.assertRaisesRegex(ValueError, "Manifeste.*manquant"):
                import_vsdx(path)
