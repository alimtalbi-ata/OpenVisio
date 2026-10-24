"""Atomic save must reject invalid JSON extension data before touching disk."""
import tempfile
import unittest
from pathlib import Path
from openvisio.model import save, load

class FullDocumentSerializationTests(unittest.TestCase):
    def test_invalid_extension_does_not_replace_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.json"
            original = {"nodes": [], "edges": []}
            save(path, original)
            before = path.read_bytes()
            invalid = {"nodes": [{"id": "n", "x": 0, "y": 0, "extension": {"bad"}}], "edges": []}
            with self.assertRaisesRegex(ValueError, "non sérialisable"):
                save(path, invalid)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(load(path)["nodes"], [])

    def test_nan_in_layer_extension_is_rejected(self):
        document = {"nodes": [], "edges": [], "layers": [{"id": "l", "name": "Layer", "custom": float("nan")}]}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "non sérialisable"):
                save(Path(directory) / "diagram.json", document)
