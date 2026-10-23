"""Portable group-layout regression. Author: Abdelhalim Talbi."""
import unittest
from openvisio.layout import align, distribute


class GroupLayoutCoreTests(unittest.TestCase):
    def test_align_moves_children_of_selected_group(self):
        nodes = [
            {"id": "g", "x": 100, "y": 50},
            {"id": "c", "x": 120, "y": 60, "visio_group_parent": "g"},
            {"id": "h", "x": 300, "y": 150},
        ]
        self.assertTrue(align(nodes, {"g", "h"}, "y"))
        self.assertEqual([(n["id"], n["y"]) for n in nodes],
                         [("g", 100), ("c", 110), ("h", 100)])

    def test_nested_child_selected_does_not_double_move(self):
        nodes = [
            {"id": "g", "x": 0, "y": 0},
            {"id": "c", "x": 10, "y": 0, "visio_group_parent": "g"},
            {"id": "n", "x": 12, "y": 0, "visio_group_parent": "c"},
            {"id": "h", "x": 100, "y": 0},
        ]
        self.assertTrue(align(nodes, {"g", "c", "n", "h"}, "x"))
        self.assertEqual([n["x"] for n in nodes], [50, 60, 62, 50])

    def test_distribution_moves_middle_group_and_child(self):
        nodes = [
            {"id": "a", "x": 0, "y": 0},
            {"id": "g", "x": 25, "y": 0},
            {"id": "c", "x": 35, "y": 0, "visio_group_parent": "g"},
            {"id": "z", "x": 100, "y": 0},
        ]
        self.assertTrue(distribute(nodes, {"a", "g", "c", "z"}, "x"))
        self.assertEqual([n["x"] for n in nodes], [0, 50, 60, 100])

    def test_invalid_axis_does_not_modify(self):
        nodes = [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 20, "y": 0}]
        with self.assertRaises(ValueError):
            align(nodes, {"a", "b"}, "z")
        self.assertEqual(nodes[0]["x"], 0)


if __name__ == "__main__":
    unittest.main()
