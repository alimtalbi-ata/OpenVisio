"""V42.84: reject encoded XML DTDs before importing external Visio pages.

Synthetic ZIP/XML fixtures only; not a Microsoft Visio interoperability test.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openvisio.vsdx import import_vsdx
from openvisio.vsdx_external import V


class EncodedVsdxDtdTests(unittest.TestCase):
    def _import_page(self, xml, encoding):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'external.vsdx'
            with ZipFile(path, 'w') as archive:
                archive.writestr('visio/pages/page1.xml', xml.encode(encoding))
            return import_vsdx(path)

    def test_utf16_le_internal_entity_must_be_rejected(self):
        xml = (f'<?xml version="1.0" encoding="UTF-16"?>'
               f'<!DOCTYPE PageContents [<!ENTITY fabric "SAN-A">]>'
               f'<PageContents xmlns="{V}"><Shapes>'
               f'<Shape ID="1"><Text>&fabric;</Text></Shape>'
               f'</Shapes></PageContents>')
        with self.assertRaisesRegex(ValueError, 'entités externes'):
            self._import_page(xml, 'utf-16')

    def test_utf16_be_doctype_without_entity_must_be_rejected(self):
        xml = (f'<?xml version="1.0" encoding="UTF-16"?>'
               f'<!DOCTYPE PageContents []>'
               f'<PageContents xmlns="{V}"/>')
        with self.assertRaisesRegex(ValueError, 'entités externes'):
            self._import_page(xml, 'utf-16-be')

    def test_utf16_without_doctype_imports_valid_geometry(self):
        xml = (f'<?xml version="1.0" encoding="UTF-16"?>'
               f'<PageContents xmlns="{V}"><Shapes>'
               f'<Shape ID="1" Name="OpenVisio storage">'
               f'<Cell N="PinX" V="2"/><Cell N="PinY" V="3"/>'
               f'<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
               f'</Shape></Shapes></PageContents>')
        doc = self._import_page(xml, 'utf-16')
        self.assertEqual(len(doc['nodes']), 1)
        self.assertEqual(doc['nodes'][0]['shape'], 'storage')

    def test_malformed_utf16_still_returns_explicit_value_error(self):
        xml = ('<?xml version="1.0" encoding="UTF-16"?>'
               '<PageContents><Shapes></PageContents>')
        with self.assertRaisesRegex(ValueError, 'XML VSDX invalide'):
            self._import_page(xml, 'utf-16')


if __name__ == '__main__':
    unittest.main()
