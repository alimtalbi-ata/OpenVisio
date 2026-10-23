"""Real Tk canvas tests (skipped without a graphical display).
Author: Abdelhalim Talbi.
"""
import unittest
try:
    import tkinter as tk
except ImportError:
    tk = None
from openvisio.render import draw_document
from openvisio.connector_labels import layout_connector_labels
from test_connector_labels_v4234 import diagram


@unittest.skipIf(tk is None, 'Tkinter unavailable')
class TkLabelTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest('No graphical display: '+str(exc))
        self.canvas = tk.Canvas(self.root, width=900, height=600)
        self.canvas.pack()
        self.root.update()

    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_four_real_canvas_labels_match_layout(self):
        doc = diagram()
        draw_document(self.canvas, doc)
        expected = layout_connector_labels(doc['nodes'], doc['edges'])
        for edge_id, label in expected.labels.items():
            item = self.canvas.find_withtag(f'ov:edge:{edge_id}:label')
            self.assertEqual(len(item), 1)
            self.assertEqual(self.canvas.itemcget(item[0], 'text'), label.text)
            self.assertEqual(tuple(self.canvas.coords(item[0])), (label.x, label.y))

    def test_redraw_is_stable_and_selection_highlight_preserved(self):
        doc = diagram()
        draw_document(self.canvas, doc, selected_edge='fc-2')
        before = {edge['id']: tuple(self.canvas.coords(
            self.canvas.find_withtag(f"ov:edge:{edge['id']}:label")[0]))
            for edge in doc['edges']}
        draw_document(self.canvas, doc, selected_edge='fc-2')
        after = {edge['id']: tuple(self.canvas.coords(
            self.canvas.find_withtag(f"ov:edge:{edge['id']}:label")[0]))
            for edge in doc['edges']}
        self.assertEqual(before, after)
        self.assertEqual(self.canvas.itemcget(
            self.canvas.find_withtag('ov:edge:fc-2:label')[0], 'fill'), '#991b1b')


if __name__ == '__main__':
    unittest.main()
