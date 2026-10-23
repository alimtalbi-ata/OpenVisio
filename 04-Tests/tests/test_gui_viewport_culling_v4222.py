"""Real Tk canvas tests, run with OPENVISIO_GUI_TESTS=1 under a display.
Author: Abdelhalim Talbi.
"""
import os
import tkinter as tk
import unittest

from openvisio.app import Editor


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'Real Tk display required')
class ViewportCullingGuiTests(unittest.TestCase):
    def setUp(self):
        self.editor = Editor()
        self.editor.geometry('1000x700+0+0')
        self.editor.update_idletasks()
        self.editor.update()
        nodes = [{'id': f'n{i}', 'label': f'Server {i}',
                  'x': 140 + (i % 40) * 200,
                  'y': 120 + (i // 40) * 130}
                 for i in range(1200)]
        edges = [{'id': f'e{i}', 'from': f'n{i}', 'to': f'n{i+1}'}
                 for i in range(0, 1100, 4)]
        self.editor.document = {'nodes': nodes, 'edges': edges}
        self.editor.history.reset(self.editor.document)
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        if self.editor._untitled_session is not None:
            self.editor._untitled_session.discard()
            self.editor._untitled_session.close()
        self.editor.destroy()

    def test_tk_draws_visible_subset_and_restores_after_pan(self):
        self.editor.draw()
        first_count = len(self.editor.canvas.find_all())
        self.assertLess(first_count, 250)
        self.assertGreater(first_count, 5)
        self.editor.viewport.pan(-4000, -900)
        self.editor.draw()
        second_count = len(self.editor.canvas.find_all())
        self.assertLess(second_count, 250)
        self.assertGreater(second_count, 5)
        self.assertEqual(len(self.editor.document['nodes']), 1200)
        self.assertEqual(len(self.editor.document['edges']), 275)

    def test_real_canvas_uses_selection_outline(self):
        self.editor.selected = 'n0'
        self.editor.selected_nodes = {'n0'}
        self.editor.draw()
        rects = self.editor.canvas.find_all()
        self.assertTrue(rects)
        self.assertTrue(any(self.editor.canvas.type(item) == 'rectangle'
                            and float(self.editor.canvas.itemcget(item, 'width')) >= 3
                            for item in rects))


if __name__ == '__main__':
    unittest.main()
