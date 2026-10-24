"""V43.07 regression: property edits must respect SAN layer locks.

The GUI filters locked objects, but pure edit commands are also used by
scripts and by dialogs opened before a layer is locked.
Author: Abdelhalim Talbi.
"""
from copy import deepcopy
import os
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openvisio.history import History
from openvisio.model import load, save, validate
from openvisio.property_commands import update_connection, update_equipment


def topology():
    return validate({
        'layers': [
            {'id': 'fabric-A', 'name': 'Fabric A', 'visible': True, 'locked': True},
            {'id': 'fabric-B', 'name': 'Fabric B', 'visible': True, 'locked': False},
        ],
        'nodes': [
            {'id': 'host-a', 'x': 90, 'y': 100, 'shape': 'server', 'layer': 'fabric-A'},
            {'id': 'array-a', 'x': 440, 'y': 100, 'shape': 'storage', 'layer': 'fabric-A'},
            {'id': 'host-b', 'x': 90, 'y': 300, 'shape': 'server', 'layer': 'fabric-B'},
            {'id': 'array-b', 'x': 440, 'y': 300, 'shape': 'storage', 'layer': 'fabric-B'},
        ],
        'edges': [
            {'id': 'fc-a', 'from': 'host-a', 'to': 'array-a', 'layer': 'fabric-A', 'protocol': 'FC'},
            {'id': 'fc-b', 'from': 'host-b', 'to': 'array-b', 'layer': 'fabric-B', 'protocol': 'FC'},
            {'id': 'fc-cross', 'from': 'host-a', 'to': 'array-b', 'layer': 'fabric-B', 'protocol': 'FC'},
        ],
    })


class PropertyLayerLockTests(unittest.TestCase):
    def setUp(self):
        self.original = topology()
        self.snapshot = deepcopy(self.original)

    def test_locked_equipment_rejects_label_and_size(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_equipment(self.original, 'host-a', {'label': 'modified'}, 'server', width=220)
        self.assertEqual(self.original, self.snapshot)

    def test_locked_edge_rejects_fc_port_change(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_connection(self.original, 'fc-a', {'protocol': 'FC', 'source_port': 'hba7'})
        self.assertEqual(self.original, self.snapshot)

    def test_unlocked_edge_with_locked_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_connection(self.original, 'fc-cross', {'protocol': 'FC', 'fabric': 'B'})
        self.assertEqual(self.original, self.snapshot)

    def test_unrelated_unlocked_fabric_remains_editable(self):
        changed = update_equipment(self.original, 'host-b', {'label': 'Host B'}, 'server')
        changed = update_connection(changed, 'fc-b', {'protocol': 'FC', 'fabric': 'B'})
        self.assertEqual(changed['nodes'][2]['label'], 'Host B')
        self.assertEqual(changed['edges'][1]['fabric'], 'B')
        self.assertEqual(self.original, self.snapshot)

    def test_unlock_then_edit_undo_redo_save_roundtrip(self):
        doc = deepcopy(self.original)
        doc['layers'][0]['locked'] = False
        history = History(doc)
        updated = update_equipment(doc, 'host-a', {'label': 'HBA host'}, 'server')
        updated = update_connection(updated, 'fc-a', {'protocol': 'FC', 'fabric': 'A'})
        self.assertTrue(history.record(updated))
        self.assertEqual(history.undo(), doc)
        self.assertEqual(history.redo(), updated)
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'fabric.openvisio'
            save(path, updated)
            self.assertEqual(load(path), updated)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1',
                     'Requires an actual Tk display (e.g. Xvfb)')
class PropertyLayerLockGuiTests(unittest.TestCase):
    def test_locked_equipment_dialog_is_not_opened(self):
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = topology()
            app.selected = 'host-a'
            with patch('tkinter.messagebox.showinfo') as info:
                app.edit_properties()
                info.assert_called_once()
            self.assertEqual(app.document, topology())
        finally:
            app.destroy()

    def test_locked_link_dialog_is_not_opened(self):
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = topology()
            app.selected_edge = 'fc-a'
            with patch('tkinter.messagebox.showinfo') as info:
                app.edit_selected_link()
                info.assert_called_once()
            self.assertEqual(app.document, topology())
        finally:
            app.destroy()


if __name__ == '__main__':
    unittest.main()
