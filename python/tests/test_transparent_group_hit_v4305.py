"""V43.05: transparent Visio groups must not mask SAN editing.

Pure geometry tests; no claim of interactive Windows or Microsoft Visio
Desktop qualification. Author: Abdelhalim Talbi.
"""
import unittest

from openvisio.render import edge_at, node_at


class TransparentGroupHitTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            {"id": "server", "x": 60, "y": 100, "shape": "server"},
            {"id": "switch", "x": 340, "y": 100, "shape": "san-switch"},
            # Group appears LAST and covers the link, as in imported VSDX.
            {"id": "group", "x": 200, "y": 100, "width": 500,
             "height": 240, "shape": "visio-group"},
        ]
        self.edges = [{"id": "fc-a", "from": "server", "to": "switch",
                       "routing": "straight"}]

    def test_group_interior_is_transparent_to_connector_selection(self):
        self.assertIsNone(node_at(self.nodes, 200, 100))
        self.assertEqual(edge_at(self.nodes, self.edges, 200, 100)["id"], "fc-a")

    def test_group_does_not_hide_child_equipment(self):
        self.assertEqual(node_at(self.nodes, 60, 100)["id"], "server")
        self.assertEqual(node_at(self.nodes, 340, 100)["id"], "switch")

    def test_group_outline_remains_selectable(self):
        self.assertEqual(node_at(self.nodes, 200, -20)["id"], "group")
        self.assertEqual(node_at(self.nodes, -50, 100)["id"], "group")

    def test_zoom_tolerance_never_fills_entire_group(self):
        self.assertIsNone(node_at(self.nodes, 200, 100, group_border_tolerance=100000))
        self.assertEqual(node_at(self.nodes, 200, -20,
                                 group_border_tolerance=100000)["id"], "group")

    def test_solid_node_wins_even_on_group_frame(self):
        nodes = [
            {"id": "child", "x": 0, "y": 0, "shape": "server"},
            {"id": "group", "x": 70, "y": 0, "width": 140,
             "height": 120, "shape": "visio-group"},
        ]
        self.assertEqual(node_at(nodes, 0, 0)["id"], "child")

    def test_outside_group_remains_empty(self):
        self.assertIsNone(node_at(self.nodes, 200, 300))


if __name__ == "__main__":
    unittest.main()
