import unittest
from openvisio.shapes import SHAPES, get_shape
class ShapesTests(unittest.TestCase):
    def test_categories(self):
        self.assertGreaterEqual(len(SHAPES), 8)
        for item in SHAPES.values():
            self.assertTrue(item["label"])
            self.assertTrue(item["fill"].startswith("#"))
    def test_fallback(self):
        self.assertEqual(get_shape("missing"), SHAPES["server"])
