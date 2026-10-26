"""Regression tests for exact Git blob verification of cumulative ZIPs."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "openvisio_git_parity", ROOT / "02-Compilation" / "verify_release_git_parity.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class GitBlobReleaseParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / "candidate.zip"
        self.files = {}
        for directory in AUDIT.ENGINE_DIRS:
            for name in AUDIT.REQUIRED_ENGINE:
                self.files[f"{directory}/{name}"] = f"# engine {name}\nVALUE = 1\n".encode()
            self.files[f"{directory}/helper.py"] = b"VALUE = 2\n"
        for directory in AUDIT.TEST_DIRS:
            self.files[f"{directory}/test_fixture.py"] = b"import unittest\n"
        for path in AUDIT.CRITICAL_FILES:
            self.files[path] = ("# fixture " + path + "\n").encode()
        mirror_test = b"# mirrored release-parity test\n"
        self.files["04-Tests/tests/test_release_git_parity_v4324.py"] = mirror_test
        self.files["python/tests/test_release_git_parity_v4324.py"] = mirror_test
        for left, right in zip(AUDIT.ENGINE_DIRS, AUDIT.ENGINE_DIRS[1:]):
            for relative in (name for name in self.files if name.startswith(left + "/")):
                self.files[right + relative[len(left):]] = self.files[relative]
        for left, right in zip(AUDIT.TEST_DIRS, AUDIT.TEST_DIRS[1:]):
            for relative in (name for name in self.files if name.startswith(left + "/")):
                self.files[right + relative[len(left):]] = self.files[relative]

    def tearDown(self):
        self.temp.cleanup()

    def _commit_repo(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "OpenVisio Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "ov-test@example.invalid"], cwd=self.root, check=True)
        for name, data in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        special = self.root / "folder with spaces" / "connector.txt"
        special.parent.mkdir(parents=True, exist_ok=True)
        special.write_bytes(b"tracked path with spaces\n")
        subprocess.run(["git", "add", "--all"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "test fixture"], cwd=self.root, check=True)
        return AUDIT.git_head(self.root)

    def _write_zip(self, head, mutate=None, omit=(), duplicate=None):
        payload = dict(self.files)
        if mutate:
            mutate(payload)
        for path in omit:
            payload.pop(path, None)
        manifest = {"project": "OpenVisio", "version": "V43.23",
                    "author": "Abdelhalim Talbi", "source_commit": head}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as out:
                for path, data in sorted(payload.items()):
                    out.writestr(path, data)
                out.writestr(AUDIT.MANIFEST_PATH, json.dumps(manifest).encode())
                if duplicate:
                    out.writestr(duplicate, payload[duplicate])

    def _audit(self):
        return AUDIT.audit_archive(self.archive, checkout_root=self.root, expected_version="V43.23")

    def test_real_git_tree_parser_handles_spaces_and_exact_blob_ids(self):
        self._commit_repo()
        blobs = AUDIT.git_tree_blobs(self.root)
        name = "folder with spaces/connector.txt"
        self.assertEqual(blobs[name], AUDIT.git_blob_sha(b"tracked path with spaces\n"))

    def test_real_checkout_and_exact_archive_pass(self):
        head = self._commit_repo()
        self._write_zip(head)
        report = self._audit()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["source_commit_expected"], report["source_commit_in_archive"])

    def test_post_commit_engine_drift_is_rejected_even_if_mirrors_match(self):
        head = self._commit_repo()
        def mutate(payload):
            for directory in AUDIT.ENGINE_DIRS:
                payload[directory + "/model.py"] = b"# changed after commit\n"
        self._write_zip(head, mutate=mutate)
        report = self._audit()
        self.assertFalse(report["ok"])
        self.assertTrue(any(x["path"].endswith("/model.py") for x in report["blob_mismatches"]))

    def test_missing_required_engine_module_is_rejected(self):
        head = self._commit_repo()
        self._write_zip(head, omit=("03-Sources/openvisio/render.py", "python/openvisio/render.py"))
        self.assertFalse(self._audit()["ok"])

    def test_untracked_engine_module_is_rejected(self):
        head = self._commit_repo()
        self._write_zip(head, mutate=lambda p: p.__setitem__("python/openvisio/untracked.py", b"x=1\n"))
        self.assertFalse(self._audit()["ok"])

    def test_divergent_mirrors_are_rejected(self):
        head = self._commit_repo()
        self._write_zip(head, mutate=lambda p: p.__setitem__("python/openvisio/vsdx.py", b"# diverged\n"))
        self.assertFalse(self._audit()["ok"])

    def test_manifest_commit_and_critical_metadata_are_bound(self):
        head = self._commit_repo()
        self._write_zip(head, mutate=lambda p: p.__setitem__(".gitattributes", b"*.py text eol=crlf\n"))
        self.assertFalse(self._audit()["ok"])
        self._write_zip("f" * 40)
        self.assertFalse(self._audit()["ok"])

    def test_duplicate_zip_path_is_rejected(self):
        head = self._commit_repo()
        self._write_zip(head, duplicate="03-Sources/openvisio/model.py")
        self.assertFalse(self._audit()["ok"])


if __name__ == "__main__":
    unittest.main()
