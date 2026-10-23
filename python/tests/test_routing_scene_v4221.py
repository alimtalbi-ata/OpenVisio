"""V42.21: exact rectangle index, scene cache safety, editor/export integration.

All fixtures are synthetic; they are not evidence of Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import random
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from openvisio import routing
from openvisio.export import to_svg
from openvisio.render import draw_document, edge_at


class RectangleIndexTests(unittest.TestCase):
    def test_query_matches_bruteforce_for_random_rectangles(self):
        rng = random.Random(42121)
        entries = []
        for index in range(300):
            left = rng.randint(-5000, 5000)
            top = rng.randint(-5000, 5000)
            width = rng.choice((0, 10, 120, 6000))
            height = rng.choice((0, 15, 90, 3000))
            entries.append((str(index), (left, top, left + width, top + height)))
        index = routing.RectangleIndex(entries)
        for _ in range(300):
            x, y = rng.randint(-5200, 5200), rng.randint(-5200, 5200)
            w, h = rng.randint(0, 1000), rng.randint(0, 1000)
            window = (x, y, x + w, y + h)
            expected = {key for key, rect in entries if routing._intersects(rect, window)}
            actual = {key for key, _ in index.query_items(window)}
            self.assertEqual(actual, expected)

    def test_edge_touching_and_spanning_rectangles_are_not_dropped(self):
        entries = [('huge', (-100000, -100000, 100000, 100000)),
                   ('touch', (10, 0, 20, 20)), ('outside', (21, 0, 30, 20))]
        found = {key for key, _ in routing.RectangleIndex(entries).query_items((0, 0, 10, 10))}
        self.assertEqual(found, {'huge', 'touch'})

    def test_local_grid_uses_index_without_changing_route(self):
        nodes = [{'id': 'a', 'x': 0, 'y': 0},
                 {'id': 'b', 'x': 500, 'y': 0},
                 {'id': 'block', 'x': 250, 'y': 0}]
        rectangles = [(n['id'], routing._bounds(n)) for n in nodes]
        window = (-100, -200, 600, 200)
        start, finish = (83, 0), (417, 0)
        old = routing._local_grid_path(start, finish, [r for _, r in rectangles], window)
        new = routing._local_grid_path(start, finish, routing.RectangleIndex(rectangles), window)
        self.assertEqual(old, new)


class RoutingSceneTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [{'id': 'a', 'x': 0, 'y': 0},
                      {'id': 'b', 'x': 400, 'y': 0},
                      {'id': 'block', 'x': 200, 'y': 0}]
        self.edge = {'id': 'e', 'from': 'a', 'to': 'b', 'routing': 'orthogonal'}

    def test_scene_is_reused_for_identical_geometry(self):
        first = routing.routing_scene(self.nodes)
        self.assertIs(first, routing.routing_scene([dict(n) for n in self.nodes]))
        self.assertIs(first, routing.routing_scene({n['id']: n for n in self.nodes}))

    def test_returned_points_cannot_mutate_cached_route(self):
        original = routing.route_points(self.edge, self.nodes)
        modified = routing.route_points(self.edge, self.nodes)
        modified[0] = (123456, 123456)
        self.assertEqual(routing.route_points(self.edge, self.nodes), original)

    def test_mutating_geometry_invalidates_cache_and_changes_path(self):
        first_scene = routing.routing_scene(self.nodes)
        original = first_scene.route_points(self.edge)
        self.nodes[2]['y'] = 500
        second_scene = routing.routing_scene(self.nodes)
        self.assertIsNot(first_scene, second_scene)
        self.assertNotEqual(second_scene.route_points(self.edge), original)
        self.assertEqual(second_scene.route_points(self.edge), [(70, 0), (330, 0)])
        self.assertEqual(first_scene.route_points(self.edge), original)

    def test_width_height_and_edge_mode_invalidate_geometry(self):
        old = routing.route_points(self.edge, self.nodes)
        self.nodes[2]['height'] = 200
        new = routing.route_points(self.edge, self.nodes)
        self.assertNotEqual(old, new)
        straight = dict(self.edge, routing='straight')
        self.assertEqual(routing.route_points(straight, self.nodes), [(70, 0), (330, 0)])
        self.assertNotEqual(routing.route_points(straight, self.nodes), new)

    def test_route_is_calculated_only_once_per_scene(self):
        scene = routing.routing_scene(self.nodes)
        scene._routes.clear()
        with patch.object(routing, '_local_grid_path', wraps=routing._local_grid_path) as search:
            one = scene.route_points(self.edge)
            first_calls = search.call_count
            self.assertGreater(first_calls, 0)
            two = scene.route_points(self.edge)
            self.assertEqual(search.call_count, first_calls)
            self.assertEqual(one, two)

    def test_legacy_implicit_and_explicit_dimensions_share_geometry(self):
        implicit = routing.routing_scene(self.nodes)
        explicit = routing.routing_scene([{**n, 'width': 140.0, 'height': 60.0}
                                          for n in self.nodes])
        self.assertIs(implicit, explicit)

    def test_many_edges_reuse_scene_and_return_safe_orthogonal_paths(self):
        nodes = [{'id': f'n{r}_{c}', 'x': c * 180, 'y': r * 120}
                 for r in range(16) for c in range(25)]
        scene = routing.routing_scene(nodes)
        for r in range(12):
            for c in range(0, 20, 2):
                edge = {'from': f'n{r}_{c}', 'to': f'n{r}_{c+2}',
                        'routing': 'orthogonal'}
                points = scene.route_points(edge)
                self.assertTrue(all(a[0] == b[0] or a[1] == b[1]
                                    for a, b in zip(points, points[1:])))
                for a, b in zip(points[1:-2], points[2:-1]):
                    self.assertFalse(routing._blocked(a, b, scene.geometry()[1]))

    def test_canvas_hit_test_and_svg_share_route_after_move(self):
        class Canvas:
            def __init__(self): self.lines = []
            def delete(self, *_): pass
            def create_line(self, *args, **_): self.lines.append(args)
            def create_rectangle(self, *args, **_): pass
            def create_text(self, *args, **_): pass
        document = {'nodes': self.nodes, 'edges': [self.edge]}
        for block_y in (0, 500, 0):
            self.nodes[2]['y'] = block_y
            canvas = Canvas()
            draw_document(canvas, document)
            points = routing.route_points(self.edge, self.nodes)
            self.assertEqual(canvas.lines[0], tuple(v for p in points for v in p))
            svg = ET.fromstring(to_svg(document))
            if len(points) > 2:
                poly = svg.find('{http://www.w3.org/2000/svg}polyline')
                self.assertEqual(poly.attrib['points'], ' '.join(f'{x},{y}' for x, y in points))
            middle = points[len(points) // 2]
            self.assertEqual(edge_at(self.nodes, [self.edge], *middle)['id'], 'e')

    def test_random_topologies_produce_deterministic_paths(self):
        rng = random.Random(4221)
        for _ in range(30):
            nodes = [{'id': 'a', 'x': 0, 'y': 0},
                     {'id': 'b', 'x': 700, 'y': 0}]
            for i in range(15):
                nodes.append({'id': str(i), 'x': rng.randint(-150, 850),
                              'y': rng.randint(-400, 400),
                              'width': rng.randint(20, 130),
                              'height': rng.randint(20, 130)})
            try:
                path = routing.route_points(self.edge, nodes)
            except routing.RoutingError:
                continue
            self.assertEqual(path, routing.routing_scene(nodes).route_points(self.edge))
            self.assertTrue(all(a[0] == b[0] or a[1] == b[1]
                                for a, b in zip(path, path[1:])))


if __name__ == '__main__':
    unittest.main()
