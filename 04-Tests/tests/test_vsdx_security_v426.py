"""VSDX untrusted input regression tests. Author: Abdelhalim Talbi."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx, export_vsdx

class VsdxSecurityTests(unittest.TestCase):
    def test_embedded_payload_requires_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'unsigned.vsdx'
            with ZipFile(p, 'w', ZIP_DEFLATED) as z:
                z.writestr('openvisio/document.json', b'{"nodes":[],"edges":[]}')
            with self.assertRaisesRegex(ValueError, 'manquant'):
                import_vsdx(p)

    def test_rejects_decompression_bomb(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bomb.vsdx'
            with ZipFile(p, 'w', ZIP_DEFLATED) as z:
                z.writestr('visio/pages/page1.xml', b'A' * 2_000_000)
            with self.assertRaisesRegex(ValueError, 'compression suspecte'):
                import_vsdx(p)

    def test_generated_vsdx_still_imports(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'valid.vsdx'
            doc = {'nodes': [], 'edges': []}
            export_vsdx(p, doc)
            self.assertEqual(import_vsdx(p), doc)
