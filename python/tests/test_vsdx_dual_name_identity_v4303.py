"""V43.03: classify external stencil devices using Name and NameU without guessing from text.

Synthetic VSDX OPC pages only; not Microsoft Visio Desktop fidelity evidence.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from openvisio.vsdx import import_vsdx
from openvisio.vsdx_external import V


class DualNameSanIdentityTests(unittest.TestCase):
    def import_shape(self, *, nameu, name, text=None):
        attributes = f'NameU="{escape(nameu)}" Name="{escape(name)}"'
        caption = f'<Text>{escape(text)}</Text>' if text is not None else ''
        page = (f'<PageContents xmlns="{V}"><Shapes>'
                f'<Shape ID="1" {attributes}>'
                '<Cell N="PinX" V="2"/><Cell N="PinY" V="4"/>'
                f'{caption}</Shape></Shapes></PageContents>')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
                archive.writestr('visio/pages/page1.xml', page)
            return import_vsdx(path)['nodes'][0]

    def test_vendor_name_is_used_when_nameu_is_generic_sheet_id(self):
        node = self.import_shape(nameu='Sheet.42', name='Brocade G720')
        self.assertEqual(node['shape'], 'san-switch')
        self.assertEqual(node['label'], 'Brocade G720')

    def test_vendor_name_does_not_override_explicit_caption(self):
        node = self.import_shape(nameu='Sheet.42', name='Cisco MDS 9710', text='Fabric B core')
        self.assertEqual(node['shape'], 'san-switch')
        self.assertEqual(node['label'], 'Fabric B core')

    def test_nameu_vendor_identity_remains_supported(self):
        node = self.import_shape(nameu='Cisco MDS 9710', name='Sheet.42')
        self.assertEqual(node['shape'], 'san-switch')

    def test_unrelated_vendor_name_does_not_turn_server_into_san_switch(self):
        node = self.import_shape(nameu='Sheet.42', name='Brocade Management Server')
        self.assertEqual(node['shape'], 'server')


if __name__ == '__main__':
    unittest.main()
