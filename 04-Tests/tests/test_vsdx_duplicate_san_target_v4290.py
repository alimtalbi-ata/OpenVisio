"""V42.90: duplicate Visio endpoint sheet IDs cannot silently miswire SAN fabric.

Fixtures are synthetic OPC/VSDX; they do not establish Microsoft Visio desktop fidelity.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile
from openvisio.vsdx_external import V, import_external_pages


def imported(*, duplicate_target=False, duplicate_unused=False, parallel=False):
    nodes = [
        '<Shape ID="1" Name="OpenVisio storage"><Cell N="PinX" V="1"/><Cell N="PinY" V="2"/></Shape>',
        '<Shape ID="2" Name="OpenVisio storage"><Cell N="PinX" V="3"/><Cell N="PinY" V="2"/></Shape>',
    ]
    if duplicate_target:
        nodes.append('<Shape ID="2" Name="OpenVisio SAN Switch"><Cell N="PinX" V="7"/><Cell N="PinY" V="2"/></Shape>')
    if duplicate_unused:
        nodes.extend(['<Shape ID="8" Name="Decorative"><Cell N="PinX" V="4"/><Cell N="PinY" V="4"/></Shape>'] * 2)
    nodes.append('<Shape ID="101"><Cell N="OneD" V="1"/><Text>Fabric A</Text></Shape>')
    rows = ['<Connect FromSheet="101" FromCell="BeginX" ToSheet="1"/>',
            '<Connect FromSheet="101" FromCell="EndX" ToSheet="2"/>']
    if parallel:
        nodes.append('<Shape ID="102"><Cell N="OneD" V="1"/><Text>Fabric B</Text></Shape>')
        rows += ['<Connect FromSheet="102" FromCell="BeginX" ToSheet="1"/>',
                 '<Connect FromSheet="102" FromCell="EndX" ToSheet="2"/>']
    xml = (f'<PageContents xmlns="{V}"><Shapes>{"".join(nodes)}</Shapes>'
           f'<Connects>{"".join(rows)}</Connects></PageContents>')
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w') as archive:
        archive.writestr('visio/pages/page1.xml', xml)
    with ZipFile(io.BytesIO(buffer.getvalue())) as archive:
        return import_external_pages(archive)


class DuplicateSanEndpointIdentityTests(unittest.TestCase):
    def test_duplicate_referenced_endpoint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'équipement VSDX dupliqué'):
            imported(duplicate_target=True)

    def test_duplicate_unused_decorative_shape_keeps_legacy_compatibility(self):
        document = imported(duplicate_unused=True)
        self.assertEqual(len(document['edges']), 1)
        self.assertEqual(document['edges'][0]['to'], 'visio-p1-s2')

    def test_distinct_parallel_fabric_links_keep_identity_and_labels(self):
        document = imported(parallel=True)
        self.assertEqual(len(document['edges']), 2)
        self.assertEqual({edge['visio_connector_sheet_id'] for edge in document['edges']}, {'101', '102'})
        self.assertEqual({edge['label'] for edge in document['edges']}, {'Fabric A', 'Fabric B'})


if __name__ == '__main__':
    unittest.main()
