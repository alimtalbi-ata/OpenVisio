"""V43.17: native SVG preserves SAN link direction and per-path identity.

Synthetic SVG interoperability checks only; not Microsoft Visio Desktop tests.
Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from openvisio.export import to_svg, export_svg

SVG = '{http://www.w3.org/2000/svg}'
ARROW = 'url(#openvisio-san-arrow)'


def topology(orthogonal=False):
    nodes = [
            {'id': 'host', 'x': 100, 'y': 120, 'shape': 'server'},
            {'id': 'array', 'x': 600, 'y': 120, 'shape': 'storage'},
        ]
    if orthogonal:
        nodes.append({'id': 'obstacle', 'x': 350, 'y': 120, 'shape': 'server', 'width': 140, 'height': 100})
    return {
        'nodes': nodes,
        'edges': [
            {'id': 'FC-A', 'from': 'host', 'to': 'array',
             'routing': 'orthogonal' if orthogonal else 'straight',
             'protocol': 'FC', 'fabric': 'A'},
            {'id': 'FC-B', 'from': 'array', 'to': 'host',
             'routing': 'orthogonal' if orthogonal else 'straight',
             'protocol': 'FC', 'fabric': 'B'},
        ],
    }


def paths(root):
    return root.findall(SVG + 'line') + root.findall(SVG + 'polyline')


class SvgDirectionTests(unittest.TestCase):
    def test_straight_san_paths_have_real_svg_arrowheads_and_identity(self):
        document = topology()
        original = copy.deepcopy(document)
        root = ET.fromstring(to_svg(document))
        markers = root.findall('.//' + SVG + 'marker')
        self.assertEqual([marker.get('id') for marker in markers], ['openvisio-san-arrow'])
        self.assertEqual(markers[0].get('orient'), 'auto')
        self.assertEqual(len(markers[0].findall(SVG + 'path')), 1)
        links = paths(root)
        self.assertEqual(len(links), 2)
        self.assertEqual({p.get('data-openvisio-connector') for p in links}, {'FC-A', 'FC-B'})
        self.assertTrue(all(p.get('marker-end') == ARROW for p in links))
        self.assertEqual(document, original, 'SVG rendering must not change the SAN diagram')

    def test_orthogonal_parallel_paths_keep_arrows_on_last_segment(self):
        root = ET.fromstring(to_svg(topology(orthogonal=True)))
        links = paths(root)
        self.assertEqual(len(links), 2)
        self.assertTrue(all(p.get('marker-end') == ARROW for p in links))
        self.assertEqual({p.get('data-openvisio-connector') for p in links}, {'FC-A', 'FC-B'})
        self.assertTrue(all(p.tag == SVG + 'polyline' for p in links))

    def test_hidden_fabric_does_not_leak_link_or_arrow(self):
        doc = topology()
        doc['layers'] = [{'id': 'hidden', 'name': 'Hidden', 'visible': False}]
        doc['edges'][1]['layer'] = 'hidden'
        root = ET.fromstring(to_svg(doc))
        self.assertEqual([p.get('data-openvisio-connector') for p in paths(root)], ['FC-A'])
        self.assertEqual(len(root.findall('.//' + SVG + 'marker')), 1)

    def test_no_edges_does_not_emit_unused_arrow_marker(self):
        root = ET.fromstring(to_svg({'nodes': [], 'edges': []}))
        self.assertEqual(root.findall('.//' + SVG + 'marker'), [])

    def test_connector_id_is_escaped_and_xml10_safe(self):
        doc = topology()
        doc['edges'] = [{**doc['edges'][0], 'id': 'FC<&"\x01'}]
        root = ET.fromstring(to_svg(doc))
        self.assertEqual(paths(root)[0].get('data-openvisio-connector'), 'FC<&"\ufffd')

    def test_exported_file_is_parseable_with_direction_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'SAN.svg'
            digest = export_svg(path, topology(), require_absent=True)
            self.assertEqual(len(digest), 64)
            root = ET.parse(path).getroot()
            self.assertEqual(len(paths(root)), 2)
            self.assertTrue(all(p.get('marker-end') == ARROW for p in paths(root)))


if __name__ == '__main__':
    unittest.main()
