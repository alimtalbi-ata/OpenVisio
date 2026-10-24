"""V43.02: external Visio vendor-labelled FC switches retain SAN identity.

Synthetic OPC fixtures, not Microsoft Visio Desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openvisio.vsdx import import_vsdx
from openvisio.vsdx_external import _kind, V


class VendorSanIdentityTests(unittest.TestCase):
    def test_known_fc_switch_product_names(self):
        names = (
            'Cisco MDS 9710', 'MDS-9148T', 'Brocade G720',
            'Brocade DCX 8510', 'Dell Connectrix DS-6620B',
            'HPE SN6600B', 'IBM SAN768B-2',
        )
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(_kind(name), 'san-switch')

    def test_lan_and_unrelated_vendor_names_unchanged(self):
        for name, expected in (
            ('Cisco Nexus 93180YC', 'server'),
            ('Brocade Management Server', 'server'),
            ('San Francisco Switch', 'network-switch'),
            ('Cisco MDS Backup Server', 'server'),
            ('Dell DS-6620B Storage', 'storage'),
        ):
            with self.subTest(name=name):
                self.assertEqual(_kind(name), expected)

    def test_external_vsdx_page_maps_mds_to_san_switch(self):
        page = f'''<PageContents xmlns="{V}"><Shapes>
          <Shape ID="1" NameU="Cisco MDS 9710">
            <Cell N="PinX" V="2"/><Cell N="PinY" V="4"/>
          </Shape>
        </Shapes></PageContents>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'mds.vsdx'
            with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
                archive.writestr('visio/pages/page1.xml', page)
            document = import_vsdx(path)
        self.assertEqual(len(document['nodes']), 1)
        self.assertEqual(document['nodes'][0]['shape'], 'san-switch')


if __name__ == '__main__':
    unittest.main()
