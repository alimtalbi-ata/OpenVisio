"""V42.83: orphaned SAN connector endpoints must not disappear silently.

Synthetic VSDX OPC fixtures, not Microsoft Visio fidelity evidence.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile

from openvisio.vsdx_external import V, import_external_pages


def imported(*, start="1", end="2", add_unused=False):
    nodes = ''.join(
        f'<Shape ID="{sid}" Name="OpenVisio storage">'
        f'<Cell N="PinX" V="{sid}"/><Cell N="PinY" V="2"/>'
        '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
        '</Shape>' for sid in (1, 2)
    )
    extra = ('<Shape ID="900" Name="SAN Link">'
             '<Cell N="OneD" V="1"/></Shape>') if add_unused else ''
    connector = ('<Shape ID="101" Name="SAN Link">'
                 '<Cell N="OneD" V="1"/><Text>Fabric A</Text></Shape>')
    rows = (f'<Connect FromSheet="101" FromCell="BeginX" ToSheet="{start}" ToCell="PinX"/>'
            f'<Connect FromSheet="101" FromCell="EndX" ToSheet="{end}" ToCell="PinX"/>')
    xml = (f'<PageContents xmlns="{V}"><Shapes>{nodes}{connector}{extra}</Shapes>'
           f'<Connects>{rows}</Connects></PageContents>')
    data = io.BytesIO()
    with ZipFile(data, 'w') as z:
        z.writestr('visio/pages/page1.xml', xml)
    with ZipFile(io.BytesIO(data.getvalue())) as z:
        return import_external_pages(z)


class OrphanedSanEndpointTests(unittest.TestCase):
    def test_missing_begin_endpoint_rejected(self):
        with self.assertRaisesRegex(ValueError, 'extrémité.*absente'):
            imported(start='999')

    def test_missing_end_endpoint_rejected(self):
        with self.assertRaisesRegex(ValueError, 'extrémité.*absente'):
            imported(end='999')

    def test_valid_endpoints_keep_label_and_identity(self):
        doc = imported(add_unused=True)
        self.assertEqual(len(doc['edges']), 1)
        self.assertEqual(doc['edges'][0]['label'], 'Fabric A')
        self.assertEqual(doc['edges'][0]['visio_connector_sheet_id'], '101')
        self.assertEqual((doc['edges'][0]['from'], doc['edges'][0]['to']),
                         ('visio-p1-s1', 'visio-p1-s2'))


if __name__ == '__main__':
    unittest.main()
