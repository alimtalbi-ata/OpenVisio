"""Real Tkinter integration for creating a second physical SAN path.
Requires Xvfb or real display; no simulated UI screenshot. Author: Abdelhalim Talbi.
"""
import os
import tkinter as tk
import unittest
from unittest.mock import patch
from openvisio.app import Editor
from openvisio.history import History
from openvisio.commands import connect_equipment


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'Requires real Tk display')
class GuiSanMultipathTests(unittest.TestCase):
    def test_dialog_creates_distinct_port_path_with_undo(self):
        base = {'nodes': [{'id': 'h', 'x': 80, 'y': 90, 'shape': 'server'},
                          {'id': 'a', 'x': 400, 'y': 90, 'shape': 'storage'}], 'edges': []}
        doc = connect_equipment(base, 'h', 'a', ident='fabric-A',
                                link={'protocol': 'FC', 'source_port': 'vmhba1',
                                      'target_port': 'ct0.fc1', 'fabric': 'A'})
        app = Editor()
        try:
            app.document = doc
            app.history = History(doc)
            app.selected_edge = 'fabric-A'
            app.update_idletasks()

            def populate_and_confirm():
                dialogs = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
                self.assertEqual(len(dialogs), 1)
                dialog = dialogs[0]
                entries = []
                buttons = []
                for child in dialog.winfo_children():
                    if isinstance(child, tk.Entry):
                        entries.append(child)
                    if isinstance(child, tk.Button):
                        buttons.append(child)
                # Port source, port cible, Fabric, Débit; protocol is an OptionMenu.
                self.assertEqual(len(entries), 4)
                for entry, value in zip(entries, ('vmhba2', 'ct1.fc1', 'B', '32')):
                    entry.delete(0, 'end')
                    entry.insert(0, value)
                self.assertEqual(len(buttons), 1)
                buttons[0].invoke()

            app.after(100, populate_and_confirm)
            with patch('tkinter.messagebox.showerror') as error:
                app.add_parallel_link()
                error.assert_not_called()
            self.assertEqual(len(app.document['edges']), 2)
            self.assertEqual(app.document['edges'][1]['source_port'], 'vmhba2')
            self.assertEqual(app.document['edges'][1]['fabric'], 'B')
            app.undo()
            self.assertEqual([e['id'] for e in app.document['edges']], ['fabric-A'])
        finally:
            app.destroy()


if __name__ == '__main__':
    unittest.main()
