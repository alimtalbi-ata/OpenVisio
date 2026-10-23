"""V42.32 actual Tk Canvas integration. Author: Abdelhalim Talbi."""
import unittest
try:
    import tkinter as tk
except ImportError:
    tk = None
from openvisio.render import draw_document
from openvisio.retained_canvas import RetainedCanvasRenderer
from test_parallel_geometry_v4232 import doc


@unittest.skipIf(tk is None, 'Tkinter not installed')
class ParallelCanvasTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest('No graphical display: ' + str(exc))
        self.canvas = tk.Canvas(self.root, width=700, height=300)
        self.canvas.pack()
        self.root.update()

    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_two_parallel_paths_have_distinct_tk_coords(self):
        draw_document(self.canvas, doc())
        a = self.canvas.find_withtag('ov:edge:path-0:path')
        b = self.canvas.find_withtag('ov:edge:path-1:path')
        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 1)
        self.assertNotEqual(self.canvas.coords(a[0]), self.canvas.coords(b[0]))

    def test_retained_canvas_preserves_both_path_items_on_redraw(self):
        renderer = RetainedCanvasRenderer(self.canvas)
        renderer.draw(doc())
        before = [self.canvas.find_withtag('ov:edge:path-%s:path' % i)[0] for i in range(2)]
        renderer.draw(doc())
        after = [self.canvas.find_withtag('ov:edge:path-%s:path' % i)[0] for i in range(2)]
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
