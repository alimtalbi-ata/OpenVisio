"""V43.08: a protected FC path cannot be rerouted through endpoint geometry edits.

Synthetic topologies, not Microsoft Visio desktop interoperability evidence.
Author: Abdelhalim Talbi.
"""
import os
import unittest
from copy import deepcopy
from types import SimpleNamespace

from openvisio.model import validate
from openvisio.property_commands import update_equipment


def topology():
    return validate({
        'layers': [{'id': 'protected', 'name': 'Protected FC', 'locked': True},
                   {'id': 'working', 'name': 'Working', 'locked': False}],
        'nodes': [
            {'id': 'h1', 'x': 100, 'y': 120, 'shape': 'server', 'layer': 'working', 'label': 'Host'},
            {'id': 's1', 'x': 460, 'y': 120, 'shape': 'storage', 'layer': 'working', 'label': 'Array'},
            {'id': 'h2', 'x': 100, 'y': 330, 'shape': 'server', 'layer': 'working'},
            {'id': 's2', 'x': 460, 'y': 330, 'shape': 'storage', 'layer': 'working'},
        ],
        'edges': [
            {'id': 'fc-protected', 'from': 'h1', 'to': 's1', 'layer': 'protected',
             'protocol': 'FC', 'source_port': 'HBA0', 'target_port': 'P1', 'fabric': 'A'},
            {'id': 'fc-working', 'from': 'h2', 'to': 's2', 'layer': 'working',
             'protocol': 'FC', 'source_port': 'HBA1', 'target_port': 'P2', 'fabric': 'B'},
        ],
    })


class ProtectedConnectorGeometryTests(unittest.TestCase):
    def setUp(self):
        self.doc = topology()
        self.original = deepcopy(self.doc)

    def test_locked_link_endpoint_resize_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_equipment(self.doc, 'h1', {'label': 'Host'}, 'server', width=220)
        self.assertEqual(self.doc, self.original)

    def test_locked_link_endpoint_shape_change_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_equipment(self.doc, 'h1', {'label': 'Host'}, 'storage')
        self.assertEqual(self.doc, self.original)

    def test_metadata_change_without_geometry_change_allowed(self):
        updated = update_equipment(self.doc, 'h1', {'label': 'Renamed host'}, 'server',
                                   width=140, height=60)
        self.assertEqual(updated['nodes'][0]['label'], 'Renamed host')
        self.assertEqual(self.doc, self.original)

    def test_unprotected_fabric_resize_allowed(self):
        updated = update_equipment(self.doc, 'h2', {'label': 'Host 2'}, 'server', width=220)
        self.assertEqual(updated['nodes'][2]['width'], 220)
        self.assertEqual(self.doc, self.original)

    def test_locked_endpoint_of_unlocked_link_also_protected(self):
        document = deepcopy(self.doc)
        document['edges'][0]['layer'] = 'working'
        document['nodes'][1]['layer'] = 'protected'
        with self.assertRaisesRegex(ValueError, 'verrouill'):
            update_equipment(document, 'h1', {'label': 'Host'}, 'server', width=200)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1',
                     'Requires real Tk display, e.g. Xvfb')
class ProtectedConnectorGeometryGuiTests(unittest.TestCase):
    def test_drag_protected_endpoint_refused_but_unrelated_endpoint_moves(self):
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = topology()
            app.history.reset(app.document)
            app.snap_enabled = False
            app.selected_nodes = {'h1'}
            app.selected = 'h1'
            app._drag_anchor = (100, 120)
            x, y = app.viewport.screen(150, 120)
            app.drag(SimpleNamespace(x=x, y=y))
            self.assertEqual(app.document['nodes'][0]['x'], 100)
            app.selected_nodes = {'h2'}
            app.selected = 'h2'
            app._drag_anchor = (100, 330)
            x, y = app.viewport.screen(150, 330)
            app.drag(SimpleNamespace(x=x, y=y))
            self.assertEqual(app.document['nodes'][2]['x'], 150)
        finally:
            app.destroy()

    def test_align_does_not_move_protected_endpoint(self):
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = topology()
            app.history.reset(app.document)
            app.document['nodes'][2]['x'] = 300
            app.selected_nodes = {'h1', 'h2'}
            app.align_selection('x')
            self.assertEqual(app.document['nodes'][0]['x'], 100)
            self.assertEqual(app.document['nodes'][2]['x'], 300)
        finally:
            app.destroy()


if __name__ == '__main__':
    unittest.main()
