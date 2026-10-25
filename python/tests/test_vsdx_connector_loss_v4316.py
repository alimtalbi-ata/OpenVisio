"""V43.16: incomplete public Visio SAN connections are never silently lost.

Only synthetic OPC fixtures; Microsoft Visio Desktop fidelity is NOT certified.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile
from openvisio.vsdx_external import V, import_external_pages


def fixture(rows, *, missing_source=False):
    nodes = ''.join(
        f'<Shape ID="{sid}" Name="OpenVisio san-switch">'
        f'<Cell N="PinX" V="{sid}"/><Cell N="PinY" V="2"/>'
        '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
        '</Shape>' for sid in (1, 2)
    )
    # Sheet 9 exists in Visio but its unsupported geometry prevents node import.
    unsupported = ('<Shape ID="9" Name="Unsupported">'
                   '<Cell N="PinX" V="invalid"/><Cell N="PinY" V="2"/>'
                   '</Shape>')
    connectors = ''.join(
        f'<Shape ID="{sid}" Name="FC Link"><Cell N="OneD" V="1"/>'
        f'<Text>Fabric {sid}</Text></Shape>' for sid in (101, 102, 103, 104)
    )
    xml_rows = ''.join(
        f'<Connect FromSheet="{sid}" FromCell="{end}" ToSheet="{target}" ToCell="PinX"/>'
        for sid, end, target in rows
    )
    if missing_source:
        xml_rows += '<Connect FromSheet="999" FromCell="BeginX" ToSheet="9" ToCell="PinX"/>'
    xml = (f'<PageContents xmlns="{V}"><Shapes>{nodes}{unsupported}{connectors}</Shapes>'
           f'<Connects>{xml_rows}</Connects></PageContents>')
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w') as archive:
        archive.writestr('visio/pages/page1.xml', xml)
    with ZipFile(io.BytesIO(buffer.getvalue())) as archive:
        return import_external_pages(archive)


class PublicVsdxConnectorLossAccounting(unittest.TestCase):
    def test_half_connected_fabric_link_has_explicit_warning(self):
        doc = fixture([(101, 'BeginY', 1)])
        self.assertEqual(doc['edges'], [])
        self.assertEqual(doc['metadata']['connector_links_skipped'], 1)
        self.assertEqual(doc['metadata']['connector_links_skipped_by_reason']['incomplete'], 1)
        self.assertIn('sheet 101', doc['metadata']['connector_links_skipped_examples'][0])
        self.assertIn('connector(s) omitted', doc['metadata']['fidelity_warnings'][0])

    def test_self_connected_fabric_link_has_explicit_warning(self):
        doc = fixture([(102, 'BeginX', 2), (102, 'EndY', 2)])
        self.assertEqual(doc['edges'], [])
        self.assertEqual(doc['metadata']['connector_links_skipped_by_reason']['self_loop'], 1)

    def test_unsupported_existing_endpoints_are_reported(self):
        doc = fixture([(103, 'BeginX', 9), (103, 'EndX', 9)])
        self.assertEqual(doc['metadata']['connector_links_skipped_by_reason']['unresolved'], 1)
        self.assertIn('unsupported endpoints', doc['metadata']['fidelity_warnings'][0])

    def test_valid_parallel_fabric_paths_remain_distinct(self):
        doc = fixture([(101, 'BeginY', 1), (101, 'EndX', 2),
                       (102, 'BeginX', 1), (102, 'EndY', 2)])
        self.assertEqual(len(doc['edges']), 2)
        self.assertEqual([e['label'] for e in doc['edges']], ['Fabric 101', 'Fabric 102'])
        self.assertEqual(doc['metadata']['connector_links_skipped'], 0)
        self.assertNotIn('fidelity_warnings', doc['metadata'])

    def test_partial_path_does_not_hide_a_valid_path(self):
        doc = fixture([(101, 'BeginX', 1), (101, 'EndX', 2), (104, 'BeginY', 1)])
        self.assertEqual(len(doc['edges']), 1)
        self.assertEqual(doc['metadata']['connector_links_skipped'], 1)
        self.assertIn('sheet 104', doc['metadata']['connector_links_skipped_examples'][0])

    def test_missing_connector_source_even_with_unsupported_target_rejected(self):
        with self.assertRaisesRegex(ValueError, 'feuille de connecteur absente'):
            fixture([], missing_source=True)


if __name__ == '__main__':
    unittest.main()
