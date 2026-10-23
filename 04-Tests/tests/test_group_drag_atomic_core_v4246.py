"""Portable V42.46 regression for nested group drag. Author: Abdelhalim Talbi."""
import unittest
from openvisio.layout import move_group


def nodes():
    return [
        {"id": "g", "shape": "visio-group", "x": 105., "y": 105.},
        {"id": "c", "visio_group_parent": "g", "x": 118., "y": 110.},
        {"id": "nested", "shape": "visio-group", "visio_group_parent": "g", "x": 140., "y": 120.},
        {"id": "leaf", "visio_group_parent": "nested", "x": 145., "y": 126.},
        {"id": "outside", "x": 380., "y": 200.},
    ]


def positions(items):
    return {n["id"]: (n["x"], n["y"]) for n in items}


class AtomicGroupDragTests(unittest.TestCase):
    def test_group_envelope_moves_all_descendants(self):
        data = nodes()
        self.assertTrue(move_group(data, {"g"}, 30, -20))
        self.assertEqual(positions(data)["leaf"], (175., 106.))
        self.assertEqual(positions(data)["c"], (148., 90.))
        self.assertEqual(positions(data)["outside"], (380., 200.))

    def test_expanded_selection_does_not_double_move(self):
        data = nodes()
        self.assertTrue(move_group(data, {"g", "c", "nested", "leaf"}, 15, 25))
        self.assertEqual(positions(data)["leaf"], (160., 151.))

    def test_nested_group_moves_its_descendants_only(self):
        data = nodes()
        self.assertTrue(move_group(data, {"nested"}, 0, 40))
        self.assertEqual(positions(data)["leaf"], (145., 166.))
        self.assertEqual(positions(data)["c"], (118., 110.))

    def test_grid_snap_preserves_relative_offsets(self):
        data = nodes()
        self.assertTrue(move_group(data, {"g", "nested"}, 23, 31, spacing=20))
        self.assertEqual(positions(data)["g"], (120., 140.))
        self.assertEqual(positions(data)["leaf"], (160., 161.))


if __name__ == "__main__":
    unittest.main()
