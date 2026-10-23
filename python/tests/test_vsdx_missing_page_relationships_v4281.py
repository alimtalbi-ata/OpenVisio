"""V42.81: never guess page identity when OPC relationship is declared but absent.

All fixtures are synthetic and are NOT Microsoft Visio interoperability evidence.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_external import V, R, OR


class MissingPageRelationshipTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'external.vsdx'
        export_vsdx(self.path, {'nodes': [{'id': 'san-a', 'x': 30, 'y': 40}], 'edges': []})

    def rewrite(self, transform):
        with ZipFile(self.path) as source:
            parts = {name: source.read(name) for name in source.namelist()
                     if not name.startswith('openvisio/')}
        transform(parts)
        with ZipFile(self.path, 'w', ZIP_DEFLATED) as target:
            for name, payload in parts.items():
                target.writestr(name, payload)

    def test_missing_rels_must_not_guess_page1(self):
        self.rewrite(lambda parts: parts.pop('visio/pages/_rels/pages.xml.rels'))
        with self.assertRaisesRegex(ValueError, 'Relation de page'):
            import_vsdx(self.path)

    def test_empty_rels_must_not_guess_page1(self):
        def transform(parts):
            parts['visio/pages/_rels/pages.xml.rels'] = (
                f'<Relationships xmlns="{R}"/>'.encode())
        self.rewrite(transform)
        with self.assertRaisesRegex(ValueError, 'Relation de page'):
            import_vsdx(self.path)

    def test_external_relation_must_not_guess_page1(self):
        def transform(parts):
            name = 'visio/pages/_rels/pages.xml.rels'
            root = ET.fromstring(parts[name])
            root.find(f'{{{R}}}Relationship').set('TargetMode', 'External')
            parts[name] = ET.tostring(root)
        self.rewrite(transform)
        with self.assertRaisesRegex(ValueError, 'Relation de page'):
            import_vsdx(self.path)

    def test_legacy_page_without_declared_rel_may_use_page1(self):
        def transform(parts):
            pages_name = 'visio/pages/pages.xml'
            root = ET.fromstring(parts[pages_name])
            page = root.find(f'{{{V}}}Page')
            page.remove(page.find(f'{{{V}}}Rel'))
            parts[pages_name] = ET.tostring(root)
            parts.pop('visio/pages/_rels/pages.xml.rels')
        self.rewrite(transform)
        imported = import_vsdx(self.path)
        self.assertEqual(len(imported['nodes']), 1)
        self.assertEqual(imported['metadata']['page_count'], 1)


if __name__ == '__main__':
    unittest.main()
