"""V43.25 regression tests for spatially bounded static VSDX route validation.

The broad-phase index may only reduce candidates; exact route checks and
obstacle-aware fallback stay authoritative. Author: Abdelhalim Talbi.
"""
import unittest
from unittest.mock import patch

from openvisio.routing import routing_scene
from openvisio.visio_route import active_visio_route, node_route_signature


def make_nodes(remote_count=0, *, crossing=False):
    nodes = [
        {"id": "src", "x": 0.0, "y": 0.0, "width": 140.0, "height": 60.0, "shape": "server"},
        {"id": "dst", "x": 400.0, "y": 0.0, "width": 140.0, "height": 60.0, "shape": "storage"},
    ]
    if crossing:
        nodes.append({"id": "cross", "x": 200.0, "y": 0.0, "width": 36.0, "height": 36.0, "shape": "switch"})
    nodes.extend(
        {"id": f"remote-{i}", "x": 20_000.0 + i * 250.0, "y": 20_000.0,
         "width": 40.0, "height": 40.0, "shape": "server"}
        for i in range(remote_count)
    )
    return nodes


def make_edge(nodes):
    by_id = {node["id"]: node for node in nodes}
    return {
        "id": "san-a", "from": "src", "to": "dst", "routing": "orthogonal",
        "visio_route": {
            "schema": 1,
            "source": node_route_signature(by_id["src"]),
            "target": node_route_signature(by_id["dst"]),
            "points": [[70.0, 0.0], [330.0, 0.0]],
        },
    }


class StaticRouteSpatialPrefilterTests(unittest.TestCase):
    def test_remote_equipment_is_filtered_without_changing_preserved_path(self):
        nodes = make_nodes(1200)
        edge = make_edge(nodes)
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            actual = routing_scene(nodes).route_points(edge)
        self.assertEqual(actual, [(70.0, 0.0), (330.0, 0.0)])
        candidates = spy.call_args.args[3]
        self.assertLessEqual(len(candidates), 2)
        self.assertEqual(len(nodes), 1202)

    def test_obstacle_inside_route_envelope_is_not_filtered_out(self):
        nodes = make_nodes(800, crossing=True)
        edge = make_edge(nodes)
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            actual = routing_scene(nodes).route_points(edge)
        self.assertNotEqual(actual, [(70.0, 0.0), (330.0, 0.0)])
        candidates = spy.call_args.args[3]
        self.assertIn("cross", {node["id"] for node in candidates})
        self.assertLess(len(candidates), len(nodes))

    def test_malformed_route_uses_conservative_full_candidate_set(self):
        nodes = make_nodes(50)
        edge = make_edge(nodes)
        edge["visio_route"]["points"] = [[70.0, 0.0], [float("nan"), 0.0]]
        with patch("openvisio.visio_route.active_visio_route", wraps=active_visio_route) as spy:
            routing_scene(nodes).route_points(edge)
        candidates = spy.call_args.args[3]
        self.assertEqual(len(candidates), len(nodes))


if __name__ == "__main__":
    unittest.main()
