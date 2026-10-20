"""Backward compatibility and deterministic migration tests. Author: Abdelhalim Talbi."""
import json
import tempfile
import unittest
from pathlib import Path
from openvisio.model import load, save

class LegacyRoundTripTests(unittest.TestCase):
    def test_missing_link_ids_are_migrated_deterministically(self):
        old = {"nodes": [{"id": "a", "x": 1, "y": 2}, {"id": "b", "x": 3, "y": 4}],
               "edges": [{"from": "a", "to": "b"}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.ovjson"
            path.write_text(json.dumps(old), encoding="utf-8")
            first = load(path)
            second = load(path)
            self.assertEqual(first, second)
            self.assertTrue(first["edges"][0]["id"].startswith("legacy-"))
            save(path, first)
            self.assertEqual(load(path), first)

    def test_invalid_legacy_link_does_not_overwrite_file(self):
        old = {"nodes": [{"id": "a", "x": 1, "y": 2}],
               "edges": [{"from": "a", "to": "missing"}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy-invalid.ovjson"
            path.write_text(json.dumps(old), encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                load(path)
            self.assertEqual(path.read_bytes(), before)
