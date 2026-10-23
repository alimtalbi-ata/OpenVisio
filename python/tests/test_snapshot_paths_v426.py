import tempfile
import unittest
from pathlib import Path
from openvisio.document_integrity import snapshot, verify_snapshot
class SnapshotPathTests(unittest.TestCase):
    def test_change_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "backup.bak"
            p.write_text("old")
            before = snapshot(p)
            self.assertEqual(before.path, p.resolve())
            p.write_text("new")
            with self.assertRaises(RuntimeError): verify_snapshot(before)
