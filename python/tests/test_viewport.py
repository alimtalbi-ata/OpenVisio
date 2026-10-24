import unittest
from openvisio.viewport import MIN_ZOOM, Viewport

class ViewportTests(unittest.TestCase):
    def test_roundtrip(self):
        v = Viewport(2, 20, -40)
        self.assertEqual(v.world(*v.screen(100, 50)), (100, 50))
    def test_zoom_preserves_anchor(self):
        v = Viewport()
        before = v.world(250, 180)
        v.zoom_at(1.5, 250, 180)
        self.assertEqual(v.world(250, 180), before)
    def test_zoom_limits(self):
        v = Viewport()
        v.zoom_at(100, 0, 0)
        self.assertEqual(v.zoom, 4)
        v.zoom_at(0.0001, 0, 0)
        self.assertEqual(v.zoom, MIN_ZOOM)
    def test_pan(self):
        v = Viewport()
        v.pan(30, -20)
        self.assertEqual(v.screen(0, 0), (30, -20))
    def test_fit(self):
        v = Viewport()
        v.fit([{"x":-1000,"y":-500},{"x":1000,"y":500}], 1200, 800)
        for x,y in [(-1000,-500),(1000,500)]:
            sx,sy=v.screen(x,y)
            self.assertGreater(sx, 0)
            self.assertLess(sx, 1200)
            self.assertGreater(sy, 0)
            self.assertLess(sy, 800)
