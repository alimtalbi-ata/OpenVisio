"""V43.19: long equipment labels remain lossless in the editor and SVG.

Synthetic renderer tests; not a Microsoft Visio Desktop fidelity claim.
Author: Abdelhalim Talbi.
"""
from copy import deepcopy
import unittest
from xml.etree import ElementTree as ET

from openvisio.export import to_svg
from openvisio.node_labels import fit_node_label, label_char_limit, wrap_label_lines
from openvisio.render import draw_document

SVG = "{http://www.w3.org/2000/svg}"
LONG_LABEL = "Brocade G720 SAN fabric — host-01 " + "FC-PORT-0123456789-" * 4 + " WWPN 20:00:00:25:B5:11:22:33"


def document(label):
    return {"nodes": [{"id": "switch-a", "x": 160, "y": 120,
                       "label": label, "shape": "switch"}], "edges": []}


class FakeCanvas:
    def __init__(self):
        self.text = []
    def delete(self, *args, **kwargs):
        pass
    def create_rectangle(self, *args, **kwargs):
        pass
    def create_polygon(self, *args, **kwargs):
        pass
    def create_line(self, *args, **kwargs):
        pass
    def create_text(self, *args, **kwargs):
        self.text.append((args, kwargs))


class NodeLabelFidelityTests(unittest.TestCase):
    def test_wrapper_preserves_all_characters_and_never_exceeds_limit_for_tokens(self):
        rows = wrap_label_lines(LONG_LABEL, 16)
        self.assertEqual("".join(rows), LONG_LABEL)
        self.assertGreater(len(rows), 2)
        self.assertTrue(all(1 <= len(row) <= 16 for row in rows))

    def test_explicit_blank_and_trailing_lines_are_preserved(self):
        self.assertEqual(wrap_label_lines("a\r\n\r\nb\n", 12),
                         ("a", "", "b", ""))

    def test_long_label_font_scales_to_fit_shape_height_without_dropping_text(self):
        rows, font_size = fit_node_label(LONG_LABEL, 140, 60, font_size=13)
        self.assertLess(font_size, 13)
        self.assertEqual("".join(rows), LONG_LABEL)
        self.assertLessEqual(len(rows) * font_size * 1.35, 52)

    def test_width_estimator_rejects_invalid_geometry(self):
        self.assertGreaterEqual(label_char_limit(140), 1)
        for args in ((0,), (-1,), (True,), (float("inf"),)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                label_char_limit(args[0])

    def test_tk_renderer_does_not_truncate_long_equipment_label(self):
        data = document(LONG_LABEL)
        before = deepcopy(data)
        canvas = FakeCanvas()
        draw_document(canvas, data, grid=False)
        labels = [kwargs for _, kwargs in canvas.text
                  if "ov:node:switch-a:label" in kwargs.get("tags", ())]
        self.assertEqual(len(labels), 1)
        displayed = labels[0]["text"]
        self.assertEqual("".join(displayed.splitlines()), LONG_LABEL)
        self.assertNotIn("...", displayed)
        self.assertGreater(labels[0]["width"], 0)
        self.assertEqual(data, before)

    def test_svg_renderer_preserves_every_character_in_wrapped_equipment_label(self):
        data = document(LONG_LABEL)
        before = deepcopy(data)
        root = ET.fromstring(to_svg(data))
        text = root.find(SVG + "text")
        self.assertIsNotNone(text)
        spans = text.findall(SVG + "tspan")
        self.assertGreater(len(spans), 1)
        self.assertEqual("".join(span.text or "" for span in spans), LONG_LABEL)
        self.assertTrue(all(float(span.get("x")) == float(text.get("x")) for span in spans))
        self.assertGreater(float(text.get("x")), data["nodes"][0]["x"])
        self.assertEqual(data, before)

    def test_custom_shape_width_controls_wrapping_without_changing_model(self):
        data = document(LONG_LABEL)
        data["nodes"][0]["width"] = 220
        before = deepcopy(data)
        root = ET.fromstring(to_svg(data))
        spans = root.find(SVG + "text").findall(SVG + "tspan")
        self.assertGreater(len(spans), 1)
        standard = ET.fromstring(to_svg(document(LONG_LABEL)))
        standard_spans = standard.find(SVG + "text").findall(SVG + "tspan")
        self.assertLessEqual(len(spans), len(standard_spans))
        self.assertEqual(data, before)


if __name__ == "__main__":
    unittest.main()
