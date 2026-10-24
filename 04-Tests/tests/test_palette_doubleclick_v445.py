"""Canvas double-click uses the selected equipment type."""
import unittest
from types import SimpleNamespace
from openvisio.app import Editor

class PaletteDoubleClickTests(unittest.TestCase):
    def test_canvas_doubleclick_uses_palette_kind(self):
        app=Editor()
        try:
            app.update()
            app.shape_list.selection_clear(0,"end")
            app.shape_list.selection_set(app._palette_kinds.index("firewall"))
            x,y=app.viewport.screen(240,170)
            app.add_node(SimpleNamespace(x=x,y=y))
            self.assertEqual(app.document["nodes"][0]["shape"],"firewall")
        finally:
            app.destroy()
