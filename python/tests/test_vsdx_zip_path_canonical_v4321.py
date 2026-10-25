"""V43.21 regressions for canonical VSDX package member paths."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openvisio.vsdx import import_vsdx


DOCUMENT = b'{"nodes":[],"edges":[]}'
MANIFEST = json.dumps({
    "schema": 1,
    "sha256": hashlib.sha256(DOCUMENT).hexdigest(),
}, separators=(",", ":")).encode("utf-8")


def make_vsdx(path, extra_member=None):
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("openvisio/document.json", DOCUMENT)
        archive.writestr("openvisio/manifest.json", MANIFEST)
        if extra_member is not None:
            archive.writestr(extra_member, b"alias")


class VsdxCanonicalMemberPathTests(unittest.TestCase):
    def test_canonical_embedded_document_is_imported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "valid.vsdx"
            make_vsdx(path)
            result = import_vsdx(path)
        self.assertEqual(result["nodes"], [])
        self.assertEqual(result["edges"], [])

    def test_dot_segment_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dot-alias.vsdx"
            make_vsdx(path, "openvisio/./document.json")
            with self.assertRaisesRegex(ValueError, "Entrée VSDX non sûre"):
                import_vsdx(path)

    def test_repeated_separator_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty-segment.vsdx"
            make_vsdx(path, "openvisio//manifest.json")
            with self.assertRaisesRegex(ValueError, "Entrée VSDX non sûre"):
                import_vsdx(path)

    def test_case_insensitive_member_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "case-alias.vsdx"
            make_vsdx(path, "OPENVisio/MANIFEST.json")
            with self.assertRaisesRegex(ValueError, "Entrées VSDX dupliquées ou aliasées"):
                import_vsdx(path)

    def test_windows_alternate_stream_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alternate-stream.vsdx"
            make_vsdx(path, "openvisio/manifest.json:payload")
            with self.assertRaisesRegex(ValueError, "Entrée VSDX non sûre"):
                import_vsdx(path)

    def test_windows_reserved_device_names_trailing_aliases_and_illegal_chars_are_rejected(self):
        unsafe_members = (
            "openvisio/CON", "openvisio/NUL.txt", "visio/COM1.xml", "visio/LPT³.xml",
            "openvisio/name.", "openvisio/name ", "visio/bad?.xml", "visio/control\x01.xml",
        )
        for member in unsafe_members:
            with self.subTest(member=member), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "unsafe-member.vsdx"
                make_vsdx(path, member)
                with self.assertRaisesRegex(ValueError, "Entrée VSDX non sûre"):
                    import_vsdx(path)


if __name__ == "__main__":
    unittest.main()
