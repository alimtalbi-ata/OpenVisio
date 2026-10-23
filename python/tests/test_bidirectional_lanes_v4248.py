"""V42.48: two-way SAN corridors remain individually visible and selectable.

Synthetic diagrams only; no Microsoft Visio certification. Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.parallel_geometry import display_edges
from openvisio.model import validate, save, load
from openvisio.render import edge_at
from openvisio.routing import routing_scene
from openvisio.export import to_svg
from openvisio.vsdx import export_vsdx, import_vsdx, V
from openvisio.vsdx_fidelity import audit_public_vsdx


def bidirectional(orthogonal=False):
    return validate({
        'nodes': [
            {'id': 'host', 'x': 0, 'y': 0, 'shape': 'server'},
            {'id': 'array', 'x': 400, 'y': 0, 'shape': 'storage'},
        ],
        'edges': [
            {'id': 'fc-a', 'from': 'host', 'to': 'array',
             'protocol': 'FC', 'source_port': 'hba0', 'target_port': 'ct0',
             'fabric': 'A', **({'routing': 'orthogonal'} if orthogonal else {})},
            {'id': 'fc-b', 'from': 'array', 'to': 'host',
             'protocol': 'FC', 'source_port': 'ct1', 'target_port': 'hba1',
             'fabric': 'B', **({'routing': 'orthogonal'} if orthogonal else {})},
        ]})


class BidirectionalLaneTests(unittest.TestCase):
    def test_reverse_direction_edges_have_distinct_stable_lanes(self):
        doc = bidirectional()
        original = copy.deepcopy(doc)
        first = {e['id']: e['_lane_offset'] for e in display_edges(doc['edges'], doc['nodes'])}
        second = {e['id']: e['_lane_offset'] for e in display_edges(doc['edges'][::-1], doc['nodes'])}
        self.assertEqual(first, second)
        self.assertEqual(sorted(first.values()), [-8.0, 8.0])
        self.assertEqual(doc, original)

    def test_two_reverse_routes_are_individually_hit_testable(self):
        doc = bidirectional()
        scene = routing_scene(doc['nodes'])
        paths = {}
        for edge in display_edges(doc['edges'], doc['nodes']):
            route = scene.route_points(edge)
            paths[edge['id']] = route
            mid = ((route[0][0] + route[-1][0])/2, (route[0][1] + route[-1][1])/2)
            self.assertEqual(edge_at(doc['nodes'], doc['edges'], *mid, tolerance=3)['id'], edge['id'])
        self.assertNotEqual(set(paths['fc-a']), set(paths['fc-b']))

    def test_orthogonal_reverse_routes_remain_distinct(self):
        doc = bidirectional(orthogonal=True)
        scene = routing_scene(doc['nodes'])
        routes = [scene.route_points(e) for e in display_edges(doc['edges'], doc['nodes'])]
        self.assertNotEqual(set(routes[0]), set(routes[1]))
        for route in routes:
            self.assertTrue(all(a[0] == b[0] or a[1] == b[1] for a,b in zip(route, route[1:])))

    def test_svg_public_connectors_are_separated(self):
        doc = bidirectional()
        root = ET.fromstring(to_svg(doc))
        lines = root.findall('{http://www.w3.org/2000/svg}line')
        self.assertEqual(len(lines), 2)
        self.assertNotEqual(lines[0].get('y1'), lines[1].get('y1'))

    def test_vsdx_public_geometry_and_private_roundtrip(self):
        doc = bidirectional()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'SAN bidirectionnel.vsdx'
            export_vsdx(p, doc)
            self.assertEqual(audit_public_vsdx(p, doc)['status'], 'PASS')
            self.assertEqual(import_vsdx(p), doc)
            with ZipFile(p) as archive:
                root = ET.fromstring(archive.read('visio/pages/page1.xml'))
            connectors = [s for s in root.findall(f'.//{{{V}}}Shape')
                          if s.get('NameU') == 'OpenVisio connector']
            self.assertEqual(len(connectors), 2)
            y = [float(next(c.get('V') for c in s.findall(f'{{{V}}}Cell')
                            if c.get('N') == 'BeginY')) for s in connectors]
            self.assertNotEqual(*y)

    def test_ovjson_does_not_persist_display_lanes(self):
        doc = bidirectional()
        display_edges(doc['edges'], doc['nodes'])
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'topology.ovjson'
            save(p, doc)
            self.assertNotIn('_lane_offset', p.read_text())
            self.assertEqual(load(p), doc)


if __name__ == '__main__':
    unittest.main()
