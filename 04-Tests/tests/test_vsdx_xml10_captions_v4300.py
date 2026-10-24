"""V43.00: public VSDX XML 1.0 caption fidelity; synthetic only.
Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.vsdx import V, export_vsdx, import_vsdx
from openvisio.vsdx_fidelity import audit_public_vsdx


class VsdxXml10Captions(unittest.TestCase):
    def document(self, caption):
        return {
            'nodes': [
                {'id': 'sw', 'shape': 'san-switch', 'x': 0, 'y': 0, 'label': caption},
                {'id': 'array', 'shape': 'storage', 'x': 300, 'y': 0,
                 'label': 'Baie ' + chr(0x16) + ' Flash'},
            ],
            'edges': [{'id': 'fc-a', 'from': 'sw', 'to': 'array',
                       'label': caption, 'fabric': 'A', 'protocol': 'FC'}],
        }

    def assert_export(self, caption, expected):
        document = self.document(caption)
        original = copy.deepcopy(document)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'san.vsdx'
            export_vsdx(path, document)
            with ZipFile(path) as archive:
                page = ET.fromstring(archive.read('visio/pages/page1.xml'))
                texts = [''.join(t.itertext()) for t in page.findall(f'.//{{{V}}}Text')]
                self.assertIn(expected, texts)
                self.assertIn('Baie \ufffd Flash', texts)
                self.assertEqual(len(page.findall(f'.//{{{V}}}Connect')), 2)
            report = audit_public_vsdx(path, document)
            self.assertEqual(report['status'], 'PASS')
            restored = import_vsdx(path)
            self.assertEqual(restored['nodes'][0]['label'], caption)
            self.assertEqual(restored['edges'][0]['label'], caption)
            self.assertEqual(document, original)

    def test_c0_controls_preserve_private_original(self):
        self.assert_export('FC' + chr(1) + ' Switch', 'FC\ufffd Switch')

    def test_unpaired_surrogate_preserve_private_original(self):
        self.assert_export('FC' + chr(0xd800) + ' Switch', 'FC\ufffd Switch')

    def test_valid_unicode_and_xml_whitespace_unchanged(self):
        self.assert_export('Fibre A\tR\u00e9seau\n\u00e9tage',
                           'Fibre A\tR\u00e9seau\n\u00e9tage')

    def test_multiple_control_characters_are_replaced_individually(self):
        self.assert_export('FC' + chr(0) + chr(11) + chr(0xfffe) + ' A',
                           'FC\ufffd\ufffd\ufffd A')


if __name__ == '__main__':
    unittest.main()
