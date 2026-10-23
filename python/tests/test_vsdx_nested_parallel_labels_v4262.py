"""Public VSDX regression: captions on grouped parallel SAN connector sheets.

Synthetic OOXML fixture, not a Microsoft Visio interoperability certification.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile
from openvisio.vsdx_external import import_external_pages

V = "http://schemas.microsoft.com/office/visio/2011/1/core"


class NestedParallelLabelsTests(unittest.TestCase):
    def test_nested_connector_captions_survive_flattened_import(self):
        def node(sheet, x):
            return (f'<Shape ID="{sheet}" Name="OpenVisio storage">'
                    f'<Cell N="PinX" V="{x}"/><Cell N="PinY" V="2"/>'
                    '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
                    '</Shape>')
        def connector(sheet, label):
            return (f'<Shape ID="{sheet}" Name="SAN Link">'
                    '<Cell N="OneD" V="1"/>'
                    f'<Text>{label}</Text></Shape>')
        connects = ''.join(
            f'<Connect FromSheet="{sid}" FromCell="{end}" ToSheet="{target}" ToCell="PinX"/>'
            for sid in (101, 102)
            for end, target in (("BeginX", 1), ("EndX", 2))
        )
        page = (f'<PageContents xmlns="{V}"><Shapes>'
                + node(1, 1) + node(2, 6)
                + '<Shape ID="50" Type="Group"><Cell N="PinX" V="3"/>'
                  '<Cell N="PinY" V="2"/><Cell N="Width" V="3"/>'
                  '<Cell N="Height" V="2"/><Shapes>'
                + connector(101, 'SAN Fabric A')
                + connector(102, 'SAN Fabric B')
                + '</Shapes></Shape></Shapes><Connects>'
                + connects + '</Connects></PageContents>')
        stream = io.BytesIO()
        with ZipFile(stream, "w") as archive:
            archive.writestr("visio/pages/page1.xml", page)
        with ZipFile(io.BytesIO(stream.getvalue())) as archive:
            document = import_external_pages(archive)
        self.assertEqual(len(document["edges"]), 2)
        self.assertEqual({edge["label"] for edge in document["edges"]},
                         {"SAN Fabric A", "SAN Fabric B"})
        self.assertEqual(len({edge["id"] for edge in document["edges"]}), 2)
        self.assertEqual(len({edge["visio_connector_sheet_id"]
                              for edge in document["edges"]}), 2)


if __name__ == "__main__":
    unittest.main()
