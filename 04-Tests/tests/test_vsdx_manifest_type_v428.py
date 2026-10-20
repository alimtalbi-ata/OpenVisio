"""Reject malformed VSDX metadata without unexpected exceptions. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx

class VsdxManifestTypeTests(unittest.TestCase):
    def test_non_object_manifests_rejected_as_value_error(self):
        for manifest in ('[]', 'null', '42', '"invalid"'):
            with self.subTest(manifest=manifest), tempfile.TemporaryDirectory() as d:
                p = Path(d) / 'bad.vsdx'
                with ZipFile(p, 'w', ZIP_DEFLATED) as z:
                    z.writestr('openvisio/document.json', '{"nodes":[],"edges":[]}')
                    z.writestr('openvisio/manifest.json', manifest)
                with self.assertRaisesRegex(ValueError, 'Manifeste OpenVisio/VSDX invalide'):
                    import_vsdx(p)
