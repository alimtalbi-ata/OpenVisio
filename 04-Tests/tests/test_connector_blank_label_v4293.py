"""V42.93: blank SAN caption fallback is identical in Tk, SVG and public VSDX.

Synthetic integration only; no Microsoft Visio Desktop qualification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.connector_labels import edge_label_text, layout_connector_labels
from openvisio.export import to_svg
from openvisio.vsdx import V, export_vsdx
from openvisio.vsdx_fidelity import audit_public_vsdx


def _diagram(label):
    return {'nodes': [
        {'id':'host','x':100,'y':150,'shape':'server','label':'ESXi'},
        {'id':'array','x':650,'y':150,'shape':'storage','label':'FlashArray'}],
        'edges': [{'id':'fc-a','from':'host','to':'array','routing':'straight',
                   'label':label,'protocol':'FC','fabric':'A',
                   'source_port':'vmhba2','target_port':'ct0.fc1'}]}


class BlankConnectorLabelTests(unittest.TestCase):
    def test_whitespace_caption_uses_fc_metadata(self):
        edge = _diagram('  \t  ')['edges'][0]
        self.assertEqual(edge_label_text(edge),
                         'FC · Fabric A · vmhba2 → ct0.fc1')

    def test_explicit_caption_has_priority(self):
        edge = _diagram('  Dedicated path  ')['edges'][0]
        self.assertEqual(edge_label_text(edge), 'Dedicated path')

    def test_blank_caption_without_metadata_is_empty(self):
        self.assertEqual(edge_label_text({'label':' \t '}), '')

    def test_svg_and_layout_share_fallback_caption(self):
        doc = _diagram('  ')
        expected = edge_label_text(doc['edges'][0])
        layout = layout_connector_labels(doc['nodes'], doc['edges'])
        self.assertEqual(layout.labels['fc-a'].text, expected)
        root = ET.fromstring(to_svg(doc))
        svg_text = [el.text for el in root.iter()
                    if el.get('data-openvisio-edge') == 'fc-a']
        self.assertEqual(svg_text, [expected])

    def test_public_vsdx_caption_and_fidelity_audit(self):
        doc = _diagram(' \t ')
        expected = edge_label_text(doc['edges'][0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'san.vsdx'
            export_vsdx(path, doc)
            with ZipFile(path) as archive:
                page = ET.fromstring(archive.read('visio/pages/page1.xml'))
                captions = [shape.find(f'{{{V}}}Text').text
                            for shape in page.findall(f'./{{{V}}}Shapes/{{{V}}}Shape')
                            if shape.get('NameU') == 'OpenVisio connector']
            self.assertEqual(captions, [expected])
            self.assertEqual(audit_public_vsdx(path, doc)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
