"""Regression for SAN links crossing imported transparent Visio group borders.

Tests pure hit-testing, not a claim of manual Windows/Visio qualification.
Author: Abdelhalim Talbi.
"""
import unittest
from openvisio.render import node_at, edge_at, object_at


class GroupFrameConnectorSelectionTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            {"id": "host", "x": 0, "y": 0, "shape": "server"},
            {"id": "switch", "x": 400, "y": 0, "shape": "san-switch"},
            {"id": "group", "x": 200, "y": 0, "width": 200,
             "height": 160, "shape": "visio-group"},
        ]
        self.edges = [{"id": "fc-fabric-a", "from": "host", "to": "switch",
                       "routing": "straight"}]

    def test_reproduces_group_border_intercepting_physical_path(self):
        self.assertEqual(node_at(self.nodes, 100, 0)["id"], "group")
        self.assertEqual(edge_at(self.nodes, self.edges, 100, 0)["id"], "fc-fabric-a")
        node, edge = object_at(self.nodes, self.edges, 100, 0)
        self.assertIsNone(node)
        self.assertEqual(edge["id"], "fc-fabric-a")

    def test_group_frame_remains_selectable_away_from_connector(self):
        node, edge = object_at(self.nodes, self.edges, 100, 65)
        self.assertEqual(node["id"], "group")
        self.assertIsNone(edge)

    def test_solid_equipment_wins_over_connector(self):
        node, edge = object_at(self.nodes, self.edges, 0, 0)
        self.assertEqual(node["id"], "host")
        self.assertIsNone(edge)

    def test_group_interior_does_not_mask_link(self):
        node, edge = object_at(self.nodes, self.edges, 200, 0)
        self.assertIsNone(node)
        self.assertEqual(edge["id"], "fc-fabric-a")

    def test_empty_space_is_not_a_group_selection(self):
        node, edge = object_at(self.nodes, self.edges, 200, 300)
        self.assertIsNone(node)
        self.assertIsNone(edge)

    def test_group_border_selection_with_tight_zoom_tolerance(self):
        node, edge = object_at(self.nodes, self.edges, 300, 70,
                               node_tolerance=1, edge_tolerance=1)
        self.assertEqual(node["id"], "group")
        self.assertIsNone(edge)


if __name__ == "__main__":
    unittest.main()
