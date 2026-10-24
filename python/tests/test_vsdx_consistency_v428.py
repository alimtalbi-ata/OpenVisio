"""Standalone VSDX consistency checker, no Tk dependency. Abdelhalim Talbi."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx_consistency import build_manifest, changed_visual_parts, inspect, main


class VsdxConsistencyCheckerTests(unittest.TestCase):
    def test_schema3_manifest_roundtrip(self):
        parts = {
            'visio/pages/pages.xml': b'<Pages/>',
            'visio/pages/_rels/pages.xml.rels': b'<Relationships/>',
            'visio/pages/page1.xml': b'<PageContents/>',
        }
        payload = b'{"nodes":[],"edges":[]}'
        manifest = build_manifest(parts, payload)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'test.vsdx'
            with ZipFile(p, 'w', ZIP_DEFLATED) as z:
                for name, data in parts.items():
                    z.writestr(name, data)
                z.writestr('openvisio/document.json', payload)
                z.writestr('openvisio/manifest.json', json.dumps(manifest))
            self.assertEqual(inspect(p)['status'], 'consistent')
            with ZipFile(p) as z:
                self.assertEqual(changed_visual_parts(z, manifest), [])

    def test_legacy_is_explicitly_unverifiable(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'old.vsdx'
            payload = b'{}'
            with ZipFile(p, 'w') as z:
                z.writestr('openvisio/document.json', payload)
                z.writestr('openvisio/manifest.json', json.dumps({
                    'schema': 1, 'sha256': hashlib.sha256(payload).hexdigest()}))
            self.assertEqual(inspect(p)['visual_consistency'], 'unverifiable')

    def test_external_vsdx_reported_without_claim_of_fidelity(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'external.vsdx'
            with ZipFile(p, 'w') as z:
                z.writestr('visio/pages/page1.xml', '<PageContents xmlns="http://schemas.microsoft.com/office/visio/2011/1/core"/>')
            self.assertEqual(inspect(p)['status'], 'external')
            self.assertEqual(inspect(p)['page_count'], 1)

    def test_corrupted_payload_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.vsdx'
            with ZipFile(p, 'w') as z:
                z.writestr('openvisio/document.json', b'{}')
                z.writestr('openvisio/manifest.json', json.dumps({'schema': 1, 'sha256': '0' * 64}))
            self.assertEqual(inspect(p)['status'], 'corrupted_payload')


if __name__ == '__main__':
    unittest.main()

class VsdxConsistencyHardeningTests(unittest.TestCase):
    def test_invalid_manifest_json_type_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad-manifest.vsdx'
            with ZipFile(p, 'w') as z:
                z.writestr('openvisio/document.json', b'{}')
                z.writestr('openvisio/manifest.json', b'[]')
            with self.assertRaisesRegex(ValueError, 'Manifeste VSDX invalide'):
                inspect(p)

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad-path.vsdx'
            with ZipFile(p, 'w') as z:
                z.writestr('../unexpected.xml', b'<xml/>')
            with self.assertRaisesRegex(ValueError, 'non sûre'):
                inspect(p)
