"""V42.34 SAN connector label layout: synthetic, reproducible geometry.

Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.connector_labels import edge_label_text, layout_connector_labels
from openvisio.export import to_svg
from openvisio.model import validate
from openvisio.node_geometry import node_bounds
from openvisio.vsdx import V, export_vsdx
from openvisio.vsdx_fidelity import audit_public_vsdx, PublicVsdxFidelityError


def diagram():
    nodes = [
        {'id':'esxi', 'x':180, 'y':260, 'shape':'server', 'label':'ESXi cluster'},
        {'id':'flash', 'x':700, 'y':260, 'shape':'storage', 'label':'FlashArray'},
        {'id':'switch', 'x':440, 'y':260, 'shape':'san-switch',
         'label':'SAN obstacle', 'width':140, 'height':100},
    ]
    edges = [{'id':f'fc-{i}', 'from':'esxi', 'to':'flash',
              'protocol':'FC', 'speed_gbps':'32', 'source_port':f'vmhba{i}',
              'target_port':f'ct{i}', 'fabric':f'FAB{i}',
              'routing':'orthogonal'} for i in range(4)]
    return validate({'nodes':nodes, 'edges':edges})


def intersects(a, b):
    return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]


class ConnectorLabelTests(unittest.TestCase):
    def test_four_parallel_paths_get_four_non_overlapping_labels(self):
        doc = diagram()
        layout = layout_connector_labels(doc['nodes'], doc['edges'])
        self.assertEqual(len(layout.labels), 4)
        self.assertFalse(layout.hidden)
        labels = list(layout.labels.values())
        for i, a in enumerate(labels):
            self.assertIn('32 Gbit/s', a.text)
            for b in labels[i+1:]:
                self.assertFalse(intersects(a.bounds, b.bounds), (a, b))
            for node in doc['nodes']:
                self.assertFalse(intersects(a.bounds, node_bounds(node)), (a, node))

    def test_layout_is_stable_on_edge_reorder_and_does_not_mutate_document(self):
        doc = diagram()
        original = copy.deepcopy(doc)
        a = layout_connector_labels(doc['nodes'], doc['edges'])
        b = layout_connector_labels(doc['nodes'], list(reversed(doc['edges'])))
        self.assertEqual(a, b)
        self.assertEqual(doc, original)

    def test_zoom_independent_world_coordinates(self):
        doc = diagram()
        a = layout_connector_labels(doc['nodes'], doc['edges'])
        self.assertEqual(a, layout_connector_labels(doc['nodes'], doc['edges']))
        self.assertTrue(all(-100000 < label.x < 100000 for label in a.labels.values()))

    def test_metadata_text_uses_single_shared_formatter(self):
        self.assertEqual(edge_label_text({'protocol':'FC','fabric':'A',
                        'source_port':'p1','target_port':'p2'}),
                         'FC · Fabric A · p1 → p2')
        self.assertEqual(edge_label_text({}), '')
        self.assertLessEqual(len(edge_label_text({'protocol':'x'*500})),72)

    def test_svg_includes_all_labels_and_full_bounds(self):
        doc = diagram()
        layout = layout_connector_labels(doc['nodes'], doc['edges'])
        root = ET.fromstring(to_svg(doc))
        ns = '{http://www.w3.org/2000/svg}'
        labels = {t.get('data-openvisio-edge'): t
                  for t in root.findall(ns+'text') if t.get('data-openvisio-edge')}
        self.assertEqual(set(labels), set(layout.labels))
        x,y,w,h = map(float, root.get('viewBox').split())
        for edge_id, label in layout.labels.items():
            self.assertEqual(labels[edge_id].text, label.text)
            self.assertAlmostEqual(float(labels[edge_id].get('x')), label.x)
            self.assertAlmostEqual(float(labels[edge_id].get('y')), label.y)
            self.assertLess(x, label.bounds[0]); self.assertGreater(x+w, label.bounds[2])
            self.assertLess(y, label.bounds[1]); self.assertGreater(y+h, label.bounds[3])

    def test_svg_escapes_connector_ids_and_text(self):
        doc = {'nodes':[{'id':'a','x':0,'y':0}, {'id':'b','x':400,'y':0}],
               'edges':[{'id':'a"&b', 'from':'a','to':'b', 'protocol':'FC<&'}]}
        root = ET.fromstring(to_svg(doc))
        label = next(t for t in root.iter() if t.get('data-openvisio-edge'))
        self.assertEqual(label.get('data-openvisio-edge'), 'a"&b')
        self.assertEqual(label.text, 'FC<&')

    def test_vsdx_connector_text_is_public_not_only_embedded_json(self):
        doc = diagram()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'san.vsdx'
            export_vsdx(path, doc)
            with ZipFile(path) as archive:
                root = ET.fromstring(archive.read('visio/pages/page1.xml'))
                connectors = [shape for shape in root.findall(f'.//{{{V}}}Shape')
                              if shape.get('NameU') == 'OpenVisio connector']
                self.assertEqual(len(connectors), 4)
                texts = [shape.find(f'{{{V}}}Text').text for shape in connectors]
                self.assertEqual(set(texts),
                                 {edge_label_text(edge) for edge in doc['edges']})

    def test_public_fidelity_detects_swapped_fc_port_labels(self):
        doc = diagram()
        with tempfile.TemporaryDirectory() as directory:
            source, changed = Path(directory)/'source.vsdx', Path(directory)/'changed.vsdx'
            export_vsdx(source, doc)
            self.assertEqual(audit_public_vsdx(source, doc)['status'], 'PASS')
            with ZipFile(source) as original, ZipFile(changed, 'w', ZIP_DEFLATED) as target:
                for name in original.namelist():
                    data = original.read(name)
                    if name == 'visio/pages/page1.xml':
                        root = ET.fromstring(data)
                        labels = [shape.find(f'{{{V}}}Text') for shape in root.findall(
                            f'./{{{V}}}Shapes/{{{V}}}Shape')
                            if shape.get('NameU') == 'OpenVisio connector']
                        labels[0].text, labels[1].text = labels[1].text, labels[0].text
                        data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    target.writestr(name, data)
            with self.assertRaisesRegex(PublicVsdxFidelityError, 'Libellé du connecteur'):
                audit_public_vsdx(changed, doc)

    def test_hidden_label_is_explicitly_reported(self):
        nodes = [{'id':'a','x':0,'y':0},{'id':'b','x':600,'y':0}]
        edges = [{'id':str(i),'from':'a','to':'b','protocol':'FC',
                  'source_port':f'a{i}', 'target_port':f'b{i}'} for i in range(100)]
        layout = layout_connector_labels(nodes, edges)
        self.assertGreater(len(layout.hidden), 0)
        self.assertEqual(len(layout.labels)+len(layout.hidden), 100)

    def test_no_label_means_no_route_work(self):
        from unittest.mock import patch
        from openvisio.routing import RoutingScene
        doc = diagram()
        for edge in doc['edges']:
            for key in ('protocol','fabric','speed_gbps','source_port','target_port'):
                edge.pop(key, None)
        with patch.object(RoutingScene, 'route_points', side_effect=AssertionError('unneeded')):
            layout = layout_connector_labels(doc['nodes'], doc['edges'])
        self.assertEqual(layout.labels, {})


if __name__ == '__main__':
    unittest.main()
