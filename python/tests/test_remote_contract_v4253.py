"""V42.53: guard against GitHub-source regression of document and VSDX contracts.

Synthetic Visio packages only. Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.model import validate
from openvisio.connector_labels import edge_label_text
from openvisio.vsdx import export_vsdx, import_vsdx


class RemoteContractTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            'nodes': [
                {'id': 'g', 'x': 0, 'y': 0, 'shape': 'visio-group', 'layer': 'L'},
                {'id': 'a', 'x': 100, 'y': 0, 'shape': 'server',
                 'layer': 'L', 'visio_group_parent': 'g'},
                {'id': 'b', 'x': 300, 'y': 0, 'shape': 'storage', 'layer': 'L'},
            ],
            'edges': [{'id': 'e', 'from': 'a', 'to': 'b', 'layer': 'L',
                       'routing': 'orthogonal', 'label': 'SAN critique'}],
            'layers': [{'id': 'L', 'name': 'Production', 'visible': True}],
            'metadata': {'source': 'Visio'},
            'extension': {'retained': True},
        }

    def test_validation_preserves_document_envelope(self):
        self.assertEqual(validate(self.doc), self.doc)

    def test_unknown_layer_is_rejected(self):
        self.doc['edges'][0]['layer'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'Calque'):
            validate(self.doc)

    def test_group_cycle_is_rejected(self):
        self.doc['nodes'][0]['visio_group_parent'] = 'g'
        with self.assertRaisesRegex(ValueError, 'groupe'):
            validate(self.doc)

    def test_invalid_routing_is_rejected(self):
        self.doc['edges'][0]['routing'] = 'unrecognized'
        with self.assertRaisesRegex(ValueError, 'routage'):
            validate(self.doc)

    def test_caption_takes_precedence_over_derived_san_metadata(self):
        self.assertEqual(edge_label_text({'label': 'SAN critique', 'protocol': 'FC'}),
                         'SAN critique')

    def test_external_vsdx_caption_survives_without_private_payload(self):
        doc = {'nodes': [
            {'id': 'a', 'x': 100, 'y': 100, 'shape': 'server'},
            {'id': 'b', 'x': 400, 'y': 100, 'shape': 'storage'}],
            'edges': [{'id': 'e', 'from': 'a', 'to': 'b',
                       'label': 'SAN critique'}]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'source.vsdx'
            export_vsdx(path, doc)
            with ZipFile(path) as source:
                parts = {name: source.read(name) for name in source.namelist()
                         if not name.startswith('openvisio/')}
            with ZipFile(path, 'w', ZIP_DEFLATED) as target:
                for name, data in parts.items():
                    target.writestr(name, data)
            imported = import_vsdx(path)
            self.assertEqual(imported['edges'][0]['label'], 'SAN critique')
            self.assertEqual(imported['metadata']['import_mode'], 'flattened-pages')


if __name__ == '__main__':
    unittest.main()
