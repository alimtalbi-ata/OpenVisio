"""V43.06 regression: malformed imported labels must not make native save unusable.

These tests exercise native OpenVisio persistence, not Microsoft Visio Desktop.
Author: Abdelhalim Talbi.
"""
import json
import tempfile
import unittest
from pathlib import Path

from openvisio.model import load, save


class NativeSaveSurrogateIntegrity(unittest.TestCase):
    def test_lone_surrogates_survive_utf8_save_and_reload(self):
        label = "Brocade G720 \ud800 — SAN \udfff"
        doc = {"nodes": [{"id": "sw-a", "x": 0, "y": 0,
                           "shape": "san-switch", "label": label}],
               "edges": [], "metadata": {"import_note": "raw \udc00 and é"}}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fabric.openvisio"
            digest = save(target, doc)
            data = target.read_bytes()
            # The on-disk file must be valid UTF-8 and JSON, even if imported
            # strings contain lone UTF-16 surrogates.
            decoded = json.loads(data.decode("utf-8"))
            self.assertEqual(decoded, doc)
            self.assertEqual(load(target), doc)
            self.assertEqual(len(digest), 64)
            self.assertIn(b"\\ud800", data)
            self.assertIn(b"\\udfff", data)
            self.assertIn("é".encode("utf-8"), data)

    def test_literal_escape_and_emoji_not_reinterpreted(self):
        doc = {"nodes": [{"id": "n", "x": 0, "y": 0,
                           "label": "Literal \\ud800 / smile 😀 / invalid \ud800"}],
               "edges": []}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "special.openvisio"
            save(target, doc)
            self.assertEqual(load(target), doc)
            self.assertIn("😀".encode("utf-8"), target.read_bytes())

    def test_optimistic_save_backup_remains_reopenable(self):
        doc = {"nodes": [{"id": "n", "x": 0, "y": 0,
                           "label": "A \ud800"}], "edges": []}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "switches.openvisio"
            revision = save(target, doc, require_absent=True)
            updated = {**doc, "nodes": [{**doc["nodes"][0], "label": "B \udfff"}]}
            save(target, updated, expected_sha256=revision)
            self.assertEqual(load(target), updated)
            self.assertEqual(load(target.with_name(target.name + ".bak")), doc)


if __name__ == "__main__":
    unittest.main()
