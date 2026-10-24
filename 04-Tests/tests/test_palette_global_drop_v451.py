"""Palette drag release must be handled even outside the listbox."""
import unittest
from types import SimpleNamespace
from openvisio.app import Editor

class PaletteGlobalDropRegression(unittest.TestCase):
    def test_drag_to_canvas_creates_selected_equipment(self):
        app = Editor()
        try:
            app.update()
            app.shape_list.selection_clear(0, "end")
            app.shape_list.selection_set(app._palette_kinds.index("storage"))
            origin = SimpleNamespace(x_root=app.shape_list.winfo_rootx()+20, y_root=app.shape_list.winfo_rooty()+20)
            app._palette_drag_start(origin)
            target = SimpleNamespace(x_root=app.canvas.winfo_rootx()+250, y_root=app.canvas.winfo_rooty()+160)
            app._palette_drop(target)
            self.assertEqual(len(app.document["nodes"]), 1)
            self.assertEqual(app.document["nodes"][0]["shape"], "storage")
        finally:
            app.destroy()

    def test_click_without_drag_does_not_create_equipment(self):
        app = Editor()
        try:
            app.update()
            event = SimpleNamespace(x_root=app.shape_list.winfo_rootx()+20, y_root=app.shape_list.winfo_rooty()+20)
            app._palette_drag_start(event)
            app._palette_drop(event)
            self.assertEqual(len(app.document["nodes"]), 0)
        finally:
            app.destroy()
