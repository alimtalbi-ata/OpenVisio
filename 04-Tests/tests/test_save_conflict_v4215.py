"""V42.15 data-loss regression tests for concurrent diagram edits. Abdelhalim Talbi."""
import tempfile
import subprocess
import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from openvisio.autosave import digest_file
from openvisio.document_service import save_document
from openvisio.model import SaveConflict, load, save
from openvisio.app import Editor


class SaveConflictTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'diagram.ovjson'
        self.first = {'nodes': [{'id': 'first', 'x': 1, 'y': 2}], 'edges': []}
        self.second = {'nodes': [{'id': 'second', 'x': 3, 'y': 4}], 'edges': []}
        self.third = {'nodes': [{'id': 'external', 'x': 5, 'y': 6}], 'edges': []}

    def test_normal_save_preserves_backup_and_revision(self):
        save(self.path, self.first)
        expected = digest_file(self.path)
        save_document(self.path, self.second, expected_sha256=expected)
        self.assertEqual(load(self.path), self.second)
        self.assertEqual(load(Path(str(self.path) + '.bak')), self.first)

    def test_external_change_refuses_save_without_changing_backup(self):
        save(self.path, self.first)
        expected = digest_file(self.path)
        save(self.path, self.third)
        backup = Path(str(self.path) + '.bak')
        old_backup = backup.read_bytes()
        with self.assertRaisesRegex(SaveConflict, 'modifié'):
            save_document(self.path, self.second, expected_sha256=expected)
        self.assertEqual(load(self.path), self.third)
        self.assertEqual(backup.read_bytes(), old_backup)

    def test_independent_process_change_is_not_overwritten(self):
        save(self.path, self.first)
        expected = digest_file(self.path)
        source = (
            "from openvisio.model import save; import sys; "
            "save(sys.argv[1], {'nodes':[{'id':'child','x':42,'y':42}],'edges':[]})"
        )
        env = dict(os.environ)
        env['PYTHONPATH'] = str(Path(__file__).resolve().parents[2] / '03-Sources')
        result = subprocess.run([sys.executable, '-c', source, str(self.path)],
                                env=env, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        with self.assertRaises(SaveConflict):
            save_document(self.path, self.second, expected_sha256=expected)
        self.assertEqual(load(self.path)['nodes'][0]['id'], 'child')

    def test_missing_document_refuses_save(self):
        save(self.path, self.first)
        expected = digest_file(self.path)
        self.path.unlink()
        with self.assertRaisesRegex(SaveConflict, 'disparu'):
            save_document(self.path, self.second, expected_sha256=expected)
        self.assertFalse(self.path.exists())

    def test_save_as_new_target_rejects_file_created_after_selection(self):
        save(self.path, self.third)
        with self.assertRaisesRegex(SaveConflict, 'créé'):
            save_document(self.path, self.second, require_absent=True)
        self.assertEqual(load(self.path), self.third)

    def test_save_as_new_target_succeeds_when_absent(self):
        save_document(self.path, self.second, require_absent=True)
        self.assertEqual(load(self.path), self.second)

    def test_change_during_backup_is_detected_before_replace(self):
        import shutil
        save(self.path, self.first)
        expected = digest_file(self.path)
        backup = Path(str(self.path) + '.bak')
        backup.write_bytes(b'PREVIOUS RECOVERY COPY')
        original_copy = shutil.copyfileobj

        def concurrent_copy(source, target, *args, **kwargs):
            result = original_copy(source, target, *args, **kwargs)
            self.path.write_text('external edit wins', encoding='utf-8')
            return result

        with patch('shutil.copyfileobj', side_effect=concurrent_copy):
            with self.assertRaises(SaveConflict):
                save_document(self.path, self.second, expected_sha256=expected)
        self.assertEqual(self.path.read_text(encoding='utf-8'), 'external edit wins')
        self.assertEqual(backup.read_bytes(), b'PREVIOUS RECOVERY COPY')

    def test_editor_save_keeps_dirty_state_after_conflict(self):
        save(self.path, self.first)
        expected = digest_file(self.path)
        save(self.path, self.third)
        class Stub:
            current_path = str(self.path)
            _saved_disk_digest = expected
            document = self.second
            saved_snapshot = 'previous'
            status = Mock()
            _refresh_document_status = Mock()
            _snapshot = lambda self: 'dirty'
        stub = Stub()
        with patch('openvisio.app.messagebox.showerror') as showerror:
            Editor.store(stub)
        showerror.assert_called_once()
        self.assertEqual(stub.saved_snapshot, 'previous')
        self.assertEqual(stub._saved_disk_digest, expected)
        self.assertEqual(load(self.path), self.third)

    def test_invalid_preconditions_do_not_write(self):
        with self.assertRaisesRegex(ValueError, 'incompatibles'):
            save(self.path, self.second, expected_sha256='0' * 64, require_absent=True)
        with self.assertRaisesRegex(ValueError, 'invalide'):
            save(self.path, self.second, expected_sha256='garbage')
        self.assertFalse(self.path.exists())

if __name__ == '__main__':
    unittest.main()
