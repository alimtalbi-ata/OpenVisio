#!/usr/bin/env python3
"""Create and independently validate one cumulative OpenVisio Windows ZIP.
Only binaries already built and smoke-tested by the caller are accepted.
Author: Abdelhalim Talbi.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

VERSION = "V43.24"
AUTHOR = "Abdelhalim Talbi"
ENGINE_DIRS = ("03-Sources/openvisio", "python/openvisio")
TEST_DIRS = ("04-Tests/tests", "python/tests")
ALLOWED_COMPILATION = {".py", ".ps1", ".iss", ".txt", ".md", ".cmd", ".bat", ".yml"}
ALLOWED_DOCS = {".md", ".svg", ".json", ".txt"}
BINARY_MIN_BYTES = 1_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise SystemExit("Git commit SHA is not a full hexadecimal commit")
    return value


def safe_archive_path(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/") or name.endswith("/"):
        return False
    parts = name.split("/")
    return (all(part not in ("", ".", "..") for part in parts)
            and not any(":" in part for part in parts))


def add_tree(root: Path, tree: str, allowed: set[str] | None = None) -> dict[str, bytes]:
    base = root / tree
    if not base.is_dir():
        raise SystemExit(f"Required source directory absent: {tree}")
    out = {}
    for file in sorted(base.rglob("*")):
        if not file.is_file() or file.is_symlink():
            continue
        if any(part in ("__pycache__", ".pytest_cache", "dist") for part in file.parts):
            continue
        if file.suffix.lower() in (".pyc", ".pyo"):
            continue
        if allowed is not None and file.suffix.lower() not in allowed:
            continue
        name = file.relative_to(root).as_posix()
        if not safe_archive_path(name):
            raise SystemExit(f"Unsafe source path: {name}")
        out[name] = file.read_bytes()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--portable", required=True, type=Path)
    parser.add_argument("--installer", required=True, type=Path)
    parser.add_argument("--qualification-json", required=True, type=Path)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--document-qa-json", required=True, type=Path)
    parser.add_argument("--document-qa-renders", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    portable = args.portable.resolve()
    installer = args.installer.resolve()
    qualification_path = args.qualification_json.resolve()
    docx_path, pdf_path = args.docx.resolve(), args.pdf.resolve()
    qa_json_path, qa_renders = args.document_qa_json.resolve(), args.document_qa_renders.resolve()

    for binary in (portable, installer):
        if not binary.is_file() or binary.stat().st_size < BINARY_MIN_BYTES:
            raise SystemExit(f"Missing or implausibly small built Windows binary: {binary}")
    report = json.loads(qualification_path.read_text(encoding="utf-8"))
    if report.get("version") != VERSION or report.get("author") != AUTHOR:
        raise SystemExit("Qualification report version/author mismatch")
    if not all(report.get(field) == "PASS" for field in (
        "checkout_and_parity", "portable_smoke", "installer_smoke", "archive_source_guard"
    )):
        raise SystemExit("Refusing to package before all required candidate qualification gates pass")
    if report.get("microsoft_visio_desktop") != "NOT_TESTED":
        raise SystemExit("Microsoft Visio status must remain explicitly unqualified")
    if not docx_path.is_file() or not pdf_path.is_file() or not qa_json_path.is_file():
        raise SystemExit("Qualified release documentation is absent")
    qa = json.loads(qa_json_path.read_text(encoding="utf-8"))
    if qa.get("pdf_render_status") != "PASS" or qa.get("docx_structural_status") != "PASS":
        raise SystemExit("Release documentation QA did not pass")
    render_paths = sorted(qa_renders.glob("page-*.png"))
    if len(render_paths) != qa.get("pdf_pages") or not render_paths:
        raise SystemExit("PDF page renders are missing or incomplete")

    commit = git_commit(root)
    payload: dict[str, bytes] = {}
    for tree in ENGINE_DIRS + TEST_DIRS:
        payload.update(add_tree(root, tree))
    payload.update(add_tree(root, "02-Compilation", ALLOWED_COMPILATION))
    payload.update(add_tree(root, "05-Documentation", ALLOWED_DOCS))
    for name in ("README.md", "verify_source_parity.py"):
        path = root / name
        if not path.is_file():
            raise SystemExit(f"Required root source is missing: {name}")
        payload[name] = path.read_bytes()
    workflow = root / ".github" / "workflows" / "openvisio-v43.24-windows-candidate.yml"
    if not workflow.is_file():
        raise SystemExit("Versioned Windows candidate workflow is missing")
    payload[workflow.relative_to(root).as_posix()] = workflow.read_bytes()

    # Repository contract tests read these legacy workflow/smoke assets directly.
    # Include them so the test suite remains runnable after extracting the ZIP.
    for relative in (
        ".gitattributes",
        ".github/workflows/openvisio-v42.93-windows-candidate.yml",
        ".github/workflows/openvisio-v42.94-windows-candidate.yml",
        "04-Tests/Smoke-Portable-V42.71.ps1",
        "04-Tests/Smoke-Installer-V42.71.ps1",
    ):
        support = root / relative
        if not support.is_file():
            raise SystemExit(f"Required packaged test support file is missing: {relative}")
        payload[relative] = support.read_bytes()

    payload[f"01-Application/binary/OpenVisio-{VERSION}-Windows-x64-Portable.exe"] = portable.read_bytes()
    payload[f"01-Application/binary/OpenVisio-Setup-{VERSION}-x64.exe"] = installer.read_bytes()
    payload[f"05-Documentation/OpenVisio-{VERSION}-Architecture-and-Qualification.docx"] = docx_path.read_bytes()
    payload[f"05-Documentation/OpenVisio-{VERSION}-Architecture-and-Qualification.pdf"] = pdf_path.read_bytes()
    payload[f"05-Documentation/{VERSION}-document-qa.json"] = qa_json_path.read_bytes()

    evidence_dir = root / "dist" / "test-logs"
    if evidence_dir.is_dir():
        for file in sorted(evidence_dir.glob("*.log")):
            payload[f"06-Evidence/Windows-Test-Logs/{file.name}"] = file.read_bytes()
    payload["06-Evidence/Windows-Candidate-Qualification.json"] = qualification_path.read_bytes()
    payload["06-Evidence/PDF-Document-QA-Note.txt"] = (
        "PDF pages were rendered to PNG and checked for text bounds by the build script.\n"
        "The DOCX was generated and structurally checked; DOCX visual rendering was not performed.\n"
        "These page renders are document QA previews, not screenshots of the OpenVisio application.\n"
        "Microsoft Visio Desktop round-trip and manual interactive Windows acceptance were not performed.\n"
    ).encode("utf-8")
    for image in render_paths:
        payload[f"06-Evidence/PDF-Document-Page-Renders/{image.name}"] = image.read_bytes()

    for name in payload:
        if not safe_archive_path(name):
            raise SystemExit(f"Unsafe packaged path: {name}")
    required = {
        f"{tree}/{module}"
        for tree in ENGINE_DIRS
        for module in ("model.py", "vsdx.py", "render.py", "routing.py", "parallel_geometry.py")
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise SystemExit("Required engine code missing from cumulative archive: " + ", ".join(missing))
    if "03-Sources/openvisio/vsdx.py" not in payload or "python/openvisio/vsdx.py" not in payload:
        raise SystemExit("Both VSDX importer mirrors must ship")

    # Validate the core source/test mirrors before building the archive.
    validator_path = root / "02-Compilation" / "verify_release_archive.py"
    spec = importlib.util.spec_from_file_location("openvisio_release_guard", validator_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Cannot load release archive validator")
    guard = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = guard
    spec.loader.exec_module(guard)
    temp_manifest_name = "07-Manifestes/manifest.json"
    manifest = {
        "project": "OpenVisio",
        "version": VERSION,
        "author": AUTHOR,
        "source_branch": "develop/v43.24-vsdx-route-attachment-guard-20261026",
        "source_commit": commit,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "windows_candidate_qualified": True,
        "windows_manual_acceptance": False,
        "microsoft_visio_qualified": False,
        "python_unit_suite": report.get("unit_suite", {}),
        "checkout_and_parity": report.get("checkout_and_parity"),
        "portable_smoke": report.get("portable_smoke"),
        "installer_smoke": report.get("installer_smoke"),
        "archive_source_guard": report.get("archive_source_guard"),
        "binary_artifacts": [
            {"name": PurePosixPath(name).name, "size": len(data), "sha256": sha256(data)}
            for name, data in sorted(payload.items()) if name.endswith(".exe")
        ],
        "file_hash_manifest": "07-Manifestes/SHA256SUMS-V43.24.txt",
        "files": {
            name: sha256(data) for name, data in sorted(payload.items())
        },
        "limitations": [
            "No Microsoft Visio Desktop round-trip certification",
            "No manual interactive Windows acceptance or application screenshot",
            "Internal application version remains 42.50.0 due to legacy build contracts",
            "Historical V43.4 ZIP is not the source of the current engine",
            "DOCX visual rendering was not performed; PDF pages were rendered and checked"
        ]
    }
    payload[temp_manifest_name] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    checksum_path = "07-Manifestes/SHA256SUMS-V43.24.txt"
    checksum_text = "".join(
        f"{sha256(data)}  {name}\n" for name, data in sorted(payload.items())
    ).encode("utf-8")
    payload[checksum_path] = checksum_text

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

    audit = guard.audit_archive(output, VERSION)
    if not audit.get("ok"):
        raise SystemExit("Final cumulative archive validation failed: " + "; ".join(audit.get("errors", [])[:20]))
    with zipfile.ZipFile(output, "r") as archive:
        bad_crc = archive.testzip()
        if bad_crc is not None:
            raise SystemExit(f"Final cumulative ZIP CRC failure: {bad_crc}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit("Final cumulative ZIP has duplicate paths")
    digest = sha256(output.read_bytes())
    sidecar = output.with_suffix(output.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {output.name}\n", encoding="ascii")
    summary = {
        "status": "PASS",
        "archive": str(output),
        "archive_sha256": digest,
        "file_count": len(payload),
        "portable_bytes": portable.stat().st_size,
        "installer_bytes": installer.stat().st_size,
        "source_commit": commit,
        "archive_guard": audit,
        "zip_crc": "PASS",
        "duplicate_paths": "PASS",
    }
    report_path = output.parent / f"{VERSION}-cumulative-archive-validation.json"
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
