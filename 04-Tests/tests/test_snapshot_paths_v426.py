import tempfile
import unittest
from pathlib import Path
from openvisio.document_integrity import snapshot, verify_snapshot

class SnapshotPathTests(unittest.TestCase):
    def test_equivalent_paths(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "diagram.bak"
            p.write_text("version one", encoding="utf-8")
            snap = snapshot(p)
            self.assertEqual(snap.path, p.resolve())
            self.assertTrue(verify_snapshot(snap))
            p.write_text("version two", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                verify_snapshot(snap)
