"""V42.64: reject phantom SAN connections from invalid connector sheets.

Fixtures are synthetic OOXML; this is not a Microsoft Visio fidelity test.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile

from openvisio.vsdx_external import import_external_pages

V = "http://schemas.microsoft.com/office/visio/2011/1/core"


def _import(source, *, include_connector=True):
    nodes = ''.join(
        f'<Shape ID="{sid}" Name="OpenVisio storage">'
        f'<Cell N="PinX" V="{sid}"/><Cell N="PinY" V="2"/>'
        '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
        '</Shape>' for sid in (1, 2)
    )
    connector = ('<Shape ID="101" Name="SAN Link">'
                 '<Cell N="OneD" V="1"/></Shape>') if include_connector else ''
    links = ''.join(
        f'<Connect FromSheet="{source}" FromCell="{end}" ToSheet="{target}"/>'
        for end, target in (("BeginX", 1), ("EndX", 2))
    )
    xml = (f'<PageContents xmlns="{V}"><Shapes>' + nodes + connector
           + '</Shapes><Connects>' + links + '</Connects></PageContents>')
    data = io.BytesIO()
    with ZipFile(data, 'w') as archive:
        archive.writestr('visio/pages/page1.xml', xml)
    with ZipFile(io.BytesIO(data.getvalue())) as archive:
        return import_external_pages(archive)


class ConnectorSourceIntegrityTests(unittest.TestCase):
    def test_node_sheet_cannot_masquerade_as_san_connector(self):
        with self.assertRaisesRegex(ValueError, 'connecteur'):
            _import('1')

    def test_missing_connector_sheet_rejected(self):
        with self.assertRaisesRegex(ValueError, 'connecteur'):
            _import('999', include_connector=False)

    def test_valid_connector_still_imported(self):
        doc = _import('101')
        self.assertEqual(len(doc['edges']), 1)
        self.assertEqual(doc['edges'][0]['visio_connector_sheet_id'], '101')


if __name__ == '__main__':
    unittest.main()
