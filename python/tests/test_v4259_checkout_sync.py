"""V42.59 checkout guard for the four recovered SAN/viewport source paths.

The expected Git blob hashes are measured from the cumulative V42.58 ZIP.
Author: Abdelhalim Talbi.
"""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "connector_geometry.py": "62809851434f39e787e62c97344f7fb3055c448c",
}
# V42.58 viewport blob 063d01ee... is a historical recovery baseline,
# not an immutable contract: V43.10 legitimately evolves zoom/scene fitting.
# Retain the historical value in documentation, while enforcing mirror parity
# for the active viewport source instead of pinning it to obsolete code.
EVOLVING = ("viewport.py",)
TESTS = {
    "test_connector_overflow_v4256.py": "6262a0c70e16e9ffba8bd54725b250a68cbfb734",
    "test_viewport_finite_v4257.py": "e3f70f30bd5a776fe31fd74f552c6ba6fd6739b1",
    "test_viewport_fit_atomic_v4255.py": "e9316deeec8488c5df6105779fc16efba5219ab6",
    "test_viewport_atomic_v4254.py": "b0adaaa6de96f256f952497a93b0375e6df55f06",
}


def blob_sha(path):
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class GitHubCheckoutSourceGuardTests(unittest.TestCase):
    def test_two_engine_paths_match_expected_zip_blobs(self):
        for filename, expected in EXPECTED.items():
            for directory in ("python/openvisio", "03-Sources/openvisio"):
                path = ROOT / directory / filename
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertTrue(path.is_file())
                    self.assertEqual(blob_sha(path), expected)

    def test_evolving_engine_paths_still_have_identical_blobs(self):
        for filename in EVOLVING:
            a = ROOT / "python/openvisio" / filename
            b = ROOT / "03-Sources/openvisio" / filename
            with self.subTest(filename=filename):
                self.assertTrue(a.is_file() and b.is_file())
                self.assertEqual(blob_sha(a), blob_sha(b))

    def test_regression_tests_match_expected_zip_blobs(self):
        for filename, expected in TESTS.items():
            path = ROOT / "python/tests" / filename
            with self.subTest(path=filename):
                self.assertTrue(path.is_file())
                self.assertEqual(blob_sha(path), expected)


if __name__ == "__main__":
    unittest.main()
