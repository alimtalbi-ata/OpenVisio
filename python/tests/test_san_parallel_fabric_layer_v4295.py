"""Regression: duplicated SAN paths preserve their Fabric layer.

The original bug caused a parallel path to escape layer visibility and audit.
Tests exercise the pure command, native persistence, history and the real Tk
multipath dialog (when OPENVISIO_GUI_TESTS=1 with an actual display).
Author: Abdelhalim Talbi.
"""
import os
import tempfile
import unittest
from pathlib import Path

from openvisio.commands import connect_equipment
from openvisio.history import History
from openvisio.layers import project_visible, set_locked, set_visibility
from openvisio.model import load, save, validate


def diagram():
    return validate({
        'nodes': [
            {'id': 'host', 'x': 90, 'y': 90, 'shape': 'server'},
            {'id': 'array', 'x': 430, 'y': 90, 'shape': 'storage'},
        ],
        'layers': [
            {'id': 'fabric-A', 'name': 'SAN Fabric A', 'visible': True, 'locked': False},
            {'id': 'fabric-B', 'name': 'SAN Fabric B', 'visible': True, 'locked': False},
        ],
        'edges': [{
            'id': 'fc-1', 'from': 'host', 'to': 'array', 'layer': 'fabric-A',
            'protocol': 'FC', 'fabric': 'A', 'source_port': 'hba0', 'target_port': 'fc0',
        }],
    })


def second_link(document, **options):
    return connect_equipment(document, 'host', 'array', ident='fc-2',
                             link={'protocol': 'FC', 'fabric': 'A',
                                   'source_port': 'hba1', 'target_port': 'fc1'},
                             **options)


class ParallelSanFabricLayerTests(unittest.TestCase):
    def test_parallel_path_stays_on_fabric_layer_and_hides_with_it(self):
        source = diagram()
        updated = second_link(source, layer='fabric-A')
        self.assertEqual(updated['edges'][1]['layer'], 'fabric-A')
        self.assertEqual(len(source['edges']), 1)
        hidden = project_visible(set_visibility(updated, 'fabric-A', False))
        self.assertEqual(hidden['edges'], [])
        self.assertEqual(len(updated['edges']), 2)

    def test_reject_locked_target_layer_without_modifying_document(self):
        locked = set_locked(diagram(), 'fabric-A', True)
        with self.assertRaisesRegex(ValueError, 'verrouillé'):
            second_link(locked, layer='fabric-A')
        self.assertEqual(len(locked['edges']), 1)

    def test_reject_unknown_target_layer(self):
        with self.assertRaisesRegex(ValueError, 'inexistant'):
            second_link(diagram(), layer='fabric-unknown')

    def test_save_load_and_undo_redo_keep_fabric_assignment(self):
        before = diagram()
        after = second_link(before, layer='fabric-A')
        history = History(before)
        self.assertTrue(history.record(after))
        self.assertEqual(len(history.undo()['edges']), 1)
        self.assertEqual(history.redo()['edges'][1]['layer'], 'fabric-A')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fabric.openvisio'
            save(path, after)
            restored = load(path)
            self.assertEqual(restored['edges'][1]['layer'], 'fabric-A')
            self.assertEqual(restored, after)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1',
                     'Requires a real Tk display (e.g. Xvfb)')
class ParallelSanFabricGuiTests(unittest.TestCase):
    def test_dialog_duplicate_inherits_selected_fabric_layer(self):
        import tkinter as tk
        from unittest.mock import patch
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = diagram()
            app.history = History(app.document)
            app.selected_edge = 'fc-1'
            app.update_idletasks()

            def confirm():
                dialogs = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
                self.assertEqual(len(dialogs), 1)
                dialog = dialogs[0]
                entries = [w for w in dialog.winfo_children() if isinstance(w, tk.Entry)]
                self.assertEqual(len(entries), 4)
                for entry, value in zip(entries, ('hba1', 'fc1', 'A', '32')):
                    entry.delete(0, 'end')
                    entry.insert(0, value)
                buttons = [w for w in dialog.winfo_children() if isinstance(w, tk.Button)]
                self.assertEqual(len(buttons), 1)
                buttons[0].invoke()

            app.after(100, confirm)
            with patch('tkinter.messagebox.showerror') as error:
                app.add_parallel_link()
                error.assert_not_called()
            self.assertEqual(app.document['edges'][1]['layer'], 'fabric-A')
            app.undo()
            self.assertEqual(len(app.document['edges']), 1)
            app.redo()
            self.assertEqual(app.document['edges'][1]['layer'], 'fabric-A')
        finally:
            app.destroy()


if __name__ == '__main__':
    unittest.main()
