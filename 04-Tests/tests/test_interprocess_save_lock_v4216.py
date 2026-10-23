"""V42.16 real process-lock and no-clobber persistence regressions.

Author: Abdelhalim Talbi.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from openvisio.autosave import digest_file
from openvisio.model import SaveConflict, load, save
from openvisio.save_lock import exclusive_document_lock, lock_path


class InterprocessSaveLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "diagram.ovjson"
        self.old = {"nodes": [{"id": "old", "x": 1, "y": 1}], "edges": []}
        self.new = {"nodes": [{"id": "new", "x": 2, "y": 2}], "edges": []}

    def _lock_holder(self):
        script = (
            "import sys; from openvisio.save_lock import exclusive_document_lock; "
            "\nwith exclusive_document_lock(sys.argv[1]):\n"
            " print('LOCKED',flush=True)\n sys.stdin.readline()\n"
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "03-Sources")
        process = subprocess.Popen(
            [sys.executable, "-c", script, str(self.target)],
            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
        def cleanup():
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()
        self.addCleanup(cleanup)
        self.assertEqual(process.stdout.readline().strip(), "LOCKED")
        return process

    def test_second_process_cannot_save_while_first_holds_lock(self):
        save(self.target, self.old)
        expected = digest_file(self.target)
        process = self._lock_holder()
        with self.assertRaisesRegex(SaveConflict, "utilisé par une autre instance"):
            save(self.target, self.new, expected_sha256=expected, lock_timeout=0.12)
        self.assertEqual(load(self.target), self.old)
        process.stdin.write("\n")
        process.stdin.flush()
        self.assertEqual(process.wait(timeout=5), 0, process.stderr.read())
        save(self.target, self.new, expected_sha256=expected)
        self.assertEqual(load(self.target), self.new)

    def test_lock_file_persists_to_prevent_inode_split_brain(self):
        save(self.target, self.old)
        first = lock_path(self.target)
        self.assertTrue(first.is_file())
        stat_before = first.stat().st_ino
        save(self.target, self.new)
        self.assertEqual(first.stat().st_ino, stat_before)
        self.assertEqual(lock_path(self.target.parent / "." / self.target.name), first)

    def test_no_clobber_if_external_writer_creates_target_at_publish(self):
        real_link = os.link
        def inject_other_writer(source, destination):
            self.target.write_text("external new file", encoding="utf-8")
            return real_link(source, destination)
        with patch("os.link", side_effect=inject_other_writer):
            with self.assertRaises(SaveConflict):
                save(self.target, self.new, require_absent=True)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "external new file")
        self.assertFalse(Path(str(self.target) + ".bak").exists())
        self.assertEqual(list(self.target.parent.glob(".openvisio-*.tmp")), [])

    def test_lock_timeout_validation_is_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Délai"):
            save(self.target, self.new, lock_timeout=-1)
        self.assertFalse(self.target.exists())

    def test_backup_remains_previous_version_under_lock(self):
        save(self.target, self.old)
        expected = digest_file(self.target)
        save(self.target, self.new, expected_sha256=expected)
        self.assertEqual(load(self.target), self.new)
        self.assertEqual(load(Path(str(self.target) + ".bak")), self.old)


if __name__ == "__main__":
    unittest.main()
