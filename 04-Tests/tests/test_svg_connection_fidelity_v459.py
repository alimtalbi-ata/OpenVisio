"""SVG export must preserve link routing and SAN annotations."""
import unittest
from xml.etree import ElementTree as ET
from openvisio.export import to_svg

class SvgConnectionFidelityTests(unittest.TestCase):
    def test_clipped_arrows_and_san_annotations(self):
        doc = {"nodes": [
            {"id": "a", "x": 100, "y": 100, "shape": "server"},
            {"id": "b", "x": 400, "y": 100, "shape": "san-switch"}],
            "edges": [{"id": "fc", "from": "a", "to": "b", "protocol": "FC", "fabric": "A", "speed_gbps": "32"}]}
        root = ET.fromstring(to_svg(doc))
        ns = "{http://www.w3.org/2000/svg}"
        lines = root.findall(f"{ns}line")
        self.assertEqual(len(lines), 1)
        self.assertGreater(float(lines[0].get("x1")), 100)
        self.assertLess(float(lines[0].get("x2")), 400)
        self.assertEqual(lines[0].get("marker-end"), "url(#ov-arrow)")
        labels = " ".join((e.text or "") for e in root.findall(f"{ns}text"))
        self.assertIn("FC", labels)
        self.assertIn("32 Gbit/s", labels)
