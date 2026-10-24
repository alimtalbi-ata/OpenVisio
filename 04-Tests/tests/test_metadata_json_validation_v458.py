"""Metadata must be JSON-serializable before save/export."""
import unittest
from openvisio.model import validate

class MetadataSerializationTests(unittest.TestCase):
    def test_reject_set(self):
        with self.assertRaisesRegex(ValueError, "non sérialisables"):
            validate({"nodes": [], "edges": [], "metadata": {"tags": {"a", "b"}}})

    def test_reject_nan(self):
        with self.assertRaisesRegex(ValueError, "non sérialisables"):
            validate({"nodes": [], "edges": [], "metadata": {"confidence": float("nan")}})

    def test_accept_nested_json(self):
        doc = {"nodes": [], "edges": [], "metadata": {"tags": ["a", "b"], "nested": {"n": 1}}}
        self.assertEqual(validate(doc)["metadata"], doc["metadata"])

    def test_reject_non_string_metadata_key(self):
        with self.assertRaisesRegex(ValueError, "Clé de métadonnée non textuelle"):
            validate({"nodes": [], "edges": [], "metadata": {1: "numeric-key"}})

    def test_reject_nested_numeric_key(self):
        with self.assertRaisesRegex(ValueError, "Clé de métadonnée non textuelle"):
            validate({"nodes": [], "edges": [], "metadata": {"nested": [{2: "bad"}]}})

    def test_reject_cyclic_metadata(self):
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaisesRegex(ValueError, "Référence circulaire"):
            validate({"nodes": [], "edges": [], "metadata": cyclic})
