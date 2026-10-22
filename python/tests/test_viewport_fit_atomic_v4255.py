"""V42.55 regression: fit must not corrupt a working diagram viewport."""
import math
import unittest
from openvisio.viewport import Viewport


class ViewportFitAtomicTests(unittest.TestCase):
    def setUp(self):
        self.viewport = Viewport(1.25, 33, -44)
        self.original = (self.viewport.zoom, self.viewport.offset_x, self.viewport.offset_y)
        self.nodes = [{"x": 0, "y": 0}, {"x": 250, "y": 150}]

    def assert_unchanged(self):
        self.assertEqual((self.viewport.zoom, self.viewport.offset_x,
                          self.viewport.offset_y), self.original)

    def test_nonfinite_canvas_rejected_atomically(self):
        for width, height, margin in ((math.nan, 800, 80),
                                      (1200, math.inf, 80),
                                      (1200, 800, -math.inf),
                                      (0, 800, 80),
                                      (1200, -1, 80),
                                      (1200, 800, -1)):
            with self.subTest(values=(width, height, margin)):
                with self.assertRaises(ValueError):
                    self.viewport.fit(self.nodes, width, height, margin)
                self.assert_unchanged()

    def test_invalid_node_coordinates_rejected_atomically(self):
        for bad in (math.nan, math.inf, -math.inf):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.viewport.fit([{"x": bad, "y": 0}], 1200, 800)
                self.assert_unchanged()

    def test_overflowing_offsets_rejected_atomically(self):
        with self.assertRaises(ValueError):
            self.viewport.fit([{"x": 1e308, "y": 1e308},
                               {"x": -1e308, "y": -1e308}], 1200, 800)
        self.assert_unchanged()

    def test_small_canvas_and_empty_diagram_remain_supported(self):
        self.viewport.fit(self.nodes, 1, 1)
        self.assertTrue(all(math.isfinite(v) for v in
                            (self.viewport.zoom, self.viewport.offset_x, self.viewport.offset_y)))
        self.viewport.fit([], 800, 600)
        self.assertEqual((self.viewport.zoom, self.viewport.offset_x,
                          self.viewport.offset_y), (1.0, 0.0, 0.0))


if __name__ == '__main__':
    unittest.main()
