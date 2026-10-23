"""Real Tk regression: editable equipment dimensions and undo. Abdelhalim Talbi."""
import os
import tkinter as tk
import unittest
from openvisio.app import Editor


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'Requires real Tk display')
class VariableShapeGuiTests(unittest.TestCase):
    def setUp(self):
        self.editor = Editor()
        self.addCleanup(self._cleanup)
        self.editor.document = {'nodes': [{'id': 'storage', 'x': 180, 'y': 120,
                                            'width': 320, 'height': 120, 'label': 'SAN'}],
                                'edges': []}
        self.editor.history.reset(self.editor.document)
        self.editor.selected = 'storage'
        self.editor.selected_nodes = {'storage'}
        self.editor.draw()

    def _cleanup(self):
        if self.editor._untitled_session is not None:
            self.editor._untitled_session.discard()
            self.editor._untitled_session.close()
        self.editor.destroy()

    def test_edit_dimensions_in_actual_tk_dialog_and_undo(self):
        def edit_dialog():
            dialogs = [child for child in self.editor.winfo_children() if isinstance(child, tk.Toplevel)]
            self.assertEqual(len(dialogs), 1)
            dialog = dialogs[0]
            def descend(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from descend(child)
            entries = [widget for widget in descend(dialog) if isinstance(widget, tk.Entry)]
            for entry in entries:
                if entry.get() == '320':
                    entry.delete(0, 'end'); entry.insert(0, '400')
                if entry.get() == '120':
                    entry.delete(0, 'end'); entry.insert(0, '100')
            buttons = [widget for widget in descend(dialog) if isinstance(widget, tk.Button)]
            self.assertTrue(buttons)
            next(b for b in buttons if b.cget('text') == 'Enregistrer').invoke()
        self.editor.after(100, edit_dialog)
        self.editor.edit_properties()
        self.assertEqual(self.editor.document['nodes'][0]['width'], 400)
        self.assertEqual(self.editor.document['nodes'][0]['height'], 100)
        self.editor.undo()
        self.assertEqual(self.editor.document['nodes'][0]['width'], 320)
        self.editor.redo()
        self.assertEqual(self.editor.document['nodes'][0]['height'], 100)


if __name__ == '__main__':
    unittest.main()

@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'Requires real Tk display')
class TimerCleanupGuiTests(unittest.TestCase):
    def test_destroy_cancels_recovery_and_autosave_callbacks(self):
        editor = Editor()
        timer1, timer2 = editor._autosave_after_id, editor._startup_recovery_after_id
        self.assertIsNotNone(timer1)
        self.assertIsNotNone(timer2)
        editor.destroy()
        self.assertTrue(editor._destroying)
        self.assertIsNone(editor._autosave_after_id)
        self.assertIsNone(editor._startup_recovery_after_id)
