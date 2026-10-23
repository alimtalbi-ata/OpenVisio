"""V42.78: VSDX inspection must not certify embedded diagrams import rejects.

Synthetic OPC archives only, not Microsoft Visio desktop interoperability.
Author: Abdelhalim Talbi.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_consistency import inspect


class EmbeddedPayloadInspectorParityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "diagram.vsdx"
        export_vsdx(self.path, {"nodes": [{"id": "esxi", "x": 0, "y": 0}], "edges": []})

    def _rewrite_payload_and_matching_manifest(self, payload):
        with ZipFile(self.path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        manifest = json.loads(parts["openvisio/manifest.json"])
        manifest["sha256"] = hashlib.sha256(payload).hexdigest()
        parts["openvisio/document.json"] = payload
        parts["openvisio/manifest.json"] = json.dumps(manifest).encode("utf-8")
        with ZipFile(self.path, "w") as archive:
            for name, data in parts.items():
                archive.writestr(name, data)

    def _assert_rejected_by_both(self, payload):
        self._rewrite_payload_and_matching_manifest(payload)
        with self.assertRaises(ValueError):
            import_vsdx(self.path)
        with self.assertRaisesRegex(ValueError, "Document OpenVisio embarqué invalide"):
            inspect(self.path)

    def test_invalid_json_with_matching_sha_is_not_consistent(self):
        self._assert_rejected_by_both(b'{"nodes": [')

    def test_duplicate_node_ids_with_matching_sha_are_not_consistent(self):
        self._assert_rejected_by_both(b'{"nodes":[{"id":"n","x":0,"y":0},{"id":"n","x":1,"y":0}],"edges":[]}')

    def test_duplicate_json_keys_with_matching_sha_are_not_consistent(self):
        self._assert_rejected_by_both(b'{"nodes":[],"nodes":[],"edges":[]}')

    def test_invalid_link_with_matching_sha_is_not_consistent(self):
        self._assert_rejected_by_both(b'{"nodes":[],"edges":[{"id":"fc","from":"missing","to":"other"}]}')

    def test_valid_payload_still_importable_and_consistent(self):
        self.assertEqual(inspect(self.path)["status"], "consistent")
        self.assertEqual(import_vsdx(self.path)["nodes"][0]["id"], "esxi")


if __name__ == "__main__":
    unittest.main()
