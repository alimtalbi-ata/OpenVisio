"""V42.80: source-free VSDX page references must be unambiguous.

Synthetic OPC tests; not a Microsoft Visio desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_external import V, R, OR


class VsdxPageRelationshipIdentityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'external.vsdx'
        export_vsdx(self.path, {'nodes': [{'id': 'san-a', 'x': 30, 'y': 40}], 'edges': []})

    def _rewrite_external(self, modify):
        with ZipFile(self.path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()
                     if not name.startswith('openvisio/')}
        modify(parts)
        with ZipFile(self.path, 'w', ZIP_DEFLATED) as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)

    def test_duplicate_relationship_id_with_different_target_is_rejected(self):
        def change(parts):
            name = 'visio/pages/_rels/pages.xml.rels'
            root = ET.fromstring(parts[name])
            rel = root.find(f'{{{R}}}Relationship')
            duplicate = dict(rel.attrib)
            duplicate['Target'] = 'page2.xml'
            ET.SubElement(root, f'{{{R}}}Relationship', duplicate)
            parts[name] = ET.tostring(root)
            parts['visio/pages/page2.xml'] = parts['visio/pages/page1.xml']
        self._rewrite_external(change)
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            import_vsdx(self.path)

    def test_duplicate_relationship_id_even_same_target_is_rejected(self):
        def change(parts):
            name = 'visio/pages/_rels/pages.xml.rels'
            root = ET.fromstring(parts[name])
            rel = root.find(f'{{{R}}}Relationship')
            ET.SubElement(root, f'{{{R}}}Relationship', dict(rel.attrib))
            parts[name] = ET.tostring(root)
        self._rewrite_external(change)
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            import_vsdx(self.path)

    def test_duplicate_visio_page_ids_are_rejected(self):
        def change(parts):
            name = 'visio/pages/pages.xml'
            root = ET.fromstring(parts[name])
            first = root.find(f'{{{V}}}Page')
            second = ET.fromstring(ET.tostring(first))
            second.set('Name', 'Second page')
            root.append(second)
            parts[name] = ET.tostring(root)
        self._rewrite_external(change)
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            import_vsdx(self.path)

    def test_two_distinct_page_relationships_still_import(self):
        def change(parts):
            page_name = 'visio/pages/pages.xml'
            pages = ET.fromstring(parts[page_name])
            first = pages.find(f'{{{V}}}Page')
            second = ET.fromstring(ET.tostring(first))
            second.set('ID', '2')
            second.set('Name', 'SAN page 2')
            second.find(f'{{{V}}}Rel').set(f'{{{OR}}}id', 'rId2')
            pages.append(second)
            parts[page_name] = ET.tostring(pages)
            rel_name = 'visio/pages/_rels/pages.xml.rels'
            relations = ET.fromstring(parts[rel_name])
            first_rel = relations.find(f'{{{R}}}Relationship')
            second_rel = dict(first_rel.attrib)
            second_rel.update({'Id': 'rId2', 'Target': 'page2.xml'})
            ET.SubElement(relations, f'{{{R}}}Relationship', second_rel)
            parts[rel_name] = ET.tostring(relations)
            parts['visio/pages/page2.xml'] = parts['visio/pages/page1.xml']
        self._rewrite_external(change)
        imported = import_vsdx(self.path)
        self.assertEqual(imported['metadata']['page_count'], 2)
        self.assertEqual(len(imported['layers']), 2)
        self.assertEqual(len(imported['nodes']), 2)
        self.assertNotEqual(imported['nodes'][0]['layer'], imported['nodes'][1]['layer'])


if __name__ == '__main__':
    unittest.main()
