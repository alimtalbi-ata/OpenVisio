#!/usr/bin/env python3
"""Verify cumulative release bytes against the exact Git HEAD blobs.

The SHA-256 manifest inside a ZIP only proves consistency with itself. This
checker independently binds the packaged engine, test mirrors and release
inputs to the selected commit. Standard library only. Author: Abdelhalim Talbi.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Mapping

ENGINE_DIRS = ("03-Sources/openvisio", "python/openvisio")
TEST_DIRS = ("04-Tests/tests", "python/tests")
SCOPED_DIRS = ENGINE_DIRS + TEST_DIRS
REQUIRED_ENGINE = (
    "model.py", "vsdx.py", "render.py", "routing.py", "parallel_geometry.py",
    "validation.py", "vsdx_external.py", "vsdx_package.py", "visio_route.py",
)
MANIFEST_PATH = "07-Manifestes/manifest.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
CRITICAL_FILES = (
    ".gitattributes", "README.md", "verify_source_parity.py",
    ".github/workflows/openvisio-v43.26-windows-candidate.yml",
    "02-Compilation/verify_release_archive.py",
    "02-Compilation/verify_release_git_parity.py",
    "02-Compilation/Build-Windows-V43.26-Candidate.ps1",
    "02-Compilation/Verify-GitHub-Checkout-V43.26.ps1",
    "02-Compilation/package_cumulative_release_v4326.py",
    "02-Compilation/generate_release_docs_v4326.py",
    "02-Compilation/release_document_guard_v4326.py",
    "02-Compilation/requirements-build.txt",
    "02-Compilation/installer/OpenVisio-V43.26-Candidate.iss",
    "05-Documentation/V43.24-STATIC-VSDX-ROUTE-ATTACHMENT.md",
    "05-Documentation/V43.24-VSDX-ENDPOINT-ATTACHMENT.svg",
    "04-Tests/tests/test_vsdx_route_endpoint_attachment_v4324.py",
    "python/tests/test_vsdx_route_endpoint_attachment_v4324.py",
    "05-Documentation/V43.25-GIT-BLOB-PARITY.md",
    "05-Documentation/V43.25-STATIC-VSDX-ROUTE-PREFILTER.md",
    "05-Documentation/V43.25-STATIC-VSDX-ROUTE-PREFILTER.svg",
    "05-Documentation/V43.25-WINDOWS-SCREENSHOTS-STATUS.md",
    "04-Tests/tests/test_vsdx_route_spatial_prefilter_v4325.py",
    "python/tests/test_vsdx_route_spatial_prefilter_v4325.py",
    "04-Tests/tests/test_vsdx_route_segment_prefilter_v4325.py",
    "python/tests/test_vsdx_route_segment_prefilter_v4325.py",
    "05-Documentation/V43.26-GIT-BLOB-PARITY.md",
    "05-Documentation/V43.26-INFRASTRUCTURE-GLYPHS.md",
    "05-Documentation/V43.26-INFRASTRUCTURE-GLYPHS.svg",
    "05-Documentation/V43.26-WINDOWS-SCREENSHOTS-STATUS.md",
    "04-Tests/tests/test_shape_icons_v4292.py",
    "python/tests/test_shape_icons_v4292.py",
    "04-Tests/tests/test_infrastructure_glyph_details_v4326.py",
    "python/tests/test_infrastructure_glyph_details_v4326.py",
    "04-Tests/tests/test_release_git_parity_v4324.py",
    "python/tests/test_release_git_parity_v4324.py",
)


def git_blob_sha(payload: bytes) -> str:
    header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
    return hashlib.sha1(header + payload).hexdigest()


def git_head(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    head = result.stdout.strip().lower()
    if not HEX40.fullmatch(head):
        raise ValueError("Git HEAD is not a full SHA-1")
    return head


def git_tree_blobs(root: Path) -> dict[str, str]:
    result = subprocess.run(["git", "ls-tree", "-rz", "--full-tree", "HEAD"], cwd=root,
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    blobs: dict[str, str] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split(" ")
        if kind == "blob":
            blobs[raw_path.decode("utf-8", "surrogateescape")] = oid.lower()
    return blobs


def _under(path: str, directory: str) -> bool:
    return path.startswith(directory.rstrip("/") + "/")


def _read_zip(path: Path) -> tuple[dict[str, bytes], list[str]]:
    payload: dict[str, bytes] = {}
    errors: list[str] = []
    with zipfile.ZipFile(path, "r") as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        if len(names) != len(set(names)):
            errors.append("ZIP contains duplicate file paths")
        bad = archive.testzip()
        if bad is not None:
            errors.append("ZIP CRC failure: " + bad)
        for item in archive.infolist():
            if item.is_dir() or item.filename in payload:
                continue
            payload[item.filename] = archive.read(item)
    return payload, errors


def audit_archive(archive: Path, *, checkout_root: Path, expected_version: str | None = None,
                  git_head_override: str | None = None,
                  git_tree_override: Mapping[str, str] | None = None) -> dict:
    root = Path(checkout_root)
    head = (git_head_override or git_head(root)).lower()
    tree = dict(git_tree_override) if git_tree_override is not None else git_tree_blobs(root)
    payload, errors = _read_zip(Path(archive))
    mismatches: list[dict[str, str]] = []
    manifest: dict = {}
    try:
        manifest = json.loads(payload[MANIFEST_PATH].decode("utf-8"))
    except KeyError:
        errors.append("Release manifest is missing")
    except (UnicodeDecodeError, json.JSONDecodeError):
        errors.append("Release manifest is invalid JSON/UTF-8")
    if manifest:
        if manifest.get("project") != "OpenVisio":
            errors.append("Manifest project mismatch")
        if manifest.get("author") != "Abdelhalim Talbi":
            errors.append("Manifest author mismatch")
        if expected_version and manifest.get("version") != expected_version:
            errors.append("Manifest version mismatch")
        embedded = manifest.get("source_commit")
        if not isinstance(embedded, str) or not HEX40.fullmatch(embedded) or embedded != head:
            errors.append("Manifest source_commit does not equal Git HEAD")

    checked = 0
    counts = {}
    for directory in SCOPED_DIRS:
        expected = {p for p in tree if _under(p, directory)}
        packaged = {p for p in payload if _under(p, directory)}
        counts[directory] = {"git_files": len(expected), "archive_files": len(packaged)}
        if not expected:
            errors.append("Git source directory missing: " + directory)
        for missing in sorted(expected - packaged):
            errors.append("Tracked source/test file missing from ZIP: " + missing)
        for extra in sorted(packaged - expected):
            errors.append("Untracked source/test file in ZIP: " + extra)
        for path in sorted(expected & packaged):
            checked += 1
            actual, expected_oid = git_blob_sha(payload[path]), tree[path]
            if actual != expected_oid:
                mismatches.append({"path": path, "expected_git_blob": expected_oid,
                                   "archive_git_blob": actual})
                errors.append("Git blob mismatch in ZIP: " + path)

    for directory in ENGINE_DIRS:
        for name in REQUIRED_ENGINE:
            path = directory + "/" + name
            if path not in tree or path not in payload:
                errors.append("Required engine module missing: " + path)

    for path in CRITICAL_FILES:
        if path not in tree:
            errors.append("Critical release input is not tracked: " + path)
        if path not in payload:
            errors.append("Critical release input is missing from ZIP: " + path)
        if path in tree and path in payload:
            checked += 1
            actual, expected_oid = git_blob_sha(payload[path]), tree[path]
            if actual != expected_oid:
                mismatches.append({"path": path, "expected_git_blob": expected_oid,
                                   "archive_git_blob": actual})
                errors.append("Git blob mismatch in critical release input: " + path)

    for left, right, label in ((ENGINE_DIRS[0], ENGINE_DIRS[1], "engine"),
                               (TEST_DIRS[0], TEST_DIRS[1], "test")):
        lhs = {p[len(left) + 1:] for p in payload if _under(p, left)}
        rhs = {p[len(right) + 1:] for p in payload if _under(p, right)}
        if lhs != rhs:
            errors.append("Mirror path sets differ: " + label)
        for rel in sorted(lhs & rhs):
            if payload[left + "/" + rel] != payload[right + "/" + rel]:
                errors.append("Mirror bytes differ: " + label + "/" + rel)

    return {"ok": not errors, "archive": str(archive), "expected_version": expected_version,
            "source_commit_expected": head, "source_commit_in_archive": manifest.get("source_commit"),
            "git_tracked_blobs": len(tree), "scoped_files": counts,
            "checked_archive_blobs": checked, "blob_mismatches": mismatches,
            "errors": errors[:100]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--checkout", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="V43.26")
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = audit_archive(args.archive, checkout_root=args.checkout, expected_version=args.version)
    except (OSError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        report = {"ok": False, "archive": str(args.archive), "errors": [str(exc)]}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(rendered, encoding="utf-8")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
