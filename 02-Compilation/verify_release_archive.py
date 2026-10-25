#!/usr/bin/env python3
"""Fail-closed source/release gate for OpenVisio cumulative ZIP archives.

Checks both engine and test mirrors, required engine dependencies, exact release
version, safe ZIP paths, duplicate members, and complete SHA-256 coverage.
Standard library only. Author: Abdelhalim Talbi.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ENGINE_DIRS = ("03-Sources/openvisio", "python/openvisio")
TEST_DIRS = ("04-Tests/tests", "python/tests")
REQUIRED_ENGINE = ("model.py", "vsdx.py", "render.py", "routing.py", "parallel_geometry.py")
MANIFEST_PATH = "07-Manifestes/manifest.json"
HEX256 = re.compile(r"^[0-9a-fA-F]{64}$")


def _normal(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git_blob_sha(data: bytes) -> str:
    """Return a Git blob SHA-1 using Git's object framing."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _disk_map(root: Path, folder: str) -> dict[str, bytes]:
    base = root / folder
    if not base.is_dir():
        return {}
    return {p.relative_to(base).as_posix(): p.read_bytes()
            for p in base.rglob("*.py") if p.is_file() and "__pycache__" not in p.parts}


def _zip_map(names: set[str], payloads: dict[str, bytes], folder: str) -> dict[str, bytes]:
    prefix = folder.rstrip("/") + "/"
    return {name[len(prefix):]: payloads[name] for name in names
            if name.startswith(prefix) and name.lower().endswith(".py")
            and "__pycache__" not in PurePosixPath(name).parts and name in payloads}


def _compare(left: dict[str, bytes], right: dict[str, bytes], label: str) -> list[str]:
    errors = []
    for name in sorted(left.keys() - right.keys())[:100]:
        errors.append(f"{label}: fichier absent à droite: {name}")
    for name in sorted(right.keys() - left.keys())[:100]:
        errors.append(f"{label}: fichier absent à gauche: {name}")
    for name in sorted(left.keys() & right.keys()):
        if _normal(left[name]) != _normal(right[name]):
            errors.append(f"{label}: contenu divergent: {name}")
            if len(errors) >= 100:
                errors.append("diagnostic tronqué à 100 erreurs")
                break
    return errors


def audit_checkout(root: Path) -> dict:
    root = root.resolve()
    errors = []
    engine_left, engine_right = (_disk_map(root, p) for p in ENGINE_DIRS)
    tests_left, tests_right = (_disk_map(root, p) for p in TEST_DIRS)
    if not engine_left or not engine_right:
        errors.append("Checkout: les deux miroirs moteur sont obligatoires")
    if not tests_left or not tests_right:
        errors.append("Checkout: les deux miroirs de tests sont obligatoires")
    errors += _compare(engine_left, engine_right, "Moteur")
    errors += _compare(tests_left, tests_right, "Tests")
    for folder, modules in zip(ENGINE_DIRS, (engine_left, engine_right)):
        for name in REQUIRED_ENGINE:
            if name not in modules:
                errors.append(f"Checkout: dépendance moteur absente: {folder}/{name}")
    if not (root / "verify_source_parity.py").is_file():
        errors.append("Checkout: verify_source_parity.py absent")
    return {"ok": not errors, "errors": errors, "details": {
        "root": str(root), "engine_files": len(engine_left), "test_files": len(tests_left),
        "required_engine_modules": len(REQUIRED_ENGINE)}}


def _safe_member(name: str) -> bool:
    """Check the raw ZIP path, before path-library normalization can hide aliases."""
    if not isinstance(name, str) or not name or "\\" in name or name.startswith("/") or name.endswith("/"):
        return False
    parts = name.split("/")
    # PurePosixPath normalizes away '.' segments and repeated separators. A
    # release ZIP must reject those spellings instead of treating distinct ZIP
    # names as equivalent paths in downstream tools and Windows extraction.
    return (all(part not in ("", ".", "..") for part in parts)
            and not any(":" in part for part in parts))


def audit_archive(path: Path, expected_version: str) -> dict:
    path = path.resolve()
    errors = []
    details: dict[str, object] = {"archive": str(path), "expected_version": expected_version}
    try:
        with zipfile.ZipFile(path) as archive:
            info = [item for item in archive.infolist() if not item.is_dir()]
            names_list = [item.filename for item in info]
            names = set(names_list)
            if len(names_list) != len(names):
                errors.append("Archive: chemins de fichiers dupliqués")
            unsafe = [name for name in names_list if not _safe_member(name)]
            if unsafe:
                errors.append("Archive: chemin non sûr: " + ", ".join(unsafe[:8]))
            crc_error = archive.testzip()
            if crc_error is not None:
                errors.append(f"Archive: CRC invalide: {crc_error}")
            payloads = {name: archive.read(name) for name in names if name not in unsafe}
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        return {"ok": False, "errors": [f"Archive illisible: {exc}"], "details": details}

    details.update({"file_entries": len(names_list), "unique_file_entries": len(names)})
    if MANIFEST_PATH not in payloads:
        errors.append(f"Archive: manifeste absent: {MANIFEST_PATH}")
        return {"ok": False, "errors": errors, "details": details}
    try:
        manifest = json.loads(payloads[MANIFEST_PATH].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Manifeste JSON invalide: {exc}")
        return {"ok": False, "errors": errors, "details": details}
    actual_version = manifest.get("version")
    details["manifest_version"] = actual_version
    if manifest.get("project") != "OpenVisio":
        errors.append("Manifeste: project doit être OpenVisio")
    if actual_version != expected_version:
        errors.append(f"Version incohérente: attendue {expected_version}, manifeste={actual_version!r}")
    if manifest.get("author") != "Abdelhalim Talbi":
        errors.append("Manifeste: auteur attendu Abdelhalim Talbi")

    checksum_path = manifest.get("file_hash_manifest")
    checksums = {}
    if not isinstance(checksum_path, str) or checksum_path not in payloads:
        errors.append(f"Manifeste: fichier de sommes SHA-256 référencé absent: {checksum_path!r}")
    else:
        for line_no, line in enumerate(payloads[checksum_path].decode("utf-8", "replace").splitlines(), 1):
            if not line.strip():
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or not HEX256.fullmatch(parts[0]):
                errors.append(f"Sommes SHA-256: ligne {line_no} mal formée")
                continue
            name = parts[1].lstrip(" *")
            if name in checksums:
                errors.append(f"Sommes SHA-256: entrée dupliquée: {name}")
                continue
            checksums[name] = parts[0].lower()
            if name not in payloads:
                errors.append(f"Sommes SHA-256: fichier absent: {name}")
            elif hashlib.sha256(payloads[name]).hexdigest() != checksums[name]:
                errors.append(f"Sommes SHA-256: empreinte incorrecte: {name}")
        expected_coverage = names - {checksum_path}
        for name in sorted(expected_coverage - checksums.keys())[:100]:
            errors.append(f"Sommes SHA-256: fichier non couvert: {name}")
        for name in sorted(checksums.keys() - expected_coverage)[:100]:
            errors.append(f"Sommes SHA-256: entrée hors archive ou auto-référence: {name}")
        details["sha256_entries"] = len(checksums)

    file_hashes = manifest.get("files")
    if file_hashes is not None:
        if not isinstance(file_hashes, dict):
            errors.append("Manifeste: files doit être un objet chemin -> SHA-256")
        else:
            for name, expected in file_hashes.items():
                if name not in payloads:
                    errors.append(f"Manifeste: fichier référencé absent: {name}")
                elif not isinstance(expected, str) or not HEX256.fullmatch(expected):
                    errors.append(f"Manifeste: SHA-256 mal formé: {name}")
                elif hashlib.sha256(payloads[name]).hexdigest() != expected.lower():
                    errors.append(f"Manifeste: empreinte incorrecte: {name}")
            details["manifest_files_entries"] = len(file_hashes)

    engine_left, engine_right = (_zip_map(names, payloads, p) for p in ENGINE_DIRS)
    tests_left, tests_right = (_zip_map(names, payloads, p) for p in TEST_DIRS)
    if not engine_left or not engine_right:
        errors.append("Archive: les deux miroirs moteur 03-Sources/python sont obligatoires")
    if not tests_left or not tests_right:
        errors.append("Archive: les deux miroirs de tests 04-Tests/python/tests sont obligatoires")
    errors += _compare(engine_left, engine_right, "Archive moteur")
    errors += _compare(tests_left, tests_right, "Archive tests")
    for folder, modules in zip(ENGINE_DIRS, (engine_left, engine_right)):
        for name in REQUIRED_ENGINE:
            if name not in modules:
                errors.append(f"Archive: dépendance moteur absente: {folder}/{name}")
    details.update({"engine_files": len(engine_left), "test_files": len(tests_left)})
    return {"ok": not errors, "errors": errors, "details": details}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--checkout", type=Path)
    modes.add_argument("--archive", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)
    report = audit_checkout(args.checkout) if args.checkout else audit_archive(args.archive, args.version)
    body = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(body, end="")
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(body, encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
