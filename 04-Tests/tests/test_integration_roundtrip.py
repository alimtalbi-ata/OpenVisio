import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from openvisio.model import save, load
from openvisio.export import export_svg
from openvisio.properties import normalize_properties
from openvisio.links import normalize_link
from openvisio.history import History

class IntegrationTests(unittest.TestCase):
    def test_edit_save_reopen_export_and_undo(self):
        a = {"id":"srv","x":100,"y":120,"shape":"server",**normalize_properties("ESXi-01",hostname="esxi01.example",address="192.0.2.11")}
        b = {"id":"san","x":400,"y":120,"shape":"san-switch",**normalize_properties("Fabric-A",vendor="Brocade")}
        edge = {"id":"fc1","from":"srv","to":"san",**normalize_link(protocol="FC",source_port="vmhba0",target_port="1/1",fabric="A",speed_gbps="32")}
        document = {"nodes":[a,b],"edges":[edge]}
        history = History(document)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "infra.ovjson"
            svg = Path(folder) / "infra.svg"
            save(path, document)
            self.assertEqual(load(path), document)
            export_svg(svg, load(path))
            root = ET.parse(svg).getroot()
            self.assertTrue(root.tag.endswith("svg"))
            document["nodes"][0]["x"] = 200
            history.record(document)
            self.assertEqual(history.undo()["nodes"][0]["x"], 100)
