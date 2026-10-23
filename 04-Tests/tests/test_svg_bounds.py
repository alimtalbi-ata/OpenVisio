import unittest
import xml.etree.ElementTree as ET
from openvisio.export import to_svg

class SvgBoundsTests(unittest.TestCase):
    def test_negative_coordinates_visible(self):
        svg = ET.fromstring(to_svg({"nodes":[{"id":"a","x":-400,"y":-200}],"edges":[]}))
        x, y, width, height = map(float, svg.attrib["viewBox"].split())
        self.assertLess(x, -470)
        self.assertLess(y, -230)
        self.assertGreater(width, 140)
        self.assertGreater(height, 60)
    def test_distant_nodes_expand_viewbox(self):
        svg = ET.fromstring(to_svg({"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":5000,"y":3000}],"edges":[]}))
        self.assertGreater(float(svg.attrib["viewBox"].split()[2]), 5000)
    def test_empty_diagram_has_default_canvas(self):
        svg = ET.fromstring(to_svg({"nodes":[],"edges":[]}))
        self.assertEqual(svg.attrib["viewBox"], "0 0 800 600")
    def test_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            to_svg({"nodes":[],"edges":[]}, width=0)
