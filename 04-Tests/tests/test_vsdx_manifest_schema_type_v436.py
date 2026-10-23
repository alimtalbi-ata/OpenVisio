"""Manifest schema must be a JSON integer, never a boolean (True == 1 in Python)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx import import_vsdx

class ManifestSchemaTypeTests(unittest.TestCase):
    def test_boolean_schema_rejected(self):
        payload = b'{"nodes":[],"edges":[]}'
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "boolean-schema.vsdx"
            manifest = {"schema": True, "sha256": hashlib.sha256(payload).hexdigest()}
            with ZipFile(filename, "w") as archive:
                archive.writestr("openvisio/document.json", payload)
                archive.writestr("openvisio/manifest.json", json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Intégrité"):
                import_vsdx(filename)
