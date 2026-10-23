"""V42.74: reject ambiguous embedded VSDX manifest metadata.
Author: Abdelhalim Talbi. Synthetic VSDX tests; not Microsoft Visio fidelity.
"""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openvisio.vsdx import export_vsdx, import_vsdx


class ManifestIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fabric.vsdx"
        export_vsdx(self.path, {"nodes": [{"id": "sw1", "x": 10, "y": 20}], "edges": []})

    def _replace_manifest(self, data):
        with ZipFile(self.path) as source:
            contents = [(entry.filename, source.read(entry.filename)) for entry in source.infolist()]
        with ZipFile(self.path, "w") as dest:
            for name, payload in contents:
                dest.writestr(name, data if name == "openvisio/manifest.json" else payload)

    def test_duplicate_schema_rejected(self):
        with ZipFile(self.path) as z:
            original = z.read("openvisio/manifest.json").decode("utf-8")
        self._replace_manifest(original.replace('"schema":', '"schema": 1, "schema":', 1))
        with self.assertRaisesRegex(ValueError, "Manifeste.*JSON invalide"):
            import_vsdx(self.path)

    def test_duplicate_digest_rejected(self):
        with ZipFile(self.path) as z:
            manifest = json.loads(z.read("openvisio/manifest.json"))
        data = json.dumps(manifest)
        self._replace_manifest(data.replace('"sha256":', '"sha256": "0", "sha256":', 1))
        with self.assertRaisesRegex(ValueError, "Manifeste.*JSON invalide"):
            import_vsdx(self.path)

    def test_nonfinite_manifest_rejected(self):
        with ZipFile(self.path) as z:
            manifest = json.loads(z.read("openvisio/manifest.json"))
        manifest["unexpected"] = float("nan")
        self._replace_manifest(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Manifeste.*JSON invalide"):
            import_vsdx(self.path)

    def test_valid_manifest_roundtrip(self):
        document = import_vsdx(self.path)
        self.assertEqual(document["nodes"][0]["id"], "sw1")
