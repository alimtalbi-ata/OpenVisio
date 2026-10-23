"""V42.72: VSDX manifest schema must be a JSON integer, never bool/float.

A JSON true value compares equal to Python integer 1 and previously bypassed
visual-part checksum verification, silently discarding external Visio edits.
Synthetic OPC package regression only; not a Microsoft Visio qualification.
Author: Abdelhalim Talbi.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openvisio.vsdx import export_vsdx, import_vsdx


class ManifestSchemaTypeTests(unittest.TestCase):
    def _mutate_schema(self, value, *, change_page=False):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        original = Path(temp.name) / 'original.vsdx'
        modified = Path(temp.name) / 'modified.vsdx'
        document = {'nodes': [{'id': 'san-a', 'x': 20, 'y': 30, 'label': 'SAN A'}], 'edges': []}
        export_vsdx(original, document)
        with ZipFile(original) as source, ZipFile(modified, 'w', ZIP_DEFLATED) as target:
            for name in source.namelist():
                content = source.read(name)
                if name == 'openvisio/manifest.json':
                    manifest = json.loads(content)
                    manifest['schema'] = value
                    content = json.dumps(manifest).encode('utf-8')
                elif name == 'visio/pages/page1.xml' and change_page:
                    content = content.replace(b'SAN A', b'SAN B')
                target.writestr(name, content)
        return modified, document

    def test_boolean_schema_cannot_disable_external_edit_detection(self):
        path, _ = self._mutate_schema(True, change_page=True)
        with self.assertRaisesRegex(ValueError, 'Intégrité'):
            import_vsdx(path)

    def test_float_schema_one_is_not_legacy_integer_one(self):
        path, _ = self._mutate_schema(1.0)
        with self.assertRaisesRegex(ValueError, 'Intégrité'):
            import_vsdx(path)

    def test_float_schema_two_is_not_integer_two(self):
        path, _ = self._mutate_schema(2.0)
        with self.assertRaisesRegex(ValueError, 'Intégrité'):
            import_vsdx(path)

    def test_valid_integer_schema_still_roundtrips(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'valid.vsdx'
            document = {'nodes': [], 'edges': []}
            export_vsdx(path, document)
            self.assertEqual(import_vsdx(path), document)
