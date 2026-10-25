"""OpenVisio VSDX import/export facade with explicit concurrency safeguards.

The package writer is isolated in vsdx_package.py so that public VSDX
imports and the GUI share one stable API. Author: Abdelhalim Talbi.
"""
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from .model import (validate, load_bytes, SaveConflict, _sha256,
                    _unique_json_object, _reject_nonfinite_json)
from .save_lock import exclusive_document_lock
from .vsdx_consistency import VISUAL_PARTS, changed_visual_parts
from .vsdx_polyline import connector_polyline
from .vsdx_package import (V, R, OR, CT, PX_PER_IN, ET, _cell, _xml,
                           _relationships, _export_vsdx_unlocked, _require_public_shape_identity,
                           UnsupportedVsdxShapeError)

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

    # Validate the public shape mapping before acquiring the lock: the lock
    # helper may create the output directory, even if export then fails.
    _require_public_shape_identity(validate(document)["nodes"])
    try:
        with exclusive_document_lock(output, timeout=lock_timeout):
            check_revision()
            return _export_vsdx_unlocked(output, document, check_revision, require_absent,
                                         archive_type=ZipFile, polyline_builder=connector_polyline)
    except TimeoutError as exc:
        raise SaveConflict(str(exc)) from exc


_WINDOWS_RESERVED_PART = re.compile(
    r"^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|CLOCK\$|COM[1-9¹²³]|LPT[1-9¹²³])$",
    re.IGNORECASE,
)
_WINDOWS_FORBIDDEN_PART_CHARS = frozenset('<>:"|?*')


def _portable_windows_part(part):
    """Reject OPC member segments that Win32 rejects, trims or aliases."""
    if not part or part[-1] in " .":
        return False
    if any(ord(char) < 32 or ord(char) == 127 or char in _WINDOWS_FORBIDDEN_PART_CHARS
           for char in part):
        return False
    stem = part.split(".", 1)[0].rstrip(" .").upper()
    return _WINDOWS_RESERVED_PART.fullmatch(stem) is None


def _canonical_vsdx_member_name(name):
    """Return a portable collision key; reject non-canonical OPC member paths."""
    if (not isinstance(name, str) or not name or "\x00" in name
            or "\\" in name or name.startswith("/")):
        raise ValueError("Entrée VSDX non sûre")
    raw = name[:-1] if name.endswith("/") else name
    parts = raw.split("/")
    if not raw or any(part in ("", ".", "..") or not _portable_windows_part(part)
                     for part in parts):
        raise ValueError("Entrée VSDX non sûre")
    return "/".join(parts).casefold()


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
        seen_member_paths = set()
        for entry in entries:
            # Bound decompression amplification before extracting attacker-controlled XML/JSON.
            if entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200:
                raise ValueError("VSDX à compression suspecte")
            if entry.file_size > 10_000_000:
                raise ValueError("Entrée VSDX non sûre")
            canonical_name = _canonical_vsdx_member_name(entry.filename)
            # Also reject Windows case-folding collisions and syntactic aliases:
            # never let two ZIP members represent one logical Open Packaging part.
            if canonical_name in seen_member_paths:
                raise ValueError("Entrées VSDX dupliquées ou aliasées")
            seen_member_paths.add(canonical_name)
        if "openvisio/manifest.json" in archive.namelist() and "openvisio/document.json" not in archive.namelist():
            raise ValueError("Document OpenVisio/VSDX manquant pour le manifeste présent")
        if "openvisio/document.json" in archive.namelist():
            payload = archive.read("openvisio/document.json")
            if "openvisio/manifest.json" not in archive.namelist():
                raise ValueError("Manifeste OpenVisio/VSDX manquant")
            # Reject ambiguous manifest keys and non-JSON numeric constants.
            # Otherwise the last duplicate SHA/schema silently wins, defeating
            # deterministic VSDX provenance and cross-reader agreement.
            try:
                manifest = json.loads(
                    archive.read("openvisio/manifest.json"),
                    object_pairs_hook=_unique_json_object,
                    parse_constant=_reject_nonfinite_json)
            except (ValueError, UnicodeError, RecursionError) as exc:
                raise ValueError("Manifeste OpenVisio/VSDX JSON invalide") from exc
            if not isinstance(manifest, dict):
                raise ValueError("Manifeste OpenVisio/VSDX invalide : objet JSON attendu")
            schema = manifest.get("schema")
            if type(schema) is not int or schema not in (1, 2, 3) or manifest.get("sha256") != hashlib.sha256(payload).hexdigest():
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
