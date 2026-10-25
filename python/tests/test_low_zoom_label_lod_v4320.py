"""V43.20: zoom-aware label LOD avoids oversized captions in overview."""
from copy import deepcopy
import unittest
from openvisio.export import to_svg
from openvisio.render import draw_document

LONG_LABEL = "Brocade G720 SAN fabric — FC-PORT-0123456789- WWPN 20:00:00:25:B5:11:22:33"


def make_document():
    return {"nodes": [{"id": "switch-a", "x": 160, "y": 120,
                       "label": LONG_LABEL, "shape": "switch"}], "edges": []}


class FakeCanvas:
    def __init__(self):
        self.text = []
        self.rectangles = []
    def delete(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): self.rectangles.append((args, kwargs))
    def create_polygon(self, *args, **kwargs): pass
    def create_line(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): self.text.append((args, kwargs))
    def winfo_width(self): return 800
    def winfo_height(self): return 600


class FakeViewport:
    def __init__(self, zoom):
        self.zoom = zoom
    def screen(self, x, y):
        return x * self.zoom, y * self.zoom
    def world(self, x, y):
        return x / self.zoom, y / self.zoom


def node_label_calls(canvas):
    return [kw for _, kw in canvas.text if "ov:node:switch-a:label" in kw.get("tags", ())]


class NodeLabelLowZoomTests(unittest.TestCase):
    def test_low_zoom_hides_only_visual_label_and_keeps_node_geometry(self):
        doc = make_document()
        before = deepcopy(doc)
        canvas = FakeCanvas()
        draw_document(canvas, doc, viewport=FakeViewport(0.15), grid=False)
        self.assertEqual(node_label_calls(canvas), [])
        self.assertEqual(len(canvas.rectangles), 1)
        self.assertEqual(doc, before)
        # Low zoom is a Tk display-level optimisation, not a model/export mutation.
        self.assertIn(LONG_LABEL, to_svg(doc))

    def test_normal_zoom_keeps_complete_label_visible(self):
        doc = make_document()
        before = deepcopy(doc)
        canvas = FakeCanvas()
        draw_document(canvas, doc, viewport=FakeViewport(0.5), grid=False)
        labels = node_label_calls(canvas)
        self.assertEqual(len(labels), 1)
        self.assertEqual("".join(labels[0]["text"].splitlines()), LONG_LABEL)
        self.assertEqual(doc, before)

    def test_boundary_zoom_does_not_toggle_based_on_label_length(self):
        short = make_document()
        short["nodes"][0]["label"] = "SAN-A"
        long = make_document()
        for doc in (short, long):
            canvas = FakeCanvas()
            draw_document(canvas, doc, viewport=FakeViewport(0.29), grid=False)
            self.assertEqual(node_label_calls(canvas), [])
        self.assertEqual(short["nodes"][0]["label"], "SAN-A")
        self.assertEqual(long["nodes"][0]["label"], LONG_LABEL)


if __name__ == "__main__":
    unittest.main()
