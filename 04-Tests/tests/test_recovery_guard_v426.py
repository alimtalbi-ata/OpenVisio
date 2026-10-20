import json
import tempfile
import unittest
from pathlib import Path
from openvisio.document_integrity import snapshot
from openvisio.recovery_guard import guarded_backup_read

class GuardedRecoveryTests(unittest.TestCase):
    def test_valid_backup(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "diagram.bak"
            p.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
            self.assertEqual(guarded_backup_read(p, snapshot(p)), {"nodes": [], "edges": []})

    def test_changed_backup_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "diagram.bak"
            p.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
            old = snapshot(p)
            p.write_text(json.dumps({"nodes": [], "edges": [], "extra": 1}), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                guarded_backup_read(p, old)
