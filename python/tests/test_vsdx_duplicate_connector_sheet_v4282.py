"""V42.82 synthetic SAN topology: connector sheet IDs must be unique.

Fixtures are synthetic OOXML, not Microsoft Visio interoperability evidence.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile

from openvisio.vsdx_external import V, import_external_pages


def imported(connector_ids):
    nodes = ''.join(
        f'<Shape ID="{sid}" Name="OpenVisio storage">'
        f'<Cell N="PinX" V="{sid}"/><Cell N="PinY" V="2"/>'
        '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
        '</Shape>' for sid in (1, 2)
    )
    connectors = ''.join(
        f'<Shape ID="{sid}" Name="SAN Link">'
        f'<Cell N="OneD" V="1"/><Text>Fabric {index}</Text></Shape>'
        for index, sid in enumerate(connector_ids, 1)
    )
    links = ''.join(
        f'<Connect FromSheet="{sid}" FromCell="{end}" ToSheet="{target}"/>'
        for sid in set(connector_ids)
        for end, target in (("BeginX", 1), ("EndX", 2))
    )
    xml = (f'<PageContents xmlns="{V}"><Shapes>{nodes}{connectors}</Shapes>'
           f'<Connects>{links}</Connects></PageContents>')
    data = io.BytesIO()
    with ZipFile(data, 'w') as archive:
        archive.writestr('visio/pages/page1.xml', xml)
    with ZipFile(io.BytesIO(data.getvalue())) as archive:
        return import_external_pages(archive)


class DuplicateConnectorSheetTests(unittest.TestCase):
    def test_duplicate_connector_sheet_must_not_collapse_parallel_san_links(self):
        with self.assertRaisesRegex(ValueError, 'connecteur.*dupliqu'):
            imported((101, 101))

    def test_three_duplicate_connector_sheets_must_be_rejected(self):
        with self.assertRaisesRegex(ValueError, 'connecteur.*dupliqu'):
            imported((101, 101, 101))

    def test_distinct_parallel_connector_sheets_remain_separate(self):
        doc = imported((101, 102))
        self.assertEqual(len(doc['edges']), 2)
        self.assertEqual({edge['visio_connector_sheet_id'] for edge in doc['edges']},
                         {'101', '102'})
        self.assertEqual({edge['label'] for edge in doc['edges']},
                         {'Fabric 1', 'Fabric 2'})


if __name__ == '__main__':
    unittest.main()
