"""Labels must remain valid XML after truncation."""
import unittest
from xml.etree import ElementTree as ET
from openvisio.export import to_svg

class SvgLabelEscapingTests(unittest.TestCase):
    def test_truncation_does_not_split_xml_entity(self):
        label = "A" * 39 + "&" + "suffix"
        doc = {"nodes": [{"id": "n", "x": 100, "y": 100, "label": label}], "edges": []}
        root = ET.fromstring(to_svg(doc))
        ns = "{http://www.w3.org/2000/svg}"
        texts = [el.text for el in root.findall(f"{ns}text")]
        self.assertIn("A" * 39 + "&", texts)

    def test_angle_brackets_and_ampersand(self):
        doc = {"nodes": [{"id": "n", "x": 100, "y": 100, "label": "<SAN & NAS>"}], "edges": []}
        root = ET.fromstring(to_svg(doc))
        ns = "{http://www.w3.org/2000/svg}"
        self.assertIn("<SAN & NAS>", [el.text for el in root.findall(f"{ns}text")])
