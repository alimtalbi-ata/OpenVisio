"""V43.18: preserve explicit multiline labels in Tk and native SVG exports.

Synthetic renderer regression tests only; no Microsoft Visio Desktop claim.
Author: Abdelhalim Talbi.
"""
import unittest
from xml.etree import ElementTree as ET

from openvisio.export import to_svg
from openvisio.connector_labels import layout_connector_labels

SVG = "{http://www.w3.org/2000/svg}"


def node_document(label):
    return {
        "nodes": [{"id": "host", "x": 100, "y": 100,
                   "label": label, "shape": "server"}],
        "edges": [],
    }


def connector_document(label):
    return {
        "nodes": [
            {"id": "host", "x": 100, "y": 120,
             "label": "Compute", "shape": "server"},
            {"id": "array", "x": 600, "y": 120,
             "label": "Storage", "shape": "storage"},
        ],
        "edges": [{"id": "FC-A", "from": "host", "to": "array",
                   "label": label, "protocol": "FC"}],
    }


class SvgMultilineLabelTests(unittest.TestCase):
    def test_equipment_label_keeps_each_explicit_line(self):
        root = ET.fromstring(to_svg(node_document("Compute\r\nNode\nA")))
        texts = root.findall(SVG + "text")
        self.assertEqual(len(texts), 1)
        spans = texts[0].findall(SVG + "tspan")
        self.assertEqual([span.text or "" for span in spans], ["Compute", "Node", "A"])
        self.assertEqual([span.get("dy") for span in spans], ["-1.2em", "1.2em", "1.2em"])
        self.assertTrue(all(span.get("x") == texts[0].get("x") for span in spans))

    def test_connector_caption_keeps_lines_and_label_geometry_height(self):
        document = connector_document("Fabric A\nPort 7")
        layout = layout_connector_labels(document["nodes"], document["edges"])
        self.assertIn("FC-A", layout.labels)
        box = layout.labels["FC-A"].bounds
        self.assertGreaterEqual(box[3] - box[1], 30.0)
        root = ET.fromstring(to_svg(document))
        caption = next(node for node in root.findall(SVG + "text")
                       if node.get("data-openvisio-edge") == "FC-A")
        self.assertEqual([span.text or "" for span in caption.findall(SVG + "tspan")],
                         ["Fabric A", "Port 7"])

    def test_line_breaks_do_not_inflate_width_beyond_longest_line(self):
        short = connector_document("X\n" + "A" * 40)
        plain = connector_document("A" * 40)
        short_layout = layout_connector_labels(short["nodes"], short["edges"])
        plain_layout = layout_connector_labels(plain["nodes"], plain["edges"])
        self.assertIn("FC-A", short_layout.labels)
        self.assertIn("FC-A", plain_layout.labels)
        short_box = short_layout.labels["FC-A"].bounds
        plain_box = plain_layout.labels["FC-A"].bounds
        self.assertAlmostEqual(short_box[2] - short_box[0],
                               plain_box[2] - plain_box[0])

    def test_single_line_output_remains_a_plain_text_node(self):
        root = ET.fromstring(to_svg(node_document("Compute Node A")))
        text = root.find(SVG + "text")
        self.assertEqual(text.text, "Compute Node A")
        self.assertEqual(text.findall(SVG + "tspan"), [])


if __name__ == "__main__":
    unittest.main()
