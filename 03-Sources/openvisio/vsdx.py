"""OpenVisio VSDX import/export facade with explicit concurrency safeguards.

The package writer is isolated in vsdx_package.py so that public VSDX
imports and the GUI share one stable API. Author: Abdelhalim Talbi.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from .model import validate, load_bytes, SaveConflict, _sha256
from .save_lock import exclusive_document_lock
from .vsdx_consistency import VISUAL_PARTS, changed_visual_parts
from .vsdx_polyline import connector_polyline
from .vsdx_package import (V, R, OR, CT, PX_PER_IN, ET, _cell, _xml,
                           _relationships, _export_vsdx_unlocked)

class VsdxExternalChangesError(ValueError):
    """Embedded OpenVisio data no longer matches the Visio drawing pages."""

def export_vsdx(path, document, *, expected_sha256=None, require_absent=False, lock_timeout=5.0):
    """Export VSDX with optional no-clobber / optimistic concurrency guards.

    GUI exports always supply a precondition. Direct API callers can retain
    legacy unconditional overwrite behavior by omitting both preconditions.
    The stable sibling lock serializes cooperating OpenVisio processes; writers
    ignoring this advisory lock cannot be made fully atomic across platforms.
    """
    output = Path(path)
    if require_absent and expected_sha256 is not None:
        raise ValueError("Préconditions d'export VSDX incompatibles")
    if expected_sha256 is not None and (
            not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(ch not in '0123456789abcdef' for ch in expected_sha256)):
        raise ValueError("Empreinte VSDX invalide")

    def check_revision():
        if require_absent:
            if output.exists() or output.is_symlink():
                raise SaveConflict("Le VSDX de destination a été créé par un autre processus")
        elif expected_sha256 is not None:
            try:
                current = _sha256(output)
            except FileNotFoundError as exc:
                raise SaveConflict("Le VSDX a disparu pendant l'export") from exc
            if current != expected_sha256:
                raise SaveConflict("Le VSDX a été modifié pendant l'export ; remplacement refusé")

    try:
        with exclusive_document_lock(output, timeout=lock_timeout):
            check_revision()
            return _export_vsdx_unlocked(output, document, check_revision, require_absent,
                                         archive_type=ZipFile, polyline_builder=connector_polyline)
    except TimeoutError as exc:
        raise SaveConflict(str(exc)) from exc


def import_vsdx(path, *, changed_pages="reject"):
    """Import VSDX, refusing to silently discard edits made in Visio.

    For a VSDX exported with schema 2/3, changed drawing XML raises
    VsdxExternalChangesError. Set changed_pages="flatten" explicitly to
    recover supported external geometry with documented fidelity limitations.
    Legacy schema-1 VSDX files lack page checksums and cannot be verified.
    """
    if changed_pages not in ("reject", "flatten"):
        raise ValueError("Mode d'import des pages VSDX invalide")
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 5000 or sum(entry.file_size for entry in entries) > 50_000_000:
            raise ValueError("VSDX trop volumineux")
        if len({entry.filename.replace("\\", "/").casefold() for entry in entries}) != len(entries):
            raise ValueError("Entrées VSDX dupliquées")
        for entry in entries:
            # Bound decompression amplification before extracting attacker-controlled XML/JSON.
            if entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200:
                raise ValueError("VSDX à compression suspecte")
            # ZIP members use forward slashes. Reject Windows backslash traversal too.
            name = entry.filename.replace("\\", "/")
            parts = PurePosixPath(name).parts
            if (entry.file_size > 10_000_000 or ".." in parts
                    or name.startswith("/") or "\\" in entry.filename
                    or (parts and ":" in parts[0])):
                raise ValueError("Entrée VSDX non sûre")
        if "openvisio/manifest.json" in archive.namelist() and "openvisio/document.json" not in archive.namelist():
            raise ValueError("Document OpenVisio/VSDX manquant pour le manifeste présent")
        if "openvisio/document.json" in archive.namelist():
            payload = archive.read("openvisio/document.json")
            if "openvisio/manifest.json" not in archive.namelist():
                raise ValueError("Manifeste OpenVisio/VSDX manquant")
            manifest = json.loads(archive.read("openvisio/manifest.json"))
            if not isinstance(manifest, dict):
                raise ValueError("Manifeste OpenVisio/VSDX invalide : objet JSON attendu")
            schema = manifest.get("schema")
            if schema not in (1, 2, 3) or manifest.get("sha256") != hashlib.sha256(payload).hexdigest():
                raise ValueError("Intégrité OpenVisio/VSDX invalide")
            if schema in (2, 3):
                changed = changed_visual_parts(archive, manifest)
                if changed:
                    if changed_pages == "reject":
                        raise VsdxExternalChangesError(
                            "Parties VSDX modifiées depuis l'export OpenVisio : "
                            + ", ".join(changed)
                            + ". L'import du modèle embarqué ignorerait ces changements. "
                              "Choisissez explicitement l'import géométrique partiel.")
                    from .vsdx_external import import_external_pages
                    imported = import_external_pages(archive)
                    imported.setdefault("metadata", {}).update({
                        "embedded_payload_discarded": True,
                        "changed_parts": changed,
                        "import_warning": "Pages modifiées : import géométrique partiel, "
                                          "sans conservation intégrale des propriétés OpenVisio.",
                    })
                    return validate(imported)
            return load_bytes(payload)
        from .vsdx_external import import_external_pages
        return import_external_pages(archive)
