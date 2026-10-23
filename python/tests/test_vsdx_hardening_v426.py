import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import import_vsdx

class VsdxHardeningTests(unittest.TestCase):
    def test_windows_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'attack.vsdx'
            with ZipFile(path, 'w', ZIP_DEFLATED) as z:
                z.writestr('visio\\..\\..\\payload.xml', 'bad')
            with self.assertRaisesRegex(ValueError, 'non sûre'):
                import_vsdx(path)

    def test_doctype_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'entity.vsdx'
            with ZipFile(path, 'w', ZIP_DEFLATED) as z:
                z.writestr('visio/pages/page1.xml', '<!DOCTYPE x [<!ENTITY a "hello">]><PageContents/>')
            with self.assertRaisesRegex(ValueError, 'entités externes'):
                import_vsdx(path)
