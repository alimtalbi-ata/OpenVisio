"""Regression: palette drag-drop must not overlap an existing equipment."""
import unittest
from openvisio.palette_placement import next_free_position

class PaletteDropClearanceTests(unittest.TestCase):
    def test_drop_on_existing_node_chooses_free_position(self):
        nodes = [{"id": "storage-a", "x": 240, "y": 120}]
        x, y = next_free_position((240, 120), nodes)
        self.assertTrue(abs(x-240) >= 145 or abs(y-120) >= 65)
        self.assertNotEqual((x, y), (240, 120))

    def test_drop_on_empty_canvas_preserves_pointer(self):
        self.assertEqual(next_free_position((241.2, 119.7), []), (241, 120))
