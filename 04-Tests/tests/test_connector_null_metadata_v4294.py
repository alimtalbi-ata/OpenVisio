"""V42.94: optional FC metadata must never render as literal None.
Synthetic unit and export integration only; not Microsoft Visio Desktop.
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


def _doc():
    return {'nodes': [
        {'id': 'h', 'x': 100, 'y': 100, 'shape': 'server'},
        {'id': 's', 'x': 550, 'y': 100, 'shape': 'san-switch'}],
        'edges': [{'id': 'fc', 'from': 'h', 'to': 's', 'routing': 'straight',
                   'label': '', 'protocol': 'FC', 'source_port': 'vmhba0'}]}


class NullMetadataLabels(unittest.TestCase):
    def test_null_metadata_is_not_text(self):
        self.assertEqual(edge_label_text({**_doc()['edges'][0], 'label': None, 'fabric': None, 'target_port': None, 'speed_gbps': None}), 'FC · vmhba0')

    def test_all_null_fields_are_blank(self):
        self.assertEqual(edge_label_text({key: None for key in
            ('label', 'protocol', 'speed_gbps', 'fabric', 'source_port', 'target_port')}), '')

    def test_layout_and_svg_have_identical_caption(self):
        doc = _doc()
        expected = 'FC · vmhba0'
        self.assertEqual(layout_connector_labels(doc['nodes'], doc['edges']).labels['fc'].text, expected)
        root = ET.fromstring(to_svg(doc))
        captions = [element.text for element in root.iter()
                    if element.get('data-openvisio-edge') == 'fc']
        self.assertEqual(captions, [expected])

    def test_public_vsdx_caption_omits_null_literals(self):
        doc = _doc()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'fc.vsdx'
            export_vsdx(target, doc)
            with ZipFile(target) as archive:
                root = ET.fromstring(archive.read('visio/pages/page1.xml'))
            captions = [shape.find(f'{{{V}}}Text').text for shape in
                root.findall(f'./{{{V}}}Shapes/{{{V}}}Shape')
                if shape.get('NameU') == 'OpenVisio connector']
            self.assertEqual(captions, ['FC · vmhba0'])


if __name__ == '__main__':
    unittest.main()
