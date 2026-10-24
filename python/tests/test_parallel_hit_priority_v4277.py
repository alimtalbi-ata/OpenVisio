"""V42.77: dense SAN lanes must be individually selectable in the editor.

Synthetic topology only; not a Microsoft Visio compatibility claim.
Author: Abdelhalim Talbi.
"""
import unittest
from openvisio.model import validate
from openvisio.parallel_geometry import display_edges
from openvisio.render import edge_at
from openvisio.routing import routing_scene


def fabric(count=12):
    nodes = [
        {'id': 'esxi', 'x': 0, 'y': 0, 'shape': 'server'},
        {'id': 'array', 'x': 450, 'y': 0, 'shape': 'storage'},
    ]
    edges = [
        {'id': f'fc-{i:02d}', 'from': 'esxi', 'to': 'array',
         'source_port': f'vmhba{i}', 'target_port': f'ct{i}',
         'fabric': f'FAB-{i}', 'protocol': 'FC'}
        for i in range(count)
    ]
    return validate({'nodes': nodes, 'edges': edges})


class DenseSanSelectionTests(unittest.TestCase):
    def test_each_dense_parallel_path_can_be_selected_at_its_center(self):
        doc = fabric()
        scene = routing_scene(doc['nodes'])
        lanes = display_edges(doc['edges'], doc['nodes'])
        for lane in lanes:
            start, end = scene.route_points(lane)
            center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
            with self.subTest(edge=lane['id']):
                selected = edge_at(doc['nodes'], doc['edges'], *center, tolerance=9)
                self.assertIsNotNone(selected)
                self.assertEqual(selected['id'], lane['id'])

    def test_selection_tracks_nearest_path_not_last_drawn(self):
        doc = fabric(8)
        lanes = display_edges(doc['edges'], doc['nodes'])
        first = lanes[0]
        p, q = routing_scene(doc['nodes']).route_points(first)
        click = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.25)
        self.assertEqual(edge_at(doc['nodes'], doc['edges'], *click)['id'], first['id'])

    def test_exact_ties_preserve_topmost_draw_order(self):
        doc = fabric(2)
        self.assertEqual(edge_at(doc['nodes'], doc['edges'], 200, 0)['id'], 'fc-01')

    def test_click_outside_tolerance_returns_none(self):
        doc = fabric()
        # V43.04: metadata labels are clickable, so test a point outside both
        # the physical lanes and every displayed SAN caption.
        self.assertIsNone(edge_at(doc['nodes'], doc['edges'], 200, 500, tolerance=9))


if __name__ == '__main__':
    unittest.main()
