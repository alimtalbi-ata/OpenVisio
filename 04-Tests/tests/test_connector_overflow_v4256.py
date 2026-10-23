"""V42.56 regression: imported Visio/SAN geometry must never generate NaN points."""
import math
import unittest
from openvisio.connector_geometry import connector_endpoints, lane_endpoints


class ConnectorOverflowTests(unittest.TestCase):
    def test_finite_endpoints_with_overflowing_delta_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'hors limites'):
            connector_endpoints({'x': 1e308, 'y': 0}, {'x': -1e308, 'y': 0})

    def test_nonfinite_parallel_lane_is_refused(self):
        a, b = {'x': 0, 'y': 0}, {'x': 400, 'y': 0}
        for lane in (math.nan, math.inf, -math.inf):
            with self.subTest(lane=lane), self.assertRaises(ValueError):
                lane_endpoints(a, b, lane)

    def test_valid_parallel_lane_still_attaches_to_shape_boundaries(self):
        a, b = {'x': 0, 'y': 0}, {'x': 400, 'y': 0}
        self.assertEqual(lane_endpoints(a, b, 12), ((70.0, 12), (330.0, 12)))


if __name__ == '__main__':
    unittest.main()
