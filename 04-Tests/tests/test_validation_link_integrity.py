"""Link integrity regression tests. Author: Abdelhalim Talbi."""
import unittest
from openvisio.model import validate

class LinkIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}]

    def test_valid_link(self):
        doc = {"nodes": self.nodes, "edges": [{"id": "e", "from": "a", "to": "b"}]}
        self.assertEqual(validate(doc), doc)

    def test_self_link_rejected(self):
        with self.assertRaises(ValueError):
            validate({"nodes": self.nodes, "edges": [{"id": "e", "from": "a", "to": "a"}]})

    def test_missing_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            validate({"nodes": self.nodes, "edges": [{"id": "e", "from": "a", "to": "missing"}]})

    def test_invalid_endpoint_type_rejected(self):
        for endpoint in (None, 1, ["b"], {"id": "b"}):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    validate({"nodes": self.nodes, "edges": [{"id": "e", "from": "a", "to": endpoint}]})
