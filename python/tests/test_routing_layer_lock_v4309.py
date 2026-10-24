"""V43.09: headless routing changes respect locked SAN fabrics.

Synthetic FC diagrams only; not Microsoft Visio Desktop fidelity evidence.
Author: Abdelhalim Talbi.
"""
import copy
import os
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

from openvisio.history import History
from openvisio.model import load, save, validate
from openvisio.routing import set_edge_routing


def topology():
    return validate({
        'layers': [
            {'id': 'locked', 'name': 'SAN Fabric A', 'locked': True},
            {'id': 'work', 'name': 'SAN Fabric B', 'locked': False},
        ],
        'nodes': [
            {'id': 'h1', 'x': 0, 'y': 0, 'shape': 'server', 'layer': 'work'},
            {'id': 'a1', 'x': 400, 'y': 0, 'shape': 'storage', 'layer': 'work'},
            {'id': 'h2', 'x': 0, 'y': 250, 'shape': 'server', 'layer': 'locked'},
            {'id': 'a2', 'x': 400, 'y': 250, 'shape': 'storage', 'layer': 'work'},
        ],
        'edges': [
            {'id': 'fc-a', 'from': 'h1', 'to': 'a1', 'layer': 'locked',
             'protocol': 'FC', 'source_port': 'HBA0', 'target_port': 'P0'},
            {'id': 'fc-b', 'from': 'h1', 'to': 'a1', 'layer': 'work',
             'protocol': 'FC', 'source_port': 'HBA1', 'target_port': 'P1'},
            {'id': 'fc-cross', 'from': 'h2', 'to': 'a2', 'layer': 'work',
             'protocol': 'FC', 'source_port': 'HBA2', 'target_port': 'P2'},
        ],
    })


class RoutingLayerLockTests(unittest.TestCase):
    def setUp(self):
        self.doc = topology()
        self.before = copy.deepcopy(self.doc)

    def test_protected_link_rejects_orthogonal_routing(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            set_edge_routing(self.doc, 'fc-a', 'orthogonal')
        self.assertEqual(self.doc, self.before)

    def test_protected_link_rejects_straight_routing(self):
        self.doc['edges'][0]['routing'] = 'orthogonal'
        original = copy.deepcopy(self.doc)
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            set_edge_routing(self.doc, 'fc-a', 'straight')
        self.assertEqual(self.doc, original)

    def test_unlocked_link_with_locked_endpoint_rejected(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            set_edge_routing(self.doc, 'fc-cross', 'orthogonal')
        self.assertEqual(self.doc, self.before)

    def test_parallel_unlocked_path_can_route_independently(self):
        updated = set_edge_routing(self.doc, 'fc-b', 'orthogonal')
        self.assertEqual(updated['edges'][1]['routing'], 'orthogonal')
        self.assertNotIn('routing', updated['edges'][0])
        self.assertEqual(self.doc, self.before)

    def test_unlock_and_relock_controls_headless_edit(self):
        unlocked = copy.deepcopy(self.doc)
        unlocked['layers'][0]['locked'] = False
        changed = set_edge_routing(unlocked, 'fc-a', 'orthogonal')
        self.assertEqual(changed['edges'][0]['routing'], 'orthogonal')
        changed['layers'][0]['locked'] = True
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            set_edge_routing(changed, 'fc-a', 'straight')

    def test_unlocked_routing_undo_redo_and_native_save(self):
        history = History(self.doc)
        updated = set_edge_routing(self.doc, 'fc-b', 'orthogonal')
        self.assertTrue(history.record(updated))
        self.assertEqual(history.undo(), self.before)
        self.assertEqual(history.redo(), updated)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fabric.openvisio'
            save(path, updated)
            self.assertEqual(load(path), updated)

    def test_unknown_edge_remains_rejected_without_mutation(self):
        with self.assertRaisesRegex(ValueError, 'introuvable'):
            set_edge_routing(self.doc, 'missing', 'orthogonal')
        self.assertEqual(self.doc, self.before)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1',
                     'Requires Tk display (e.g. Xvfb)')
class RoutingLayerLockGuiTests(unittest.TestCase):
    def test_editor_blocks_locked_link_but_routes_parallel_working_link(self):
        from openvisio.app import Editor
        editor = Editor()
        try:
            editor.document = topology()
            editor.history.reset(editor.document)
            editor.selected_edge = 'fc-a'
            with patch('tkinter.messagebox.showinfo') as info:
                editor.toggle_selected_edge_routing()
                info.assert_called_once()
            self.assertNotIn('routing', editor.document['edges'][0])
            editor.selected_edge = 'fc-b'
            editor.toggle_selected_edge_routing()
            self.assertEqual(editor.document['edges'][1]['routing'], 'orthogonal')
            self.assertNotIn('routing', editor.document['edges'][0])
        finally:
            editor.destroy()


if __name__ == '__main__':
    unittest.main()
