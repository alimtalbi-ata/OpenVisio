"""VSDX inspector must not treat JSON boolean as schema 1."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx_consistency import inspect

class InspectorSchemaTests(unittest.TestCase):
    def test_boolean_schema_is_rejected(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.vsdx"
            with ZipFile(path, "w") as archive:
                archive.writestr("openvisio/document.json", payload)
                archive.writestr("openvisio/manifest.json", json.dumps({
                    "schema": True, "sha256": hashlib.sha256(payload).hexdigest()
                }))
            with self.assertRaisesRegex(ValueError, "Intégrité"):
                inspect(path)
