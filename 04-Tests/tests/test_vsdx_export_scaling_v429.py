"""VSDX export performance regression. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx import export_vsdx

class ExportScalingTests(unittest.TestCase):
    def test_large_fabric_exports_all_connectors(self):
        # Structural test: 750 nodes and 1,499 connectors. No timing threshold.
        nodes = [{"id":f"n{i}","x":float(i%30)*180,"y":float(i//30)*110,"label":f"SAN {i}"} for i in range(750)]
        edges = [{"id":f"e{i}","from":f"n{i%750}","to":f"n{(i+1+(i//750))%750}"} for i in range(1499)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"fabric.vsdx"
            export_vsdx(p,{"nodes":nodes,"edges":edges})
            with ZipFile(p) as z:
                xml=z.read("visio/pages/page1.xml")
                self.assertEqual(xml.count(b'NameU="OpenVisio connector"'),1499)
                self.assertEqual(xml.count(b'NameU="OpenVisio node"'),750)
