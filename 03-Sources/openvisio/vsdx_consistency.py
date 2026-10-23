"""Check VSDX drawing-part consistency independently of the GUI.

V42.8. A SHA-256 digest detects accidental or uncoordinated edits; it is NOT
an authenticity signature. External Visio resaves may reserialize unchanged XML
and still trigger a conservative mismatch. Author: Abdelhalim Talbi.
"""
import argparse
import hashlib
import json
from zipfile import ZipFile, BadZipFile
from .vsdx_manifest_schema import validate_manifest_schema

VISUAL_PARTS = (
    "visio/pages/pages.xml",
    "visio/pages/_rels/pages.xml.rels",
    "visio/pages/page1.xml",
)


def build_manifest(parts, embedded_payload):
    """Build schema-2 digest manifest for a newly exported VSDX package."""
    return {
        "schema": 2,
        "sha256": hashlib.sha256(embedded_payload).hexdigest(),
        "visual_parts": {name: hashlib.sha256(parts[name]).hexdigest()
                         for name in VISUAL_PARTS},
    }


def changed_visual_parts(archive, manifest):
    """Return changed/missing Visio drawing parts, rejecting invalid metadata."""
    expected = manifest.get("visual_parts")
    if (not isinstance(expected, dict) or set(expected) != set(VISUAL_PARTS)
            or any(not isinstance(digest, str) or len(digest) != 64
                   or any(c not in "0123456789abcdef" for c in digest)
                   for digest in expected.values())):
        raise ValueError("Manifeste visuel OpenVisio/VSDX invalide")
    names = set(archive.namelist())
    return [name for name in VISUAL_PARTS if name not in names
            or hashlib.sha256(archive.read(name)).hexdigest() != expected[name]]


def inspect(path):
    """Inspect an exported VSDX without importing or executing its contents."""
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 5000 or sum(entry.file_size for entry in entries) > 50_000_000:
            raise ValueError("VSDX trop volumineux")
        for entry in entries:
            if entry.file_size > 10_000_000 or (entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200):
                raise ValueError("Entrée VSDX suspecte")
        names = archive.namelist()
        if any(name.startswith("/") or "\\\\" in name or ".." in name.split("/") for name in names):
            raise ValueError("Chemin VSDX non sûr")
        if len(names) != len({name.casefold() for name in names}):
            raise ValueError("Entrées VSDX dupliquées")
        has_manifest = "openvisio/manifest.json" in names
        has_document = "openvisio/document.json" in names
        if has_manifest != has_document:
            raise ValueError("Paquet OpenVisio/VSDX incomplet")
        if not has_manifest:
            if not any(name.startswith("visio/pages/") and name.endswith(".xml") and "/_rels/" not in name for name in names):
                raise ValueError("Archive sans page Visio : fichier VSDX invalide")
            return {"status": "external", "visual_consistency": "not_applicable"}
        if archive.getinfo("openvisio/manifest.json").file_size > 1_000_000:
            raise ValueError("Manifeste VSDX trop volumineux")
        if archive.getinfo("openvisio/document.json").file_size > 10_000_000:
            raise ValueError("Document VSDX trop volumineux")
        manifest = json.loads(archive.read("openvisio/manifest.json"))
        if not isinstance(manifest, dict):
            raise ValueError("Manifeste VSDX invalide")
        payload = archive.read("openvisio/document.json")
        if manifest.get("sha256") != hashlib.sha256(payload).hexdigest():
            return {"status": "corrupted_payload", "visual_consistency": "unknown"}
        schema = validate_manifest_schema(manifest)
        if schema == 1:
            return {"status": "legacy", "visual_consistency": "unverifiable"}
        if schema != 2:
            raise ValueError("Version du manifeste VSDX inconnue")
        changed = changed_visual_parts(archive, manifest)
        return {"status": "modified" if changed else "consistent",
                "visual_consistency": "mismatch" if changed else "matched",
                "changed_parts": changed}


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
