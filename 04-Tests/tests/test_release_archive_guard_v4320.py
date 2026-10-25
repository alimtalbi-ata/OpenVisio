"""Synthetic source-release guard regressions. Author: Abdelhalim Talbi."""
import hashlib, importlib.util, json, sys, tempfile, unittest, warnings
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_release_archive", ROOT / "02-Compilation" / "verify_release_archive.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("release archive guard cannot be loaded")
GUARD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GUARD
SPEC.loader.exec_module(GUARD)

VERSION = "V43.20"
ENGINE = {
    "model.py": b"# model\n",
    "vsdx.py": b"# package\n",
    "render.py": b"# renderer\n",
    "routing.py": b"# router\n",
    "parallel_geometry.py": b"# lane geometry\n",
}


def build_zip(path, *, version=VERSION, changed_mirror=False, missing_dependency=False,
              missing_checksum=False, corrupt_hash=False, duplicate_path=False,
              traversal=False, noncanonical_path=False, unsafe_member=None):
    payload = {}
    for name, data in ENGINE.items():
        if missing_dependency and name == "routing.py":
            continue
        payload[f"03-Sources/openvisio/{name}"] = data
        payload[f"python/openvisio/{name}"] = data
    payload["04-Tests/tests/test_contract.py"] = b"# test\n"
    payload["python/tests/test_contract.py"] = b"# test\n"
    if changed_mirror:
        payload["python/openvisio/render.py"] = b"# stale renderer\n"
    checksum_name = "07-Manifestes/SHA256SUMS-V43.20.txt"
    manifest = {
        "project": "OpenVisio",
        "version": version,
        "author": "Abdelhalim Talbi",
        "windows_qualified": False,
        "microsoft_visio_qualified": False,
        "file_hash_manifest": "07-Manifestes/SHA256SUMS.txt" if missing_checksum else checksum_name,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())},
    }
    payload["07-Manifestes/manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    lines = []
    for name, data in sorted(payload.items()):
        digest = hashlib.sha256(data).hexdigest()
        if corrupt_hash and name == "03-Sources/openvisio/model.py":
            digest = "0" * 64
        lines.append(f"{digest}  {name}\n")
    payload[checksum_name] = "".join(lines).encode()
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            archive.writestr(name, data)
        if duplicate_path:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr("03-Sources/openvisio/model.py", b"duplicate")
        if traversal:
            archive.writestr("../outside.py", b"unsafe")
        if noncanonical_path:
            # PurePosixPath would normalize away this raw dot segment.
            archive.writestr("03-Sources/./openvisio/alias.py", b"unsafe")
        if unsafe_member is not None:
            archive.writestr(unsafe_member, b"unsafe")


class ReleaseArchiveGuardTests(unittest.TestCase):
    def audit(self, folder, **kwargs):
        path = Path(folder) / "test.zip"
        manifest_version = kwargs.pop("version", VERSION)
        build_zip(path, version=manifest_version, **kwargs)
        # Always compare against the expected release, not the version supplied
        # to the synthetic archive. This is essential to test version rejection.
        return GUARD.audit_archive(path, VERSION)

    def test_valid_archive_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["details"]["engine_files"], len(ENGINE))

    def test_old_manifest_cannot_pass_for_new_release(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, version="V42.8-partial-embedded-candidate")
        self.assertFalse(report["ok"])
        self.assertTrue(any("Version incohérente" in err for err in report["errors"]))

    def test_missing_engine_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, missing_dependency=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("routing.py" in err for err in report["errors"]))

    def test_divergent_engine_mirrors_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, changed_mirror=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("render.py" in err and "divergent" in err for err in report["errors"]))

    def test_missing_hash_manifest_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, missing_checksum=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("fichier de sommes SHA-256 référencé absent" in err for err in report["errors"]))

    def test_wrong_sha256_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, corrupt_hash=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("empreinte incorrecte" in err for err in report["errors"]))

    def test_duplicate_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, duplicate_path=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("dupliqués" in err for err in report["errors"]))

    def test_zip_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            report = self.audit(folder, traversal=True)
        self.assertFalse(report["ok"])
        self.assertTrue(any("chemin non sûr" in err for err in report["errors"]))


    def test_windows_reserved_names_trailing_aliases_and_metacharacters_are_rejected(self):
        unsafe_names = (
            "03-Sources/openvisio/CON", "03-Sources/openvisio/NUL.txt",
            "03-Sources/openvisio/COM1.log", "03-Sources/openvisio/LPT³.data",
            "03-Sources/openvisio/trailing-dot.", "03-Sources/openvisio/trailing-space ",
            "03-Sources/openvisio/bad?.py", "03-Sources/openvisio/control\x01.py",
        )
        for member in unsafe_names:
            with self.subTest(member=member), tempfile.TemporaryDirectory() as folder:
                report = self.audit(folder, unsafe_member=member)
            self.assertFalse(report["ok"], member)
            self.assertTrue(any("chemin non sûr" in err for err in report["errors"]), report["errors"])

    def test_windows_casefold_and_file_directory_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.zip"
            build_zip(path)
            with ZipFile(path, "a", ZIP_DEFLATED) as archive:
                archive.writestr("03-Sources/openvisio/MODEL.PY", b"case alias")
                archive.writestr("alias-folder/", b"")
                archive.writestr("alias-folder", b"file alias")
            report = GUARD.audit_archive(path, VERSION)
        self.assertFalse(report["ok"])
        self.assertTrue(any("dupliqués ou aliasés" in err for err in report["errors"]), report["errors"])

    def test_noncanonical_raw_path_segments_are_rejected(self):
        for spelling in ("dot segment", "repeated separator"):
            with self.subTest(spelling=spelling), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "test.zip"
                build_zip(path)
                alias = ("03-Sources/./openvisio/alias.py" if spelling == "dot segment"
                         else "03-Sources//openvisio/alias.py")
                with ZipFile(path, "a", ZIP_DEFLATED) as archive:
                    archive.writestr(alias, b"unsafe")
                report = GUARD.audit_archive(path, VERSION)
                self.assertFalse(report["ok"])
                self.assertTrue(any("chemin non sûr" in err for err in report["errors"]))


if __name__ == "__main__":
    unittest.main()
