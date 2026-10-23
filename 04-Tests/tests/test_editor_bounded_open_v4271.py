"""V42.71: editor open-with-revision must share the bounded document reader.

Synthetic fixtures, not evidence of Windows or Microsoft Visio qualification.
Author: Abdelhalim Talbi.
"""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openvisio import model
from openvisio.document_service import open_document_with_revision


class _BoundedStream(io.BytesIO):
    def __init__(self, payload):
        super().__init__(payload)
        self.sizes = []

    def read(self, size=-1):
        self.sizes.append(size)
        if size < 0:
            raise AssertionError("unbounded editor read")
        return super().read(size)


class EditorBoundedOpenTests(unittest.TestCase):
    def test_editor_reads_only_limit_plus_one(self):
        stream = _BoundedStream(b"x" * 40)
        with patch.object(model, "MAX_DOCUMENT_BYTES", 32), patch.object(
            Path, "open", return_value=stream
        ):
            with self.assertRaisesRegex(ValueError, "volumineux"):
                open_document_with_revision("untrusted.ovjson")
        self.assertEqual(stream.sizes, [33])

    def test_editor_accepts_document_at_exact_limit_and_hashes_same_bytes(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.ovjson"
            path.write_bytes(payload)
            with patch.object(model, "MAX_DOCUMENT_BYTES", len(payload)):
                document, revision = open_document_with_revision(path)
        self.assertEqual(document, {"nodes": [], "edges": []})
        self.assertEqual(revision, hashlib.sha256(payload).hexdigest())

    def test_editor_rejects_one_byte_over_limit(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.ovjson"
            path.write_bytes(payload)
            with patch.object(model, "MAX_DOCUMENT_BYTES", len(payload) - 1):
                with self.assertRaisesRegex(ValueError, "volumineux"):
                    open_document_with_revision(path)


if __name__ == "__main__":
    unittest.main()
