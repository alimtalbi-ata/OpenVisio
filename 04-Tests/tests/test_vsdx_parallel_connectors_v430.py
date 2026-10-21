"""Parallel SAN links must not disappear silently during external Visio import. Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx import import_vsdx

V='http://schemas.microsoft.com/office/visio/2011/1/core'

def fixture():
    return f'''<PageContents xmlns="{V}"><Shapes>
      <Shape ID="1" NameU="SAN A"><Cell N="PinX" V="1"/><Cell N="PinY" V="1"/></Shape>
      <Shape ID="2" NameU="SAN B"><Cell N="PinX" V="4"/><Cell N="PinY" V="1"/></Shape>
    </Shapes><Connects>
      <Connect FromSheet="3" FromCell="BeginX" ToSheet="1"/><Connect FromSheet="3" FromCell="EndX" ToSheet="2"/>
      <Connect FromSheet="4" FromCell="BeginX" ToSheet="1"/><Connect FromSheet="4" FromCell="EndX" ToSheet="2"/>
    </Connects></PageContents>'''

class ParallelConnectorsTests(unittest.TestCase):
    def test_parallel_links_loss_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'parallel.vsdx'
            with ZipFile(path,'w') as archive:
                archive.writestr('visio/pages/page1.xml',fixture())
            result=import_vsdx(path)
            self.assertEqual(len(result['nodes']),2)
            self.assertEqual(len(result['edges']),1)
            self.assertEqual(result['metadata']['omitted_parallel_links'],1)
            self.assertIn('liens parallèles',result['metadata']['import_warning'])
            self.assertEqual(len({e['id'] for e in result['edges']}),1)
