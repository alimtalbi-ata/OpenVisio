"""V42.75: inspector and importer must agree on VSDX manifest validity.

These tests use generated OPC ZIP packages, not Microsoft Visio desktop.
Author: Abdelhalim Talbi.
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_consistency import inspect, main


class VsdxManifestInspectorParityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "san-fabric.vsdx"
        export_vsdx(self.path, {
            "nodes": [{"id": "san-switch", "x": 20, "y": 30}],
            "edges": [],
        })

    def _manifest(self):
        with ZipFile(self.path) as archive:
            return archive.read("openvisio/manifest.json").decode("utf-8")

    def _replace_manifest(self, payload):
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        with ZipFile(self.path) as archive:
            parts = [(member.filename, archive.read(member.filename))
                     for member in archive.infolist()]
        with ZipFile(self.path, "w") as archive:
            for name, data in parts:
                archive.writestr(name, payload if name == "openvisio/manifest.json" else data)

    def _assert_rejected_by_both(self):
        with self.assertRaises(ValueError):
            import_vsdx(self.path)
        with self.assertRaises(ValueError):
            inspect(self.path)

    def test_duplicate_schema_rejected_by_inspector_and_importer(self):
        self._replace_manifest(self._manifest().replace(
            '"schema":', '"schema": 1, "schema":', 1))
        self._assert_rejected_by_both()

    def test_duplicate_digest_rejected_by_inspector_and_importer(self):
        self._replace_manifest(self._manifest().replace(
            '"sha256":', '"sha256": "0", "sha256":', 1))
        self._assert_rejected_by_both()

    def test_nonfinite_json_rejected_by_inspector_and_importer(self):
        self._replace_manifest(self._manifest().replace(
            '"schema":', '"unused": NaN, "schema":', 1))
        self._assert_rejected_by_both()

    def test_boolean_schema_rejected_by_inspector_and_importer(self):
        self._replace_manifest(self._manifest().replace('"schema": 3', '"schema": true', 1))
        self._assert_rejected_by_both()

    def test_valid_schema3_still_consistent(self):
        self.assertEqual(inspect(self.path)["status"], "consistent")
        self.assertEqual(import_vsdx(self.path)["nodes"][0]["id"], "san-switch")

    def test_corrupted_payload_status_is_preserved(self):
        manifest = json.loads(self._manifest())
        manifest["sha256"] = "0" * 64
        self._replace_manifest(json.dumps(manifest))
        self.assertEqual(inspect(self.path)["status"], "corrupted_payload")

    def test_cli_reports_invalid_manifest_as_error(self):
        self._replace_manifest(self._manifest().replace(
            '"schema":', '"schema": 1, "schema":', 1))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([str(self.path)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
