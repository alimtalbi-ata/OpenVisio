import tempfile
from unittest.mock import patch
import unittest
from pathlib import Path
from openvisio.model import load, save, validate

class ModelTests(unittest.TestCase):
    def test_roundtrip(self):
        data = {"nodes":[{"id":"a","x":1,"y":2},{"id":"b","x":3,"y":4}],"edges":[{"id":"edge-ab","from":"a","to":"b"}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagram.ovjson"
            save(path, data)
            self.assertEqual(load(path), data)
    def test_corrupt_json_reports_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.ovjson"
            path.write_text('{"nodes": [', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON invalide"):
                load(path)

    def test_invalid_utf8_reports_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.ovjson"
            path.write_bytes(b"\\xff\\xfe")
            with self.assertRaisesRegex(ValueError, "illisible"):
                load(path)

    def test_failed_atomic_replace_preserves_existing_file(self):
        original = {"nodes": [{"id": "a", "x": 1, "y": 2}], "edges": []}
        changed = {"nodes": [{"id": "b", "x": 3, "y": 4}], "edges": []}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagram.ovjson"
            save(path, original)
            original_bytes = path.read_bytes()
            with patch("os.replace", side_effect=OSError("simulated disk failure")):
                with self.assertRaises(OSError):
                    save(path, changed)
            self.assertEqual(path.read_bytes(), original_bytes)
            self.assertEqual(list(Path(tmp).glob(".openvisio-*.tmp")), [])

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":1,"y":2},{"id":"a","x":1,"y":2}],"edges":[]})
    def test_dangling_edge(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":1,"y":2}],"edges":[{"id":"edge-invalid","from":"a","to":"missing"}]})

if __name__ == "__main__":
    unittest.main()
