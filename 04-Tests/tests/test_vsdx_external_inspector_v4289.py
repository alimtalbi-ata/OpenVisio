"""External VSDX inspector must not certify packages its importer rejects.

Fixtures are synthetic OPC/XML, not Microsoft Visio-generated evidence.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx_consistency import inspect
from openvisio.vsdx import import_vsdx

V = 'http://schemas.microsoft.com/office/visio/2011/1/core'
R = 'http://schemas.openxmlformats.org/package/2006/relationships'
OR = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


class ExternalInspectorParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'external.vsdx'

    def make_package(self, *, page_root='PageContents', pages=True, rels=True,
                     page_payload=None):
        parts = {}
        if pages:
            parts['visio/pages/pages.xml'] = (
                f'<Pages xmlns="{V}" xmlns:r="{OR}">'
                '<Page ID="1" Name="Fabric A"><Rel r:id="rId1"/></Page>'
                '</Pages>').encode('utf-8')
        if rels:
            parts['visio/pages/_rels/pages.xml.rels'] = (
                f'<Relationships xmlns="{R}">'
                '<Relationship Id="rId1" Target="page1.xml"/>'
                '</Relationships>').encode('utf-8')
        if page_root is not None:
            parts['visio/pages/page1.xml'] = (page_payload if page_payload is not None else
                f'<{page_root} xmlns="{V}"/>'.encode('utf-8'))
        with ZipFile(self.path, 'w', ZIP_DEFLATED) as z:
            for name, data in parts.items():
                z.writestr(name, data)

    def test_valid_external_page_remains_inspectable(self):
        self.make_package()
        result = inspect(self.path)
        self.assertEqual(result['status'], 'external')
        self.assertEqual(result['page_count'], 1)
        self.assertEqual(result['fidelity_warnings'], [])
        self.assertEqual(import_vsdx(self.path)['metadata']['page_count'], 1)

    def test_empty_zip_cannot_report_valid_external(self):
        self.make_package(page_root=None, pages=False, rels=False)
        with self.assertRaisesRegex(ValueError, 'Page Visio absente'):
            inspect(self.path)

    def test_wrong_page_xml_root_cannot_report_valid_external(self):
        self.make_package(page_root='Pages')
        with self.assertRaisesRegex(ValueError, 'racine XML VSDX invalide'):
            inspect(self.path)

    def test_missing_opc_page_relation_cannot_report_valid_external(self):
        self.make_package(rels=False)
        with self.assertRaisesRegex(ValueError, 'Relation de page VSDX'):
            inspect(self.path)

    def test_external_xml_dtd_is_rejected_before_inspection(self):
        self.make_package(page_payload=(
            f'<!DOCTYPE PageContents [<!ENTITY x "unsafe">]>'
            f'<PageContents xmlns="{V}"><Text>&x;</Text></PageContents>'
        ).encode('utf-8'))
        with self.assertRaisesRegex(ValueError, 'entités externes interdit'):
            inspect(self.path)


if __name__ == '__main__':
    unittest.main()
