"""Perimeter attachment regressions, including VSDX exported coordinates.
Author: Abdelhalim Talbi.
"""
import math
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.connector_geometry import connector_endpoints
from openvisio.render import edge_at, draw_document
from openvisio.vsdx import export_vsdx, V, PX_PER_IN


class ConnectorGeometryTests(unittest.TestCase):
    def test_horizontal_boundary(self):
        a, b = {"x": 0, "y": 0}, {"x": 300, "y": 0}
        self.assertEqual(connector_endpoints(a, b), ((70, 0), (230, 0)))

    def test_reverse_direction(self):
        self.assertEqual(connector_endpoints({"x": 300, "y": 0}, {"x": 0, "y": 0}),
                         ((230, 0), (70, 0)))

    def test_vertical_boundary(self):
        self.assertEqual(connector_endpoints({"x": 0, "y": 0}, {"x": 0, "y": 200}),
                         ((0, 30), (0, 170)))

    def test_diagonal_boundary(self):
        (x1, y1), (x2, y2) = connector_endpoints({"x": 0, "y": 0}, {"x": 300, "y": 300})
        self.assertAlmostEqual(x1, 30)
        self.assertAlmostEqual(y1, 30)
        self.assertAlmostEqual(x2, 270)
        self.assertAlmostEqual(y2, 270)

    def test_overlap_does_not_reverse_arrow(self):
        self.assertEqual(connector_endpoints({"x": 0, "y": 0}, {"x": 100, "y": 0}),
                         ((0, 0), (100, 0)))
        self.assertEqual(connector_endpoints({"x": 0, "y": 0}, {"x": 0, "y": 0}),
                         ((0, 0), (0, 0)))

    def test_reject_invalid_dimensions_and_nonfinite(self):
        with self.assertRaises(ValueError):
            connector_endpoints({"x": 0, "y": 0}, {"x": math.inf, "y": 1})
        with self.assertRaises(ValueError):
            connector_endpoints({"x": 0, "y": 0}, {"x": 200, "y": 1}, half_height=0)

    def test_hit_testing_excludes_node_interior(self):
        nodes = [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 300, "y": 0}]
        edges = [{"id": "ab", "from": "a", "to": "b"}]
        self.assertIsNone(edge_at(nodes, edges, 30, 0, tolerance=5))
        self.assertEqual(edge_at(nodes, edges, 150, 0, tolerance=5)["id"], "ab")

    def test_canvas_draws_at_boundaries(self):
        class Canvas:
            def __init__(self): self.lines = []
            def delete(self, *args): pass
            def create_line(self, *args, **kwargs): self.lines.append(args)
            def create_rectangle(self, *args, **kwargs): pass
            def create_text(self, *args, **kwargs): pass
        canvas = Canvas()
        doc = {"nodes": [{"id": "a", "x": 0, "y": 0},
                         {"id": "b", "x": 300, "y": 0}],
               "edges": [{"id": "ab", "from": "a", "to": "b"}]}
        draw_document(canvas, doc)
        self.assertEqual(canvas.lines, [(70.0, 0.0, 230.0, 0.0)])

    def test_vsdx_exports_clipped_coordinates(self):
        doc = {"nodes": [{"id": "a", "x": 0, "y": 0, "label": "A"},
                         {"id": "b", "x": 300, "y": 0, "label": "B"}],
               "edges": [{"id": "ab", "from": "a", "to": "b"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.vsdx"
            export_vsdx(path, doc)
            with ZipFile(path) as z:
                page = ET.fromstring(z.read("visio/pages/page1.xml"))
            connector = next(s for s in page.findall(f".//{{{V}}}Shape")
                             if s.get("NameU") == "OpenVisio connector")
            cells = {c.get("N"): float(c.get("V")) for c in connector.findall(f"{{{V}}}Cell")
                     if c.get("N") in {"BeginX", "EndX", "BeginY", "EndY"}}
            self.assertAlmostEqual((cells["EndX"] - cells["BeginX"]) * PX_PER_IN, 160, delta=.001)
            self.assertAlmostEqual(cells["EndY"], cells["BeginY"], delta=.001)
