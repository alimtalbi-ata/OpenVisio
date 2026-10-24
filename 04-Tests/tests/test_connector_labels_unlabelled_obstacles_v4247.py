"""Regression for visible but unlabelled SAN links. Author: Abdelhalim Talbi."""
import copy
import unittest
from openvisio.connector_labels import layout_connector_labels


class FixedScene:
    def __init__(self):
        self.calls = []

    def route_points(self, edge):
        self.calls.append(edge['id'])
        return {
            'labelled': [(0, 0), (600, 0)],
            'unlabelled': [(300, -200), (300, 200)],
        }[edge['id']]


class UnlabelledConnectorObstacles(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            {'id': 'a', 'x': 0, 'y': 0}, {'id': 'b', 'x': 600, 'y': 0},
            {'id': 'c', 'x': 300, 'y': -200}, {'id': 'd', 'x': 300, 'y': 200},
        ]
        self.edges = [
            {'id': 'labelled', 'from': 'a', 'to': 'b', 'protocol': 'FC'},
            {'id': 'unlabelled', 'from': 'c', 'to': 'd'},
        ]

    def test_label_avoids_unlabelled_crossing_link(self):
        original = copy.deepcopy((self.nodes, self.edges))
        scene = FixedScene()
        layout = layout_connector_labels(self.nodes, self.edges, scene=scene)
        self.assertIn('labelled', layout.labels)
        self.assertNotIn('unlabelled', layout.labels)
        self.assertEqual(set(scene.calls), {'labelled', 'unlabelled'})
        box = layout.labels['labelled'].bounds
        # The unlabelled vertical link at x=300 must not cross label bounds.
        self.assertFalse(box[0] < 302 and box[2] > 298
                         and box[1] < 202 and box[3] > -202, box)
        self.assertEqual((self.nodes, self.edges), original)

    def test_all_unlabelled_edges_skip_routing(self):
        scene = FixedScene()
        self.edges[0].pop('protocol')
        layout = layout_connector_labels(self.nodes, self.edges, scene=scene)
        self.assertEqual(layout.labels, {})
        self.assertEqual(scene.calls, [])

    def test_label_layout_stable_on_edge_reorder(self):
        first = layout_connector_labels(self.nodes, self.edges, scene=FixedScene())
        second = layout_connector_labels(self.nodes, list(reversed(self.edges)), scene=FixedScene())
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
