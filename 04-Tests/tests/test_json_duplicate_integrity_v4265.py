"""V42.65: untrusted JSON must not silently replace diagram topology.

Fixtures are local synthetic JSON, not evidence of Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import unittest
from openvisio.model import load_bytes, save
from tempfile import TemporaryDirectory
from pathlib import Path


class DuplicateJsonIntegrityTests(unittest.TestCase):
    def test_duplicate_node_id_field_rejected(self):
        payload = b'{"nodes":[{"id":"safe","id":"other","x":1,"y":2}],"edges":[]}'
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            load_bytes(payload)

    def test_duplicate_root_nodes_field_rejected(self):
        payload = b'{"nodes":[],"nodes":[{"id":"other","x":1,"y":2}],"edges":[]}'
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            load_bytes(payload)

    def test_duplicate_edge_destination_rejected(self):
        payload = (b'{"nodes":[{"id":"a","x":1,"y":2},'
                   b'{"id":"b","x":2,"y":3}],'
                   b'"edges":[{"id":"e","from":"a","to":"a","to":"b"}]}')
        with self.assertRaisesRegex(ValueError, 'dupliqu'):
            load_bytes(payload)

    def test_nonfinite_json_literal_rejected(self):
        for constant in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(constant=constant):
                with self.assertRaisesRegex(ValueError, 'constante JSON interdite'):
                    load_bytes(b'{"nodes":[{"id":"a","x":' + constant
                               + b',"y":2}],"edges":[]}')

    def test_valid_document_still_roundtrips(self):
        original = {'nodes': [{'id': 'a', 'x': 1, 'y': 2}], 'edges': []}
        with TemporaryDirectory() as folder:
            destination = Path(folder) / 'test.ovjson'
            receipt = save(destination, original)
            self.assertEqual(len(receipt), 64)
            self.assertEqual(load_bytes(destination.read_bytes()), original)


if __name__ == '__main__':
    unittest.main()
