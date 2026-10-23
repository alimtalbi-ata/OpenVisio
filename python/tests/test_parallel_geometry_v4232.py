"""V42.32: visible SAN multipath lanes and identical public export geometry.

All VSDX examples are synthetic. Author: Abdelhalim Talbi.
"""
import copy
import math
import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.parallel_geometry import display_edges
from openvisio.render import edge_at
from openvisio.routing import routing_scene, _blocked
from openvisio.connector_geometry import lane_endpoints
from openvisio.export import to_svg
from openvisio.model import validate, save, load
from openvisio.vsdx import export_vsdx, V
from openvisio.vsdx_fidelity import audit_public_vsdx


def doc(count=2, orthogonal=False):
    nodes = [
        {'id': 'host', 'x': 0, 'y': 0, 'label': 'ESXi', 'shape': 'server'},
        {'id': 'array', 'x': 400, 'y': 0, 'label': 'Array', 'shape': 'storage'},
    ]
    edges = [{'id': 'path-' + str(i), 'from': 'host', 'to': 'array',
              'protocol': 'FC', 'source_port': 'hba' + str(i),
              'target_port': 'ct' + str(i), 'fabric': 'FAB' + str(i),
              **({'routing': 'orthogonal'} if orthogonal else {})}
             for i in range(count)]
    return validate({'nodes': nodes, 'edges': edges})


class ParallelGeometryTests(unittest.TestCase):
    def test_lanes_separate_without_modifying_document(self):
        document = doc()
        before = copy.deepcopy(document)
        view = display_edges(document['edges'], document['nodes'])
        self.assertEqual([e['_lane_offset'] for e in view], [-8.0, 8.0])
        self.assertEqual(document, before)
        self.assertTrue(all('_lane_offset' not in e for e in document['edges']))

    def test_reverse_input_order_keeps_identity_lanes(self):
        document = doc(4)
        first = {e['id']: e['_lane_offset'] for e in display_edges(document['edges'], document['nodes'])}
        reverse = {e['id']: e['_lane_offset'] for e in display_edges(document['edges'][::-1], document['nodes'])}
        self.assertEqual(first, reverse)
        self.assertEqual(len(set(first.values())), 4)

    def test_adaptive_lanes_stay_within_small_shape(self):
        document = doc(14)
        for node in document['nodes']:
            node['height'] = 20
        view = display_edges(document['edges'], document['nodes'])
        self.assertEqual(len(set(e['_lane_offset'] for e in view)), 14)
        for edge in view:
            start, end = lane_endpoints(*document['nodes'], edge['_lane_offset'])
            self.assertLess(abs(start[1]), 10)
            self.assertLess(abs(end[1]), 10)

    def test_each_parallel_edge_is_individually_selectable(self):
        document = doc()
        for edge in display_edges(document['edges'], document['nodes']):
            points = routing_scene(document['nodes']).route_points(edge)
            midpoint = tuple((a + b) / 2 for a, b in zip(*points))
            selected = edge_at(document['nodes'], document['edges'], *midpoint, tolerance=4)
            self.assertEqual(selected['id'], edge['id'])

    def test_routing_cache_does_not_collapse_distinct_lanes(self):
        document = doc()
        scene = routing_scene(document['nodes'])
        routes = [scene.route_points(edge) for edge in display_edges(document['edges'], document['nodes'])]
        self.assertNotEqual(routes[0], routes[1])
        self.assertNotEqual(routes[0][0], routes[1][0])
        self.assertNotEqual(routes[0][-1], routes[1][-1])

    def test_single_link_retains_legacy_route(self):
        document = doc(1)
        edge = display_edges(document['edges'], document['nodes'])[0]
        self.assertNotIn('_lane_offset', edge)
        self.assertEqual(routing_scene(document['nodes']).route_points(edge),
                         [(70, 0), (330, 0)])

    def test_svg_has_two_distinct_straight_lines(self):
        document = doc()
        root = ET.fromstring(to_svg(document))
        lines = root.findall('{http://www.w3.org/2000/svg}line')
        self.assertEqual(len(lines), 2)
        self.assertNotEqual(lines[0].attrib['y1'], lines[1].attrib['y1'])
        self.assertNotEqual(lines[0].attrib['y2'], lines[1].attrib['y2'])

    def test_vsdx_public_endpoints_separated_and_fidelity_passes(self):
        document = doc()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fabric.vsdx'
            export_vsdx(path, document)
            self.assertEqual(audit_public_vsdx(path, document)['status'], 'PASS')
            with ZipFile(path) as archive:
                root = ET.fromstring(archive.read('visio/pages/page1.xml'))
            connectors = [s for s in root.findall(f'.//{{{V}}}Shape')
                          if s.get('NameU') == 'OpenVisio connector']
            self.assertEqual(len(connectors), 2)
            begins = []
            for shape in connectors:
                cells = {c.get('N'): c.get('V') for c in shape.findall(f'{{{V}}}Cell')}
                begins.append(float(cells['BeginY']))
                rows = shape.findall(f'./{{{V}}}Section/{{{V}}}Row')
                self.assertEqual([r.get('T') for r in rows], ['MoveTo', 'LineTo'])
            self.assertNotEqual(*begins)

    def test_orthogonal_paths_have_distinct_valid_port_anchors(self):
        document = doc(2, orthogonal=True)
        scene = routing_scene(document['nodes'])
        routes = [scene.route_points(edge) for edge in display_edges(document['edges'], document['nodes'])]
        self.assertNotEqual(routes[0], routes[1])
        for route in routes:
            for a, b in zip(route, route[1:]):
                self.assertTrue(a[0] == b[0] or a[1] == b[1])
            self.assertAlmostEqual(abs(route[0][0]), 70)

    def test_saved_document_never_contains_transient_lanes(self):
        document = doc()
        display_edges(document['edges'], document['nodes'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'diagram.ovjson'
            save(path, document)
            self.assertNotIn('_lane_offset', path.read_text())
            self.assertEqual(load(path), document)


if __name__ == '__main__':
    unittest.main()
