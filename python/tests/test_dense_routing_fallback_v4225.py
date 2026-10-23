"""V42.25: a dense *candidate* must not reject other safe port orientations.

The fixtures are synthetic. These tests do not certify Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from openvisio import routing


def dense_fixture():
    # The horizontal corridor contains >32,000 grid cells; the bottom/top
    # candidate's window excludes these obstacles and has a valid safe path.
    nodes = [
        {'id': 'source', 'x': 0, 'y': 0},
        {'id': 'target', 'x': 600, 'y': 400},
    ]
    nodes.extend({
        'id': f'upper-{i}', 'x': 110 + i * 1.75,
        'y': -145 + i * .04, 'width': 4, 'height': 4,
    } for i in range(190))
    edge = {'id': 'link', 'from': 'source', 'to': 'target', 'routing': 'orthogonal'}
    return nodes, edge


class DenseRoutingFallbackTests(unittest.TestCase):
    def setUp(self):
        routing._scene_for_signature.cache_clear()
        routing.routing_scene._latest_scene = None

    def test_real_dense_horizontal_candidate_does_not_block_safe_vertical(self):
        nodes, edge = dense_fixture()
        with patch.object(routing, '_local_grid_path', wraps=routing._local_grid_path) as grid:
            points = routing.route_points(edge, nodes)
        self.assertGreaterEqual(grid.call_count, 2)
        self.assertEqual(points[0], (0.0, 30.0))
        self.assertEqual(points[-1], (600.0, 370.0))
        self.assertTrue(all(a[0] == b[0] or a[1] == b[1]
                            for a, b in zip(points, points[1:])))
        # No segment may cross a third-party equipment's clearance rectangle.
        rectangles = [routing._bounds(node) for node in nodes[2:]]
        self.assertTrue(all(not routing._blocked(a, b, rectangles)
                            for a, b in zip(points, points[1:])))

    def test_dense_failure_for_all_ports_remains_explicit_and_uncached(self):
        nodes = [{'id': 'source', 'x': 0, 'y': 0},
                 {'id': 'target', 'x': 600, 'y': 400}]
        edge = {'id': 'link', 'from': 'source', 'to': 'target', 'routing': 'orthogonal'}
        with patch.object(routing, '_local_grid_path',
                          side_effect=routing.RoutingDensityError('Routage orthogonal trop dense pour la limite de sécurité')) as grid:
            with self.assertRaisesRegex(routing.RoutingError, 'trop dense'):
                routing.route_points(edge, nodes)
        self.assertEqual(grid.call_count, 4)
        self.assertFalse(routing.routing_scene(nodes)._routes)

    def test_unexpected_routing_error_is_not_silently_swallowed(self):
        nodes = [{'id': 'source', 'x': 0, 'y': 0},
                 {'id': 'target', 'x': 600, 'y': 400}]
        edge = {'id': 'link', 'from': 'source', 'to': 'target', 'routing': 'orthogonal'}
        with patch.object(routing, '_local_grid_path',
                          side_effect=routing.RoutingError('unexpected routing error')):
            with self.assertRaisesRegex(routing.RoutingError, 'unexpected routing error'):
                routing.route_points(edge, nodes)

    def test_route_is_deterministic_after_cache_clear(self):
        nodes, edge = dense_fixture()
        warm = routing.route_points(edge, nodes)
        self.setUp()
        self.assertEqual(warm, routing.route_points(edge, nodes))

    def test_synthetic_vsdx_export_retains_safe_route(self):
        from openvisio.vsdx import export_vsdx
        nodes, edge = dense_fixture()
        expected = routing.route_points(edge, nodes)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'synthetic.vsdx'
            export_vsdx(target, {'nodes': nodes, 'edges': [edge]})
            with ZipFile(target) as archive:
                page = archive.read('visio/pages/page1.xml')
                self.assertIn(b'<', page)
                self.assertIn(b'OpenVisio connector', page)
        self.assertEqual(expected, routing.route_points(edge, nodes))


if __name__ == '__main__':
    unittest.main()
