"""Check VSDX drawing-part consistency independently of the GUI.

V42.8. A SHA-256 digest detects accidental or uncoordinated edits; it is NOT
an authenticity signature. External Visio resaves may reserialize unchanged XML
and still trigger a conservative mismatch. Author: Abdelhalim Talbi.
"""
import argparse
import hashlib
import json
from zipfile import ZipFile, BadZipFile
from pathlib import PurePosixPath
from .model import _unique_json_object, _reject_nonfinite_json, load_bytes

PRIVATE_PARTS = frozenset({"openvisio/document.json", "openvisio/manifest.json"})

VISUAL_PARTS = (
    "visio/pages/pages.xml",
    "visio/pages/_rels/pages.xml.rels",
    "visio/pages/page1.xml",
)


def build_manifest(parts, embedded_payload):
    """Build schema-3 integrity manifest covering every non-private OPC part.

    Unlike schema 2, this detects changes to Visio document settings, masters,
    relationships, styles, content types, and *newly added* package parts.  A
    digest is an accidental-change detector, not a cryptographic signature.
    """
    if not set(VISUAL_PARTS).issubset(parts):
        raise ValueError("Parties VSDX publiques requises absentes")
    return {
        "schema": 3,
        "sha256": hashlib.sha256(embedded_payload).hexdigest(),
        "package_parts": {name: hashlib.sha256(data).hexdigest()
                          for name, data in sorted(parts.items()) if name not in PRIVATE_PARTS},
    }


def changed_visual_parts(archive, manifest):
    """Detect altered, removed *or added* public package parts.

    Schema-2 manifests are still supported, but they only cover three drawing
    parts. Schema-3 manifests bind the complete non-private OPC member set.
    """
    schema = manifest.get("schema")
    field = "package_parts" if schema == 3 else "visual_parts"
    expected = manifest.get(field)
    if (schema not in (2, 3) or not isinstance(expected, dict)
            or not set(VISUAL_PARTS).issubset(expected)
            or (schema == 2 and set(expected) != set(VISUAL_PARTS))
            or len(expected) > 5000
            or (schema == 3 and any(name in PRIVATE_PARTS or not isinstance(name, str)
                                    or not name or name.endswith("/") for name in expected))
            or any(not isinstance(digest, str) or len(digest) != 64
                   or any(c not in "0123456789abcdef" for c in digest)
                   for digest in expected.values())):
        raise ValueError("Manifeste visuel OpenVisio/VSDX invalide")
    # Explicit ZIP directory markers are not OPC package parts. Visio and
    # third-party ZIP writers may add them without changing any drawing XML.
    names = {entry.filename for entry in archive.infolist() if not entry.is_dir()}
    if schema == 2:
        return [name for name in VISUAL_PARTS if name not in names
                or hashlib.sha256(archive.read(name)).hexdigest() != expected[name]]
    public = names - PRIVATE_PARTS
    changed = set(public) ^ set(expected)
    for name in public & set(expected):
        if hashlib.sha256(archive.read(name)).hexdigest() != expected[name]:
            changed.add(name)
    return sorted(changed)


def inspect(path):
    """Inspect an exported VSDX without importing or executing its contents."""
    with ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(entries) > 5000 or sum(entry.file_size for entry in entries) > 50_000_000:
            raise ValueError("VSDX trop volumineux")
        for entry in entries:
            normalized = entry.filename.replace("\\", "/")
            parts = PurePosixPath(normalized).parts
            if (entry.file_size > 10_000_000 or ".." in parts or normalized.startswith("/")
                    or "\\" in entry.filename or (parts and ":" in parts[0])):
                raise ValueError("Entrée VSDX non sûre")
            if entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200:
                raise ValueError("Compression VSDX suspecte")
        if len(names) != len({name.casefold() for name in names}):
            raise ValueError("Entrées VSDX dupliquées")
        has_manifest = "openvisio/manifest.json" in names
        has_document = "openvisio/document.json" in names
        if has_manifest != has_document:
            raise ValueError("Paquet OpenVisio/VSDX incomplet")
        if not has_manifest:
            return {"status": "external", "visual_consistency": "not_applicable"}
        if archive.getinfo("openvisio/manifest.json").file_size > 1_000_000:
            raise ValueError("Manifeste VSDX trop volumineux")
        if archive.getinfo("openvisio/document.json").file_size > 10_000_000:
            raise ValueError("Document VSDX trop volumineux")
        # Use the same strict JSON contract as import_vsdx. A diagnostic
        # reporting "consistent" must never accept a package the importer
        # rejects for ambiguous keys, NaN/Infinity, or boolean schema values.
        try:
            manifest = json.loads(
                archive.read("openvisio/manifest.json"),
                object_pairs_hook=_unique_json_object,
                parse_constant=_reject_nonfinite_json)
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise ValueError("Manifeste VSDX JSON invalide") from exc
        if not isinstance(manifest, dict):
            raise ValueError("Manifeste VSDX invalide")
        schema = manifest.get("schema")
        if type(schema) is not int or schema not in (1, 2, 3):
            raise ValueError("Version du manifeste VSDX inconnue")
        payload = archive.read("openvisio/document.json")
        if manifest.get("sha256") != hashlib.sha256(payload).hexdigest():
            return {"status": "corrupted_payload", "visual_consistency": "unknown"}
        # A matching checksum proves byte consistency, not that the embedded
        # diagram is usable. Mirror import_vsdx's strict JSON and model checks
        # before ever claiming "consistent" (or "legacy").
        try:
            load_bytes(payload)
        except ValueError as exc:
            raise ValueError("Document OpenVisio embarqué invalide") from exc
        if schema == 1:
            return {"status": "legacy", "visual_consistency": "unverifiable"}
        changed = changed_visual_parts(archive, manifest)
        return {"status": "modified" if changed else "consistent",
                "visual_consistency": "mismatch" if changed else "matched",
                "changed_parts": changed,
                "integrity_coverage": "complete-package-v3" if manifest["schema"] == 3
                                      else "partial-pages-v2"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check embedded OpenVisio/VSDX drawing consistency")
    parser.add_argument("vsdx", help="VSDX file to inspect")
    args = parser.parse_args(argv)
    try:
        report = inspect(args.vsdx)
    except (OSError, ValueError, KeyError, BadZipFile, json.JSONDecodeError) as exc:
        report = {"status": "invalid", "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in ("consistent", "external", "legacy") else 2


if __name__ == "__main__":
    raise SystemExit(main())
