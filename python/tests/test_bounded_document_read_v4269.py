"""Regression tests for bounded OpenVisio file reads. Author: Abdelhalim Talbi."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openvisio import model


class _TrackedStream(io.BytesIO):
    def __init__(self, payload):
        super().__init__(payload)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size < 0:
            raise AssertionError("unbounded document read")
        return super().read(size)


class BoundedDocumentReadTests(unittest.TestCase):
    def test_load_uses_explicit_size_limit(self):
        stream = _TrackedStream(b"x" * 33)
        with patch.object(model, "MAX_DOCUMENT_BYTES", 32), patch.object(
            Path, "open", return_value=stream
        ):
            with self.assertRaisesRegex(ValueError, "volumineux"):
                model.load("not-actually-read.ovjson")
        self.assertEqual(stream.read_sizes, [33])

    def test_exact_limit_is_accepted(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.ovjson"
            path.write_bytes(payload)
            with patch.object(model, "MAX_DOCUMENT_BYTES", len(payload)):
                self.assertEqual(model.load(path), {"nodes": [], "edges": []})

    def test_one_byte_over_limit_is_rejected(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.ovjson"
            path.write_bytes(payload)
            with patch.object(model, "MAX_DOCUMENT_BYTES", len(payload) - 1):
                with self.assertRaisesRegex(ValueError, "volumineux"):
                    model.load(path)

    def test_save_and_reload_preserves_topology(self):
        topology = {"nodes": [{"id": "switch1", "x": 1, "y": 2},
                              {"id": "array1", "x": 8, "y": 4}],
                    "edges": [{"id": "san-a", "from": "switch1", "to": "array1"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "san.ovjson"
            model.save(path, topology)
            self.assertEqual(model.load(path), topology)


if __name__ == "__main__":
    unittest.main()
