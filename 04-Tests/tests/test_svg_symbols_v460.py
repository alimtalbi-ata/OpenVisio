"""Regression checks for semantic SVG infrastructure glyphs."""
import unittest
from xml.etree import ElementTree as ET
from openvisio.export import to_svg

class SvgSymbolTests(unittest.TestCase):
    def test_infrastructure_glyphs_are_not_generic_rectangles(self):
        kinds = ("server", "storage", "san-switch", "network-switch", "database", "firewall")
        doc = {"nodes": [{"id": str(i), "x": 100 + i*200, "y": 100, "shape": kind, "label": kind}
                         for i, kind in enumerate(kinds)], "edges": []}
        root = ET.fromstring(to_svg(doc))
        ns = "{http://www.w3.org/2000/svg}"
        self.assertGreater(len(root.findall(f".//{ns}ellipse")), 0)
        self.assertGreater(len(root.findall(f".//{ns}line")), 0)
        self.assertGreater(len(root.findall(f".//{ns}rect")), len(kinds))
        self.assertEqual(len(root.findall(f"{ns}text")), len(kinds))
