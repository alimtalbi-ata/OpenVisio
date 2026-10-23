"""V42.76: every successfully saved JSON document must be reopenable.

Uses a lowered in-memory size ceiling to exercise the exact production gate
without allocating a 128 MiB fixture. Author: Abdelhalim Talbi.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openvisio import model


class SaveLoadSizeContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'topology.json'

    def test_oversized_new_document_is_not_published(self):
        with patch.object(model, 'MAX_DOCUMENT_BYTES', 256):
            with self.assertRaisesRegex(ValueError, 'trop volumineux'):
                model.save(self.path, {'nodes': [], 'edges': [],
                                       'metadata': {'notes': 'x' * 300}}, require_absent=True)
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.path.parent.glob('.openvisio-*.tmp')), [])

    def test_oversized_update_preserves_document_and_backup(self):
        original = {'nodes': [], 'edges': []}
        revision = model.save(self.path, original, require_absent=True)
        before = self.path.read_bytes()
        backup = self.path.with_name(self.path.name + '.bak')
        backup.write_bytes(b'known recovery copy')
        with patch.object(model, 'MAX_DOCUMENT_BYTES', 256):
            with self.assertRaisesRegex(ValueError, 'trop volumineux'):
                model.save(self.path, {'nodes': [], 'edges': [],
                                       'metadata': {'notes': 'x' * 300}},
                           expected_sha256=revision)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(backup.read_bytes(), b'known recovery copy')
        self.assertEqual(model.load(self.path), original)

    def test_boundary_save_roundtrips_and_revision_matches(self):
        doc = {'nodes': [], 'edges': [], 'metadata': {'notes': 'small'}}
        with patch.object(model, 'MAX_DOCUMENT_BYTES', 256):
            revision = model.save(self.path, doc, require_absent=True)
            self.assertEqual(model.load(self.path), doc)
            self.assertEqual(revision, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_serialized_size_not_source_string_length_is_checked(self):
        # ensure_ascii=False stores multibyte characters as UTF-8; the
        # actual published byte length, not Python str length, is the limit.
        doc = {'nodes': [], 'edges': [], 'metadata': {'notes': 'é' * 120}}
        with patch.object(model, 'MAX_DOCUMENT_BYTES', 256):
            with self.assertRaisesRegex(ValueError, 'trop volumineux'):
                model.save(self.path, doc, require_absent=True)
        self.assertFalse(self.path.exists())


if __name__ == '__main__':
    unittest.main()
