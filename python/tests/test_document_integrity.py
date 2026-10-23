"""Recovery integrity regression tests. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from openvisio.document_service import save_document, inspect_previous, restore_inspected

class IntegrityTests(unittest.TestCase):
    def test_backup_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'diagram.ovjson'
            first = {'nodes': [], 'edges': []}
            save_document(p, first)
            save_document(p, {'nodes': [{'id': 'a', 'x': 1, 'y': 2}], 'edges': []})
            doc, snap = inspect_previous(p)
            self.assertEqual(doc, first)
            self.assertEqual(restore_inspected(p, snap), first)
    def test_backup_changed_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'diagram.ovjson'
            save_document(p, {'nodes': [], 'edges': []})
            save_document(p, {'nodes': [{'id': 'a', 'x': 1, 'y': 2}], 'edges': []})
            _, snap = inspect_previous(p)
            Path(str(p) + '.bak').write_text('modified', encoding='utf-8')
            with self.assertRaises(RuntimeError):
                restore_inspected(p, snap)
    def test_wrong_document_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'a.ovjson'
            save_document(p, {'nodes': [], 'edges': []})
            save_document(p, {'nodes': [], 'edges': []})
            _, snap = inspect_previous(p)
            with self.assertRaises(ValueError):
                restore_inspected(Path(d) / 'b.ovjson', snap)
