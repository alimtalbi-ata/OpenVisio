"""Reject ambiguous half-embedded VSDX packages. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx
from openvisio.vsdx_consistency import inspect

class PartialEmbeddedTests(unittest.TestCase):
    def test_manifest_without_document_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"manifest-only.vsdx"
            with ZipFile(p,"w",ZIP_DEFLATED) as z:
                z.writestr("openvisio/manifest.json", "{}")
            with self.assertRaisesRegex(ValueError,"manquant"):
                import_vsdx(p)
            with self.assertRaisesRegex(ValueError,"incomplet"):
                inspect(p)

    def test_document_without_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"document-only.vsdx"
            with ZipFile(p,"w",ZIP_DEFLATED) as z:
                z.writestr("openvisio/document.json", "{}")
            with self.assertRaisesRegex(ValueError,"manquant"):
                import_vsdx(p)
            with self.assertRaisesRegex(ValueError,"incomplet"):
                inspect(p)
