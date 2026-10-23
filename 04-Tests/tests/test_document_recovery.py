"""Document recovery service tests. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from openvisio.document_recovery import backup_path, read_backup
from openvisio.model import save

class RecoveryServiceTests(unittest.TestCase):
    def test_backup_path_and_recovered_document(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "network.ovjson"
            old = {"nodes": [], "edges": []}
            new = {"nodes": [{"id": "n", "x": 1, "y": 2}], "edges": []}
            self.assertEqual(backup_path(target), Path(str(target) + ".bak"))
            save(target, old)
            save(target, new)
            self.assertEqual(read_backup(target), old)

    def test_missing_backup_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                read_backup(Path(directory) / "missing.ovjson")
