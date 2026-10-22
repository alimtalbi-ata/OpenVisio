"""V42.54: protect diagram navigation against corrupting invalid pointer input."""
import math
import unittest
from openvisio.viewport import Viewport


class ViewportAtomicInputTests(unittest.TestCase):
    def test_reject_invalid_zoom_without_mutation(self):
        for factor in (0, -1, math.nan, math.inf, -math.inf):
            viewport = Viewport(1.5, 20, -30)
            with self.subTest(factor=factor), self.assertRaises(ValueError):
                viewport.zoom_at(factor, 100, 200)
            self.assertEqual((viewport.zoom, viewport.offset_x, viewport.offset_y),
                             (1.5, 20, -30))

    def test_reject_nonfinite_pointer_without_mutation(self):
        for x, y in ((math.nan, 2), (2, math.inf), (-math.inf, 2)):
            viewport = Viewport(0.5, 11, 22)
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                viewport.zoom_at(1.2, x, y)
            self.assertEqual((viewport.zoom, viewport.offset_x, viewport.offset_y),
                             (0.5, 11, 22))

    def test_reject_invalid_pan_without_mutation(self):
        for dx, dy in ((math.nan, 1), (1, math.inf), (-math.inf, 1)):
            viewport = Viewport(1, 7, 9)
            with self.subTest(dx=dx, dy=dy), self.assertRaises(ValueError):
                viewport.pan(dx, dy)
            self.assertEqual((viewport.offset_x, viewport.offset_y), (7, 9))

    def test_fit_zoom_still_preserves_pointer_anchor(self):
        viewport = Viewport(0.001, 300, 200)
        anchor = viewport.world(110, 70)
        viewport.zoom_at(1.5, 110, 70)
        self.assertEqual(viewport.world(110, 70), anchor)


if __name__ == '__main__':
    unittest.main()
