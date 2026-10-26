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


class VsdxFidelityError(ValueError):
    """Strict import refused a VSDX whose known fidelity losses are non-empty."""

    def __init__(self, issues):
        if isinstance(issues, str):
            issues = (issues,)
        self.issues = tuple(str(item) for item in issues)
        detail = "; ".join(self.issues) or "Fidélité non vérifiable"
        super().__init__("Import VSDX refusé en mode fidélité stricte : " + detail)


def _require_reported_fidelity(document, strict_fidelity):
    """Refuse a public-geometry import when the importer reports known loss.

    This is an opt-in safety gate, not a Microsoft Visio certification. It
    blocks known omissions/approximations that the importer explicitly records.
    """
    if not strict_fidelity:
        return document
    metadata = document.get("metadata", {}) if isinstance(document, dict) else {}
    if not isinstance(metadata, dict):
        raise VsdxFidelityError("Métadonnées de fidélité absentes")
    issues = []
    warnings = metadata.get("fidelity_warnings", [])
    if isinstance(warnings, (list, tuple)):
        issues.extend(str(item) for item in warnings if str(item).strip())
    elif warnings:
        issues.append(str(warnings))
    warning = metadata.get("import_warning")
    if isinstance(warning, str) and warning.strip() and warning not in issues:
        issues.append(warning)
    if metadata.get("embedded_payload_discarded"):
        issues.append("modèle OpenVisio embarqué écarté")
    # Loss counters are a second, independent evidence channel. A future importer
    # refactor must not accidentally make strict mode permissive merely by
    # forgetting to add a matching human-readable warning string.
    loss_counters = {
        "rotated_shapes_as_bounding_boxes": ("rotated Visio shape",),
        "formula_driven_geometry_unresolved_shapes": ("formula-driven geometry",),
        "group_children_omitted": ("nested group child shape(s) omitted",),
        "group_children_imported": ("nested group child shape(s) imported",),
        "page_extent_expanded": ("Visio page(s) expanded",),
        "orthogonal_connector_routes_approximated": ("orthogonal Visio connector(s)",),
        "connector_links_skipped": ("Visio connector(s) omitted", "liaison(s) non importée(s)"),
    }
    for key, warning_markers in loss_counters.items():
        if key not in metadata:
            continue
        count = metadata[key]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            issues.append(f"Compteur de perte de fidélité invalide : {key}")
            continue
        already_described = any(
            marker.casefold() in issue.casefold()
            for issue in issues for marker in warning_markers
        )
        if count and not already_described:
            issues.append(f"Compteur de perte de fidélité {key}={count}")
    if issues:
        raise VsdxFidelityError(issues)
    return document

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


def _require_canonical_openvisio_parts(member_names):
    """Reject case aliases of OpenVisio's reserved payload parts.

    A case-variant ``openvisio/document.json`` previously bypassed the private
    payload branch on case-sensitive systems and silently fell back to the
    lossy public-Visio geometry importer. Keep the custom-part names exact so
    an archive can never appear to import successfully while dropping editor
    metadata, layers, or other model fields.
    """
    expected_parts = ("openvisio/document.json", "openvisio/manifest.json")
    by_casefold = {}
    for name in member_names:
        by_casefold.setdefault(name.casefold(), []).append(name)
    for expected in expected_parts:
        for actual in by_casefold.get(expected, ()):
            if actual != expected:
                raise ValueError("Nom de partie OpenVisio non canonique : " + actual)


def import_vsdx(path, *, changed_pages="reject", strict_fidelity=False):
    """Import VSDX with optional refusal of importer-known fidelity losses.

    strict_fidelity=True rejects skipped/approximated geometry, explicit
    flatten recovery that discards the embedded model, and legacy schema-1
    payloads whose public pages have no integrity checksums. It is not a
    Microsoft Visio compatibility certificate.
    """
    if changed_pages not in ("reject", "flatten"):
        raise ValueError("Mode d'import des pages VSDX invalide")
    if type(strict_fidelity) is not bool:
        raise ValueError("strict_fidelity doit être un booléen")
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
        member_names = [entry.filename for entry in entries]
        _require_canonical_openvisio_parts(member_names)
        member_name_set = set(member_names)
        if "openvisio/manifest.json" in member_name_set and "openvisio/document.json" not in member_name_set:
            raise ValueError("Document OpenVisio/VSDX manquant pour le manifeste présent")
        if "openvisio/document.json" in member_name_set:
            payload = archive.read("openvisio/document.json")
            if "openvisio/manifest.json" not in member_name_set:
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
                    if strict_fidelity:
                        raise VsdxFidelityError(
                            ["les pages Visio ont été modifiées ; le repli géométrique "
                             "écarterait le modèle OpenVisio embarqué", *changed])
                    from .vsdx_external import import_external_pages
                    imported = import_external_pages(archive)
                    imported.setdefault("metadata", {}).update({
                        "embedded_payload_discarded": True,
                        "changed_parts": changed,
                        "import_warning": "Pages modifiées : import géométrique partiel, "
                                          "sans conservation intégrale des propriétés OpenVisio.",
                    })
                    return _require_reported_fidelity(validate(imported), strict_fidelity)
            if strict_fidelity and schema == 1:
                raise VsdxFidelityError(
                    "VSDX de schéma 1 : les pages publiques ne disposent pas d'empreintes "
                    "permettant de vérifier les modifications externes")
            return load_bytes(payload)
        from .vsdx_external import import_external_pages
        imported = import_external_pages(archive)
        return _require_reported_fidelity(imported, strict_fidelity)
