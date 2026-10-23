"""V42.24 conservative incremental routing after geometry edits.

Synthetic test fixtures; NOT a Microsoft Visio fidelity qualification.
Author: Abdelhalim Talbi.
"""
import random
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from unittest.mock import patch

from openvisio import routing


def scene_fixture():
    nodes = [
        {'id': 'a', 'x': 0, 'y': 0},
        {'id': 'b', 'x': 600, 'y': 0},
        {'id': 'obstacle', 'x': 300, 'y': 0},
        {'id': 'distant', 'x': 300, 'y': 1800},
        {'id': 'top', 'x': 300, 'y': -1800},
        {'id': 'left', 'x': -2000, 'y': 0},
        {'id': 'right', 'x': 2000, 'y': 0},
    ]
    edges = [
        {'id': 'ab', 'from': 'a', 'to': 'b', 'routing': 'orthogonal'},
        {'id': 'ad', 'from': 'a', 'to': 'distant', 'routing': 'straight'},
        {'id': 'bd', 'from': 'b', 'to': 'distant', 'routing': 'orthogonal'},
    ]
    return nodes, edges


class IncrementalRoutingTests(unittest.TestCase):
    def setUp(self):
        routing._scene_for_signature.cache_clear()
        routing.routing_scene._latest_scene = None

    def test_distant_obstacle_move_reuses_orthogonal_route_without_search(self):
        nodes, edges = scene_fixture()
        original_scene = routing.routing_scene(nodes)
        expected = original_scene.route_points(edges[0])
        # Move a non-endpoint obstacle outside every previously searched region.
        nodes[3]['x'] += 50
        with patch.object(routing, '_local_grid_path', wraps=routing._local_grid_path) as search:
            new_scene = routing.routing_scene(nodes)
            self.assertIsNot(new_scene, original_scene)
            self.assertIn(('a', 'b', 'orthogonal'), new_scene._routes)
            self.assertEqual(new_scene.route_points(edges[0]), expected)
            self.assertEqual(search.call_count, 0)

    def test_changed_endpoint_is_always_recomputed(self):
        nodes, edges = scene_fixture()
        routing.routing_scene(nodes).route_points(edges[0])
        nodes[0]['x'] += 25
        new_scene = routing.routing_scene(nodes)
        self.assertNotIn(('a', 'b', 'orthogonal'), new_scene._routes)
        self.assertNotEqual(new_scene.route_points(edges[0])[0], (70, 0))

    def test_changed_obstacle_in_search_envelope_invalidates_route(self):
        nodes, edges = scene_fixture()
        original = routing.routing_scene(nodes).route_points(edges[0])
        nodes[2]['y'] = 140  # Old obstacle intersects the search envelope.
        new_scene = routing.routing_scene(nodes)
        self.assertNotIn(('a', 'b', 'orthogonal'), new_scene._routes)
        self.assertNotEqual(original, new_scene.route_points(edges[0]))

    def test_new_obstacle_in_search_envelope_invalidates_route(self):
        nodes, edges = scene_fixture()
        nodes[2]['y'] = 400
        initial = routing.routing_scene(nodes).route_points(edges[0])
        nodes[2]['y'] = 0
        new_scene = routing.routing_scene(nodes)
        self.assertNotIn(('a', 'b', 'orthogonal'), new_scene._routes)
        self.assertNotEqual(initial, new_scene.route_points(edges[0]))

    def test_global_bounds_change_prevents_reuse(self):
        nodes, edges = scene_fixture()
        routing.routing_scene(nodes).route_points(edges[0])
        nodes[-1]['x'] += 500
        new_scene = routing.routing_scene(nodes)
        self.assertEqual(len(new_scene._routes), 0)

    def test_added_removed_or_reordered_nodes_disable_reuse(self):
        for action in ('add', 'remove', 'reorder'):
            with self.subTest(action=action):
                self.setUp()
                nodes, edges = scene_fixture()
                routing.routing_scene(nodes).route_points(edges[0])
                if action == 'add':
                    nodes.append({'id': 'extra', 'x': 300, 'y': 2000})
                elif action == 'remove':
                    nodes.pop(3)
                else:
                    nodes[3], nodes[4] = nodes[4], nodes[3]
                self.assertFalse(routing.routing_scene(nodes)._routes)

    def test_straight_routes_depend_only_on_endpoints(self):
        nodes, edges = scene_fixture()
        original = routing.routing_scene(nodes).route_points(edges[1])
        nodes[2]['y'] = 100
        new_scene = routing.routing_scene(nodes)
        self.assertIn(('a', 'distant', 'straight'), new_scene._routes)
        self.assertEqual(new_scene.route_points(edges[1]), original)

    def test_inherited_route_is_detached_from_callers(self):
        nodes, edges = scene_fixture()
        routing.routing_scene(nodes).route_points(edges[0])
        nodes[3]['x'] += 25
        new_scene = routing.routing_scene(nodes)
        original = new_scene.route_points(edges[0])
        changed = new_scene.route_points(edges[0])
        changed[0] = (999, 999)
        self.assertEqual(new_scene.route_points(edges[0]), original)

    def test_svg_and_vsdx_geometry_equal_after_incremental_reuse(self):
        from openvisio.export import to_svg
        from openvisio.vsdx import export_vsdx, import_vsdx
        nodes, edges = scene_fixture()
        routing.routing_scene(nodes).route_points(edges[0])
        nodes[3]['x'] += 25
        document = {'nodes': nodes, 'edges': edges}
        warm_svg = to_svg(document)
        with tempfile.TemporaryDirectory() as tmp:
            warm_file = Path(tmp) / 'warm.vsdx'
            cold_file = Path(tmp) / 'cold.vsdx'
            export_vsdx(warm_file, document)
            routing._scene_for_signature.cache_clear()
            routing.routing_scene._latest_scene = None
            cold_svg = to_svg(document)
            export_vsdx(cold_file, document)
            self.assertEqual(warm_svg, cold_svg)
            with ZipFile(warm_file) as warm, ZipFile(cold_file) as cold:
                self.assertEqual(warm.read('visio/pages/page1.xml'),
                                 cold.read('visio/pages/page1.xml'))
            self.assertEqual(import_vsdx(warm_file), import_vsdx(cold_file))

    def test_differential_cold_route_random_nonendpoint_edits(self):
        rng = random.Random(4224)
        for index in range(35):
            with self.subTest(case=index):
                self.setUp()
                nodes, edges = scene_fixture()
                # Move either central or distant obstacle, possibly resizing.
                which = rng.choice((2, 3, 4))
                original_scene = routing.routing_scene(nodes)
                original_scene.route_points(edges[0])
                nodes[which]['x'] += rng.randint(-150, 150)
                nodes[which]['y'] += rng.randint(-150, 150)
                nodes[which]['width'] = rng.randint(80, 180)
                warm_scene = routing.routing_scene(nodes)
                try:
                    warm = warm_scene.route_points(edges[0])
                except routing.RoutingError:
                    warm = 'no-safe-path'
                cold_nodes = deepcopy(nodes)
                routing._scene_for_signature.cache_clear()
                routing.routing_scene._latest_scene = None
                try:
                    cold = routing.routing_scene(cold_nodes).route_points(edges[0])
                except routing.RoutingError:
                    cold = 'no-safe-path'
                self.assertEqual(warm, cold)


if __name__ == '__main__':
    unittest.main()
