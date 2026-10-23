import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx

class ExternalGeometryTests(unittest.TestCase):
    def test_nonfinite_coordinates_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.vsdx"
            xml=b'<PageContents xmlns="http://schemas.microsoft.com/office/visio/2011/1/core"><Shapes><Shape ID="1"><Cell N="PinX" V="NaN"/><Cell N="PinY" V="3"/></Shape><Shape ID="2"><Cell N="PinX" V="1"/><Cell N="PinY" V="Infinity"/></Shape></Shapes></PageContents>'
            with ZipFile(p,"w",ZIP_DEFLATED) as z:z.writestr("visio/pages/page1.xml",xml)
            self.assertEqual(import_vsdx(p)["nodes"],[])
