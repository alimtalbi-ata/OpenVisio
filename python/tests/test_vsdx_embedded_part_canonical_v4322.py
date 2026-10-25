"""V43.22 regression: private OpenVisio OPC part paths must be canonical.

Synthetic VSDX fixtures only; this is not Microsoft Visio Desktop qualification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from openvisio.vsdx import export_vsdx, import_vsdx


def _sample_document():
    return {
        "nodes": [
            {"id": "host-1", "x": 24, "y": 48, "shape": "server", "label": "ESXi host"},
            {"id": "array-1", "x": 260, "y": 48, "shape": "storage", "label": "FlashArray"},
        ],
        "edges": [{"id": "fc-a", "from": "host-1", "to": "array-1",
                   "protocol": "FC", "source_port": "vmhba1", "target_port": "ct0.fc1",
                   "fabric": "A"}],
        "metadata": {"service_owner": "Storage Architecture", "preserve_exactly": True},
    }


def _write_case_alias(source, destination, aliases):
    with ZipFile(source, "r") as reader, ZipFile(destination, "w", ZIP_DEFLATED) as writer:
        for info in reader.infolist():
            name = aliases.get(info.filename, info.filename)
            writer.writestr(name, reader.read(info.filename))


class VsdxEmbeddedPartCanonicalNameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.original = self.root / "canonical.vsdx"
        self.document = _sample_document()
        export_vsdx(self.original, self.document)

    def tearDown(self):
        self.temp.cleanup()

    def test_canonical_private_payload_preserves_editor_metadata(self):
        imported = import_vsdx(self.original)
        self.assertEqual(imported["metadata"], self.document["metadata"])
        self.assertEqual(imported["nodes"], self.document["nodes"])
        self.assertEqual(imported["edges"], self.document["edges"])

    def test_case_variant_document_part_is_rejected_not_flattened(self):
        aliased = self.root / "document-case-alias.vsdx"
        _write_case_alias(self.original, aliased, {
            "openvisio/document.json": "OpenVisio/Document.json",
        })
        with self.assertRaisesRegex(ValueError, "Nom de partie OpenVisio non canonique"):
            import_vsdx(aliased)

    def test_case_variant_manifest_part_is_rejected_not_flattened(self):
        aliased = self.root / "manifest-case-alias.vsdx"
        _write_case_alias(self.original, aliased, {
            "openvisio/manifest.json": "openvisio/Manifest.json",
        })
        with self.assertRaisesRegex(ValueError, "Nom de partie OpenVisio non canonique"):
            import_vsdx(aliased)

    def test_both_case_variant_parts_cannot_bypass_lossless_import(self):
        aliased = self.root / "both-case-alias.vsdx"
        _write_case_alias(self.original, aliased, {
            "openvisio/document.json": "OpenVisio/Document.json",
            "openvisio/manifest.json": "OpenVisio/Manifest.json",
        })
        with self.assertRaisesRegex(ValueError, "Nom de partie OpenVisio non canonique"):
            import_vsdx(aliased)

    def test_case_exact_parts_are_not_affected_by_guard(self):
        imported = import_vsdx(self.original)
        self.assertTrue(imported["metadata"]["preserve_exactly"])
        self.assertEqual(len(imported["edges"]), 1)


if __name__ == "__main__":
    unittest.main()
