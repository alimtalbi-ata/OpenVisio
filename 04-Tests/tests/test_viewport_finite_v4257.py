"""V42.57: reject non-finite persisted and transformed viewport coordinates."""
import math
import unittest
from openvisio.viewport import Viewport


class ViewportFiniteCoordinatesTests(unittest.TestCase):
    def test_constructor_rejects_invalid_persisted_state(self):
        for args in ((0, 0, 0), (-1, 0, 0), (math.nan, 0, 0),
                     (math.inf, 0, 0), (1, math.nan, 0),
                     (1, 0, -math.inf), (True, 0, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                Viewport(*args)

    def test_screen_rejects_bad_input_and_arithmetic_overflow(self):
        view = Viewport(4, 2, 3)
        for coords in ((math.nan, 1), (1, math.inf), (1e308, 0), (True, 2)):
            with self.subTest(coords=coords), self.assertRaises(ValueError):
                view.screen(*coords)
        self.assertEqual((view.zoom, view.offset_x, view.offset_y), (4, 2, 3))

    def test_world_rejects_bad_input_and_arithmetic_overflow(self):
        view = Viewport(0.001, -1e308, 0)
        for coords in ((math.nan, 1), (1, math.inf), (1e308, 0)):
            with self.subTest(coords=coords), self.assertRaises(ValueError):
                view.world(*coords)
        self.assertEqual((view.zoom, view.offset_x, view.offset_y),
                         (0.001, -1e308, 0))

    def test_normal_roundtrip_still_works(self):
        view = Viewport(1.5, 20, -30)
        self.assertEqual(view.world(*view.screen(200, 100)), (200, 100))


if __name__ == "__main__":
    unittest.main()
