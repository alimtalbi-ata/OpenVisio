import json
import tempfile
import unittest
from pathlib import Path
from openvisio.model import load

class LegacyMigrationTests(unittest.TestCase):
    def test_old_edge_without_id_is_migrated(self):
        document = {"nodes":[{"id":"a","x":1,"y":2},{"id":"b","x":3,"y":4}],"edges":[{"from":"a","to":"b"}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "legacy.ovjson"
            path.write_text(json.dumps(document), encoding="utf-8")
            first = load(path)
            second = load(path)
            self.assertTrue(first["edges"][0]["id"].startswith("legacy-"))
            self.assertEqual(first, second)
            self.assertEqual(json.loads(path.read_text()), document)
