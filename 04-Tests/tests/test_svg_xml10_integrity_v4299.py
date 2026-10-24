"""V42.99: SVG export is always XML 1.0 compatible for imported captions.

Synthetic OpenVisio checks, not Microsoft Visio Desktop fidelity.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from openvisio.export import export_svg, to_svg

SVG = '{http://www.w3.org/2000/svg}'


class SvgXml10IntegrityTests(unittest.TestCase):
    def test_invalid_xml_controls_in_node_caption_are_replaced(self):
        doc = {'nodes': [{'id': 'host', 'x': 100, 'y': 100,
                          'label': 'FC\x00 host\x1f — \U0001f5a5'}], 'edges': []}
        root = ET.fromstring(to_svg(doc))
        texts = [node.text for node in root.findall(SVG + 'text')]
        self.assertIn('FC\ufffd host\ufffd — \U0001f5a5', texts)

    def test_invalid_controls_in_connector_id_and_caption_are_replaced(self):
        doc = {'nodes': [{'id': 'a', 'x': 0, 'y': 0},
                         {'id': 'b', 'x': 450, 'y': 0}],
               'edges': [{'id': 'fc\x01A', 'from': 'a', 'to': 'b',
                          'label': 'Fabric\x02 A & B'}]}
        root = ET.fromstring(to_svg(doc))
        labels = [n for n in root.findall(SVG + 'text')
                  if 'data-openvisio-edge' in n.attrib]
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].attrib['data-openvisio-edge'], 'fc\ufffdA')
        self.assertEqual(labels[0].text, 'Fabric\ufffd A & B')

    def test_unpaired_surrogate_is_safe_for_utf8_file_export(self):
        doc = {'nodes': [{'id': 'host', 'x': 100, 'y': 100,
                          'label': 'bad\ud800surrogate'}], 'edges': []}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'diagram.svg'
            revision = export_svg(path, doc, require_absent=True)
            self.assertEqual(len(revision), 64)
            root = ET.parse(path).getroot()
            self.assertIn('bad\ufffdsurrogate', [n.text for n in root.findall(SVG + 'text')])


if __name__ == '__main__':
    unittest.main()
