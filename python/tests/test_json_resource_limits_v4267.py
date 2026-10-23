"""V42.67: reject malformed/oversized diagrams without unhandled exceptions.

Synthetic JSON fixtures only; not Microsoft Visio fidelity evidence.
Author: Abdelhalim Talbi.
"""
import unittest
from unittest.mock import patch

from openvisio.model import load_bytes


class JsonResourceLimitTests(unittest.TestCase):
    def test_oversized_document_rejected_before_parse(self):
        with patch('openvisio.model.MAX_DOCUMENT_BYTES', 12):
            with self.assertRaisesRegex(ValueError, 'volumineux'):
                load_bytes(b'{"nodes":[],"edges":[]}')

    def test_deeply_nested_json_rejected_as_document_error(self):
        payload = b'{"metadata":' + b'[' * 2000 + b'0' + b']' * 2000 + b'}'
        with self.assertRaisesRegex(ValueError, 'illisible|invalide'):
            load_bytes(payload)

    def test_invalid_input_type_rejected_consistently(self):
        for payload in (None, '{"nodes":[]}', bytearray(b'{}')):
            with self.subTest(payload_type=type(payload).__name__):
                with self.assertRaisesRegex(ValueError, 'binaire'):
                    load_bytes(payload)

    def test_missing_optional_edges_loads_without_key_error(self):
        self.assertEqual(load_bytes(b'{"nodes":[]}'),
                         {"nodes": [], "edges": []})

    def test_valid_small_document_still_loads(self):
        self.assertEqual(load_bytes(b'{"nodes":[],"edges":[]}'),
                         {'nodes': [], 'edges': []})


if __name__ == '__main__':
    unittest.main()
