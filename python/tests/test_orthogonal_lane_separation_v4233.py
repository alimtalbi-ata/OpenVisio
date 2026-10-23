"""V42.33: obstacle-aware orthogonal SAN lane separation, no unsafe fallback.

Synthetic geometry only. Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from openvisio.parallel_geometry import display_edges
from openvisio.lane_clearance import lane_clearance, expanded_intermediate_bounds
from openvisio.routing import (RoutingError, _blocked, route_points,
                               routing_scene, _bounds)
from openvisio.render import edge_at
from openvisio.export import to_svg
from openvisio.vsdx import export_vsdx
from openvisio.vsdx_fidelity import audit_public_vsdx
from openvisio.model import validate


def sample():
    nodes = [
        {'id': 'esxi', 'x': 0, 'y': 0, 'label': 'ESXi', 'shape': 'server'},
        {'id': 'flash', 'x': 400, 'y': 0, 'label': 'Flash', 'shape': 'storage'},
        {'id': 'obstacle', 'x': 200, 'y': 0, 'width': 140,
         'height': 90, 'label': 'Fabric switch', 'shape': 'san-switch'},
    ]
    edges = [
        {'id': 'fc-%d' % i, 'from': 'esxi', 'to': 'flash',
         'protocol': 'FC', 'source_port': 'hba%d' % i,
         'target_port': 'ct%d' % i, 'fabric': 'F%d' % i,
         'routing': 'orthogonal'} for i in range(4)
    ]
    return validate({'nodes': nodes, 'edges': edges})


class OrthogonalLaneTests(unittest.TestCase):
    def test_clearance_policy_is_bounded_and_validated(self):
        self.assertEqual(lane_clearance(-24), 12)
        self.assertEqual(lane_clearance(8), 4)
        self.assertEqual(lane_clearance(1000), 12)
        with self.assertRaises(ValueError):
            lane_clearance(float('nan'))

    def test_attachment_equipment_is_never_inflated(self):
        rect = (-10, -10, 10, 10)
        self.assertEqual(expanded_intermediate_bounds('a', rect, 'a', 'b', 4), rect)
        self.assertEqual(expanded_intermediate_bounds('b', rect, 'a', 'b', 4), rect)
        self.assertEqual(expanded_intermediate_bounds('c', rect, 'a', 'b', 4), (-14, -14, 14, 14))

    def test_four_lanes_have_distinct_safe_central_trunks(self):
        doc = sample()
        routes = [route_points(e, doc['nodes'])
                  for e in display_edges(doc['edges'], doc['nodes'])]
        trunks = [next((a[1] for a, b in zip(points, points[1:])
                        if a[1] == b[1] and abs(a[0] - b[0]) > 200), None)
                  for points in routes]
        self.assertEqual(trunks, [-69.0, -61.0, 61.0, 69.0])
        self.assertEqual(len(set(trunks)), 4)
        obstacle = _bounds(doc['nodes'][2])
        for points in routes:
            self.assertTrue(all(not _blocked(a, b, [obstacle])
                                for a, b in zip(points, points[1:])))

    def test_selection_on_separate_trunks(self):
        doc = sample()
        for edge in display_edges(doc['edges'], doc['nodes']):
            route = route_points(edge, doc['nodes'])
            middle = next((a, b) for a, b in zip(route, route[1:])
                          if a[1] == b[1] and abs(a[0] - b[0]) > 200)
            point = ((middle[0][0] + middle[1][0]) / 2, middle[0][1])
            self.assertEqual(edge_at(doc['nodes'], doc['edges'], *point, tolerance=2)['id'], edge['id'])

    def test_svg_and_vsdx_public_export_still_valid(self):
        doc = sample()
        svg = ET.fromstring(to_svg(doc))
        self.assertEqual(len(svg.findall('{http://www.w3.org/2000/svg}polyline')), 4)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'san.vsdx'
            export_vsdx(path, doc)
            self.assertEqual(audit_public_vsdx(path, doc)['status'], 'PASS')
            with ZipFile(path) as archive:
                self.assertIn('visio/pages/page1.xml', archive.namelist())

    def test_safe_base_route_is_used_if_separation_fails(self):
        doc = sample()
        edge = display_edges(doc['edges'], doc['nodes'])[0]
        from openvisio import routing
        original = routing._route_points_in_scene
        attempts = []
        def fallback(candidate, scene, **kwargs):
            attempts.append(kwargs.get('extra_clearance', 0))
            if kwargs.get('extra_clearance', 0):
                raise RoutingError('simulated narrow corridor')
            return original(candidate, scene, **kwargs)
        routing._scene_for_signature.cache_clear()
        with patch.object(routing, '_route_points_in_scene', side_effect=fallback):
            route = routing.route_points(edge, doc['nodes'])
        self.assertEqual(attempts, [12.0, 0])
        self.assertTrue(route)

    def test_lane_routes_not_inherited_across_geometry_edits(self):
        doc = sample()
        edge = display_edges(doc['edges'], doc['nodes'])[0]
        first = routing_scene(doc['nodes'])
        first.route_points(edge)
        changed = [dict(n) for n in doc['nodes']]
        changed[2]['y'] += 10
        second = routing_scene(changed)
        self.assertNotIn((edge['from'], edge['to'], 'orthogonal', edge['_lane_offset']), second._routes)


if __name__ == '__main__':
    unittest.main()
