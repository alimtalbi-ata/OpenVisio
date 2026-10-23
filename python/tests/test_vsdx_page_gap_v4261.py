"""Synthetic Visio page-spacing regression; not a Microsoft Visio fidelity test.
Author: Abdelhalim Talbi.
"""
import io
import unittest
from zipfile import ZipFile
from openvisio.vsdx_external import import_external_pages
from openvisio.node_geometry import node_bounds

V = 'http://schemas.microsoft.com/office/visio/2011/1/core'
OR = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
R = 'http://schemas.openxmlformats.org/package/2006/relationships'


class PageGapTests(unittest.TestCase):
    def test_negative_page_overflow_preserves_clearance(self):
        pages = (f'<Pages xmlns="{V}" xmlns:r="{OR}">'
                 '<Page ID="1"><Rel r:id="r1"/></Page>'
                 '<Page ID="2"><Rel r:id="r2"/></Page></Pages>')
        rels = (f'<Relationships xmlns="{R}">'
                '<Relationship Id="r1" Target="page1.xml"/>'
                '<Relationship Id="r2" Target="page2.xml"/></Relationships>')
        def shape(y):
            return (f'<PageContents xmlns="{V}"><Shapes><Shape ID="1">'
                    f'<Cell N="PinX" V="1"/><Cell N="PinY" V="{y}"/>'
                    '<Cell N="Width" V="1"/><Cell N="Height" V="1"/>'
                    '</Shape></Shapes></PageContents>')
        stream = io.BytesIO()
        with ZipFile(stream, 'w') as archive:
            archive.writestr('visio/pages/pages.xml', pages)
            archive.writestr('visio/pages/_rels/pages.xml.rels', rels)
            archive.writestr('visio/pages/page1.xml', shape('-12'))
            archive.writestr('visio/pages/page2.xml', shape('4'))
        with ZipFile(io.BytesIO(stream.getvalue())) as archive:
            doc = import_external_pages(archive)
        a, b = doc['nodes']
        self.assertGreaterEqual(node_bounds(b)[1] - node_bounds(a)[3], 96)
        self.assertGreater(doc['metadata']['page_bottom_overflow_px_total'], 1000)
        self.assertEqual(doc['metadata']['page_extent_expanded'], 1)


if __name__ == '__main__':
    unittest.main()
