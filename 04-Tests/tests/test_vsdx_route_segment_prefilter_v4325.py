"""V43.25 regressions for segment-level prefiltering of static VSDX routes.

The spatial broad phase must include every possible blocker but must not scan
unrelated shapes lying only inside the route's overall bounding rectangle.
Author: Abdelhalim Talbi.
"""
import unittest
from unittest.mock import patch

from openvisio.routing import routing_scene
from openvisio.visio_route import active_visio_route, node_route_signature


def route_nodes(*, blocker=False, decoys=0):
    nodes = [
        {"id": "src", "x": 0.0, "y": 0.0, "width": 140.0, "height": 60.0, "shape": "server"},
        {"id": "dst", "x": 400.0, "y": 400.0, "width": 140.0, "height": 60.0, "shape": "storage"},
    ]
    if blocker:
        nodes.append({"id": "blocker", "x": 200.0, "y": 180.0,
                      "width": 30.0, "height": 30.0, "shape": "san-switch"})
    # These are inside the path's overall bounding rectangle but are at least
    # 16 px outside every route segment's clearance-expanded obstacle envelope.
    pockets = [(200.0, 35.0), (200.0, 70.0), (200.0, 105.0),
               (200.0, 140.0), (200.0, 230.0), (200.0, 270.0),
               (200.0, 310.0), (200.0, 350.0), (100.0, 250.0),
               (300.0, 100.0)]
    for i in range(decoys):
        x, y = pockets[i % len(pockets)]
        # Small jitter avoids creating duplicate nodes while remaining clear
        # of each segment and its 12-pixel broad-phase clearance.
        nodes.append({"id": f"decoy-{i}", "x": x + (i // len(pockets)) * 0.2,
                      "y": y, "width": 20.0, "height": 20.0, "shape": "server"})
    return nodes


def make_edge(nodes, points=None):
    by_id = {node["id"]: node for node in nodes}
    return {
        "id": "san-zigzag", "from": "src", "to": "dst", "routing": "orthogonal",
        "visio_route": {
            "schema": 1,
            "source": node_route_signature(by_id["src"]),
            "target": node_route_signature(by_id["dst"]),
            "points": points or [[70.0, 0.0], [140.0, 0.0], [140.0, 180.0],
                                  [260.0, 180.0], [260.0, 400.0], [330.0, 400.0]],
        },
    }


class StaticRouteSegmentPrefilterTests(unittest.TestCase):
    def test_meandering_route_does_not_scan_off_path_nodes_inside_its_bbox(self):
        nodes = route_nodes(decoys=1000)
        edge = make_edge(nodes)
        expected = [(70.0, 0.0), (140.0, 0.0), (140.0, 180.0),
                    (260.0, 180.0), (260.0, 400.0), (330.0, 400.0)]
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            actual = routing_scene(nodes).route_points(edge)
        self.assertEqual(actual, expected)
        candidates = spy.call_args.args[3]
        self.assertEqual({node["id"] for node in candidates}, {"src", "dst"})
        self.assertEqual(len(nodes), 1002)

    def test_blocker_touching_a_segment_is_kept_in_candidate_set(self):
        nodes = route_nodes(blocker=True, decoys=400)
        edge = make_edge(nodes)
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            actual = routing_scene(nodes).route_points(edge)
        candidates = spy.call_args.args[3]
        self.assertIn("blocker", {node["id"] for node in candidates})
        self.assertNotEqual(actual, [(70.0, 0.0), (140.0, 0.0), (140.0, 180.0),
                                     (260.0, 180.0), (260.0, 400.0), (330.0, 400.0)])

    def test_complex_valid_route_uses_bounded_full_scan_fallback(self):
        nodes = route_nodes()
        nodes.extend({"id": f"remote-{i}", "x": 20_000.0 + i * 50.0,
                      "y": 20_000.0, "width": 20.0, "height": 20.0,
                      "shape": "server"} for i in range(20))
        points = [[70.0, 0.0]]
        x, y = 70.0, 0.0
        for i in range(255):
            if i % 2 == 0:
                x += 0.5
            else:
                y += 0.5
            points.append([x, y])
        points.extend([[x, 400.0], [330.0, 400.0]])
        edge = make_edge(nodes, points)
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            actual = routing_scene(nodes).route_points(edge)
        self.assertEqual(actual, [(float(px), float(py)) for px, py in points])
        self.assertEqual(len(spy.call_args.args[3]), len(nodes))

    def test_diagonal_or_zero_length_metadata_uses_full_scan_fallback(self):
        for points in (
            [[70.0, 0.0], [140.0, 20.0], [330.0, 400.0]],
            [[70.0, 0.0], [70.0, 0.0], [330.0, 400.0]],
        ):
            with self.subTest(points=points):
                nodes = route_nodes(decoys=20)
                edge = make_edge(nodes, points)
                with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
                    routing_scene(nodes).route_points(edge)
                candidates = spy.call_args.args[3]
                self.assertEqual(len(candidates), len(nodes))


if __name__ == "__main__":
    unittest.main()
