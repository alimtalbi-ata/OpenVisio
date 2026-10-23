"""V42.63: external VSDX must never silently miswire ambiguous SAN links.

The fixtures are synthetic OOXML, not evidence of Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile

from openvisio.vsdx_external import import_external_pages

V = "http://schemas.microsoft.com/office/visio/2011/1/core"


def imported(connect_rows, *, second_connector=False):
    nodes = ''.join(
        f'<Shape ID="{sid}" Name="OpenVisio storage">'
        f'<Cell N="PinX" V="{sid}"/><Cell N="PinY" V="2"/>'
        '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
        '</Shape>' for sid in (1, 2, 3)
    )
    connector = ('<Shape ID="101" Name="SAN Link">'
                 '<Cell N="OneD" V="1"/><Text>SAN Fabric A</Text></Shape>')
    if second_connector:
        connector += ('<Shape ID="102" Name="SAN Link">'
                      '<Cell N="OneD" V="1"/><Text>SAN Fabric B</Text></Shape>')
    links = ''.join(
        f'<Connect FromSheet="101" FromCell="{end}" ToSheet="{sid}" ToCell="PinX"/>'
        for end, sid in connect_rows
    )
    if second_connector:
        links += ('<Connect FromSheet="102" FromCell="BeginX" ToSheet="1" ToCell="PinX"/>'
                  '<Connect FromSheet="102" FromCell="EndX" ToSheet="2" ToCell="PinX"/>')
    page = (f'<PageContents xmlns="{V}"><Shapes>' + nodes + connector
            + '</Shapes><Connects>' + links + '</Connects></PageContents>')
    stream = io.BytesIO()
    with ZipFile(stream, 'w') as archive:
        archive.writestr('visio/pages/page1.xml', page)
    with ZipFile(io.BytesIO(stream.getvalue())) as archive:
        return import_external_pages(archive)


class AmbiguousSanTopologyTests(unittest.TestCase):
    def test_conflicting_connector_endpoint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ambiguë'):
            imported([('BeginX', 1), ('EndX', 2), ('BeginX', 3)])

    def test_reordering_conflict_does_not_change_rejection(self):
        with self.assertRaisesRegex(ValueError, 'ambiguë'):
            imported([('BeginX', 3), ('BeginX', 1), ('EndX', 2)])

    def test_identical_duplicate_rows_are_accepted(self):
        diagram = imported([('BeginX', 1), ('EndX', 2), ('BeginX', 1), ('EndX', 2)])
        self.assertEqual(len(diagram['edges']), 1)
        self.assertEqual(diagram['edges'][0]['from'], 'visio-p1-s1')
        self.assertEqual(diagram['edges'][0]['to'], 'visio-p1-s2')
        self.assertEqual(diagram['edges'][0]['label'], 'SAN Fabric A')

    def test_parallel_distinct_connectors_remain_supported(self):
        diagram = imported([('BeginX', 1), ('EndX', 2)], second_connector=True)
        self.assertEqual(len(diagram['edges']), 2)
        self.assertEqual({edge['visio_connector_sheet_id'] for edge in diagram['edges']},
                         {'101', '102'})
        self.assertEqual({edge['label'] for edge in diagram['edges']},
                         {'SAN Fabric A', 'SAN Fabric B'})


if __name__ == '__main__':
    unittest.main()
