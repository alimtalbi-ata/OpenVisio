"""V42.28: native group commands, data integrity and UI integration.
Synthetic examples, not real Microsoft Visio fidelity tests.
Author: Abdelhalim Talbi.
"""
import os
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy

from openvisio.group_commands import (group_members, group_selection,
                                      ungroup_selection, resize_group)
from openvisio.model import validate, save, load
from openvisio.commands import remove_selection
from openvisio.clipboard import copy_selection, paste_selection
from openvisio.history import History
from openvisio.layout import move_group


def sample():
    return {'nodes': [
        {'id': 'a', 'x': 100, 'y': 100, 'width': 100, 'height': 60, 'shape': 'server'},
        {'id': 'b', 'x': 300, 'y': 100, 'width': 100, 'height': 60, 'shape': 'storage'},
        {'id': 'c', 'x': 500, 'y': 100, 'shape': 'server'}],
        'edges': [{'id': 'ab', 'from': 'a', 'to': 'b'},
                  {'id': 'bc', 'from': 'b', 'to': 'c'}]}


class NativeGroupTests(unittest.TestCase):
    def test_create_preserves_geometry_and_connectors(self):
        original = sample()
        grouped, ident = group_selection(original, {'a', 'b'}, ident='g')
        self.assertEqual(ident, 'g')
        self.assertEqual(original, sample())
        self.assertEqual([n['id'] for n in grouped['nodes']], ['a', 'b', 'c', 'g'])
        self.assertEqual(group_members(grouped['nodes'], {'g'}), {'g', 'a', 'b'})
        self.assertEqual(grouped['edges'], original['edges'])
        self.assertEqual((grouped['nodes'][-1]['width'], grouped['nodes'][-1]['height']), (348, 108))

    def test_nested_groups_and_move_are_atomic(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='inner')
        doc, _ = group_selection(doc, {'inner', 'c'}, ident='outer')
        members = group_members(doc['nodes'], {'outer'})
        self.assertEqual(members, {'outer', 'inner', 'a', 'b', 'c'})
        before = {n['id']: (n['x'], n['y']) for n in doc['nodes']}
        self.assertTrue(move_group(doc['nodes'], members, 50, -30))
        for n in doc['nodes']:
            self.assertEqual((n['x'], n['y']), (before[n['id']][0]+50, before[n['id']][1]-30))
        validate(doc)

    def test_ungroup_preserves_nested_and_links(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='inner')
        doc, _ = group_selection(doc, {'inner', 'c'}, ident='outer')
        result = ungroup_selection(doc, {'outer'})
        self.assertEqual({n['id'] for n in result['nodes']}, {'inner', 'a', 'b', 'c'})
        self.assertNotIn('visio_group_parent', next(n for n in result['nodes'] if n['id'] == 'inner'))
        self.assertEqual(result['edges'], doc['edges'])
        self.assertEqual(next(n for n in result['nodes'] if n['id'] == 'a')['visio_group_parent'], 'inner')

    def test_ungroup_rejects_connected_group_without_data_loss(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        doc['edges'].append({'id': 'cg', 'from': 'c', 'to': 'g'})
        original = deepcopy(doc)
        with self.assertRaisesRegex(ValueError, 'connecté'):
            ungroup_selection(doc, {'g'})
        self.assertEqual(doc, original)

    def test_group_delete_cascades_and_preserves_unrelated(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        result = remove_selection(doc, {'g'})
        self.assertEqual([n['id'] for n in result['nodes']], ['c'])
        self.assertEqual(result['edges'], [])
        self.assertEqual(len(doc['nodes']), 4)

    def test_clipboard_copy_paste_remaps_hierarchy(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        payload = copy_selection(doc, {'g'})
        self.assertEqual({n['id'] for n in payload['nodes']}, {'g', 'a', 'b'})
        new_ids = paste_selection(doc, payload)
        self.assertEqual(len(new_ids), 3)
        pasted = [n for n in doc['nodes'] if n['id'] in new_ids]
        new_group = next(n for n in pasted if n['shape'] == 'visio-group')
        self.assertEqual({n['visio_group_parent'] for n in pasted if n['id'] != new_group['id']}, {new_group['id']})
        self.assertEqual(len(doc['edges']), 3)
        validate(doc)

    def test_group_resize_scales_children_and_dimensions(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        old = {n['id']: n for n in doc['nodes']}
        result = resize_group(doc, 'g', 696, 216)
        updated = {n['id']: n for n in result['nodes']}
        self.assertEqual(updated['g']['width'], 696)
        self.assertEqual(updated['a']['width'], 200)
        self.assertEqual(updated['b']['x']-updated['a']['x'], 400)
        self.assertEqual(updated['c'], old['c'])
        self.assertEqual(result['edges'], doc['edges'])

    def test_resize_failure_does_not_mutate(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        original = deepcopy(doc)
        with self.assertRaises(ValueError):
            resize_group(doc, 'g', float('nan'), 100)
        self.assertEqual(doc, original)

    def test_group_undo_redo_and_save_roundtrip(self):
        doc = sample()
        history = History(doc)
        grouped, _ = group_selection(doc, {'a', 'b'}, ident='g')
        history.record(grouped)
        self.assertEqual(history.undo(), doc)
        self.assertEqual(history.redo(), grouped)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'group.ovjson'
            save(path, grouped)
            self.assertEqual(load(path), grouped)

    def test_invalid_parent_missing_non_group_and_cycle(self):
        doc = sample()
        doc['nodes'][0]['visio_group_parent'] = 'missing'
        with self.assertRaises(ValueError):
            validate(doc)
        doc['nodes'][0]['visio_group_parent'] = 'b'
        with self.assertRaises(ValueError):
            validate(doc)
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        doc['nodes'][-1]['visio_group_parent'] = 'g'
        with self.assertRaises(ValueError):
            validate(doc)

    def test_assign_layer_moves_entire_group_and_rejects_isolated_child(self):
        from openvisio.layers import assign_nodes
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        doc['layers'] = [{'id': 'new', 'visible': True, 'locked': False}]
        with self.assertRaisesRegex(ValueError, 'parent'):
            assign_nodes(doc, {'a'}, 'new')
        result = assign_nodes(doc, {'g'}, 'new')
        self.assertEqual({n.get('layer') for n in result['nodes'] if n['id'] in {'g','a','b'}}, {'new'})
        self.assertNotIn('layer', next(n for n in result['nodes'] if n['id']=='c'))
        validate(result)

    def test_imported_vsdx_group_can_move_with_children(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 1, 1) + shp(3, 4, 1)))
        gid = 'visio-p1-s1'
        members = group_members(doc['nodes'], {gid})
        self.assertEqual(members, {'visio-p1-s1','visio-p1-s2','visio-p1-s3'})
        before = {n['id']: n['x'] for n in doc['nodes']}
        move_group(doc['nodes'], members, 45, 0)
        self.assertEqual({n['id']: n['x']-before[n['id']] for n in doc['nodes']}, {i:45 for i in members})
        validate(doc)

    def test_clipboard_partial_child_is_detached_safely(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='g')
        payload = copy_selection(doc, {'a'})
        self.assertEqual(len(payload['nodes']), 1)
        pasted = paste_selection(doc, payload)
        node = next(n for n in doc['nodes'] if n['id'] in pasted)
        self.assertNotIn('visio_group_parent', node)
        validate(doc)

    def test_layer_mismatch_and_unknown_ids_rejected(self):
        doc = sample()
        doc['layers'] = [{'id': 'x'}, {'id': 'y'}]
        doc['nodes'][0]['layer'] = 'x'
        doc['nodes'][1]['layer'] = 'y'
        with self.assertRaisesRegex(ValueError, 'même'):
            group_selection(doc, {'a', 'b'})
        with self.assertRaises(ValueError):
            group_selection(sample(), {'a', 'unknown'})

    def test_ungroup_multiple_levels(self):
        doc, _ = group_selection(sample(), {'a', 'b'}, ident='inner')
        doc, _ = group_selection(doc, {'inner', 'c'}, ident='outer')
        result = ungroup_selection(doc, {'outer', 'inner'})
        self.assertEqual(result, sample())


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'GUI needs Xvfb or Windows desktop')
class NativeGroupGuiTests(unittest.TestCase):
    def test_editor_group_move_undo_ungroup(self):
        from openvisio.app import Editor
        from types import SimpleNamespace
        editor = Editor()
        editor.withdraw()
        try:
            editor.document = sample()
            editor.history.reset(editor.document)
            editor.selected_nodes = {'a', 'b'}
            editor.selected = 'a'
            editor.group_selected()
            gid = editor.selected
            self.assertEqual(group_members(editor.document['nodes'], {gid}), {'a', 'b', gid})
            before = {n['id']: n['x'] for n in editor.document['nodes']}
            editor._drag_anchor = (0, 0)
            editor.snap_enabled = False
            editor.drag(SimpleNamespace(x=50, y=0))
            editor.end_drag(SimpleNamespace(state=0))
            after = {n['id']: n['x'] for n in editor.document['nodes']}
            self.assertAlmostEqual(after['a']-before['a'], 50)
            self.assertAlmostEqual(after['b']-before['b'], 50)
            editor.undo()
            self.assertEqual(next(n['x'] for n in editor.document['nodes'] if n['id']=='a'), 100)
            editor.redo()
            self.assertEqual(next(n['x'] for n in editor.document['nodes'] if n['id']=='a'), 150)
            editor.selected = gid
            editor.selected_nodes = {gid}
            editor.ungroup_selected()
            self.assertEqual({n['id'] for n in editor.document['nodes']}, {'a','b','c'})
        finally:
            editor.destroy()


if __name__ == '__main__':
    unittest.main()
