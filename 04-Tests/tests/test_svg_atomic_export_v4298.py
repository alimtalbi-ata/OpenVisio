"""V42.98 SVG transaction regression tests. Author: Abdelhalim Talbi."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from openvisio.export import export_svg
from openvisio.model import SaveConflict

DOC = {"nodes": [{"id": "host", "x": 100, "y": 100, "label": "Hôte SAN"}], "edges": []}


class AtomicSvgExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "topology.svg"

    def test_published_svg_is_valid_and_revision_matches(self):
        revision = export_svg(self.path, DOC, require_absent=True)
        self.assertEqual(revision, hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(ElementTree.parse(self.path).getroot().tag,
                         "{http://www.w3.org/2000/svg}svg")

    def test_existing_svg_is_never_clobbered_with_require_absent(self):
        self.path.write_bytes(b"external edit")
        with self.assertRaises(SaveConflict):
            export_svg(self.path, DOC, require_absent=True)
        self.assertEqual(self.path.read_bytes(), b"external edit")

    def test_matching_revision_can_be_replaced(self):
        self.path.write_bytes(b"old")
        expected = hashlib.sha256(b"old").hexdigest()
        revision = export_svg(self.path, DOC, expected_sha256=expected)
        self.assertEqual(revision, hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertNotEqual(self.path.read_bytes(), b"old")

    def test_stale_revision_does_not_change_primary(self):
        self.path.write_bytes(b"another writer")
        with self.assertRaises(SaveConflict):
            export_svg(self.path, DOC, expected_sha256="0" * 64)
        self.assertEqual(self.path.read_bytes(), b"another writer")

    def test_invalid_preconditions_rejected_without_write(self):
        for kwargs in ({"expected_sha256": "INVALID"},
                       {"expected_sha256": "0" * 64, "require_absent": True}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    export_svg(self.path, DOC, **kwargs)
                self.assertFalse(self.path.exists())

    def test_failed_replace_preserves_original_and_cleans_temporary(self):
        self.path.write_bytes(b"original")
        with patch("os.replace", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                export_svg(self.path, DOC)
        self.assertEqual(self.path.read_bytes(), b"original")
        self.assertFalse(list(self.path.parent.glob(".openvisio-svg-*.tmp")))

    def test_invalid_document_does_not_touch_destination(self):
        self.path.write_bytes(b"previous")
        with self.assertRaises(ValueError):
            export_svg(self.path, {"nodes": "invalid", "edges": []})
        self.assertEqual(self.path.read_bytes(), b"previous")


if __name__ == "__main__":
    unittest.main()
