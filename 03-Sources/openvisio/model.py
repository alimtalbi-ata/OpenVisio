"""Validated diagram model, no Java or JavaScript runtime. Author: Abdelhalim Talbi."""
import json
import hashlib
import warnings
from uuid import uuid5, NAMESPACE_URL
from pathlib import Path

from .validation import validate_document

# Reject unexpectedly large files before JSON decoding allocates additional memory.
MAX_DOCUMENT_BYTES = 128 * 1024 * 1024

def validate(data):
    return validate_document(data)

def _read_document_bytes(path):
    """Read a single bounded snapshot for both editor and API load paths.

    Callers may hash these exact bytes to obtain the revision of the document
    they actually displayed, without a second potentially racing disk read.
    """
    with Path(path).open("rb") as stream:
        return stream.read(MAX_DOCUMENT_BYTES + 1)


def load(path):
    """Load a validated document without an unbounded file read."""
    return load_bytes(_read_document_bytes(path))

def _unique_json_object(pairs):
    """Reject duplicate JSON keys instead of silently changing diagram topology."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Document OpenVisio invalide : clé JSON dupliquée {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value):
    raise ValueError(f"Document OpenVisio invalide : constante JSON interdite {value}")


def load_bytes(payload):
    if not isinstance(payload, bytes):
        raise ValueError("Document OpenVisio : contenu binaire attendu")
    if len(payload) > MAX_DOCUMENT_BYTES:
        raise ValueError("Document OpenVisio trop volumineux")
    try:
        data = json.loads(payload.decode("utf-8"),
                          object_pairs_hook=_unique_json_object,
                          parse_constant=_reject_nonfinite_json)
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise ValueError("Document OpenVisio illisible ou JSON invalide") from exc
    if isinstance(data, dict) and isinstance(data.get("edges", []), list):
        # Backward compatibility with earlier diagrams lacking edge IDs.
        edges = []
        for index, edge in enumerate(data.get("edges", [])):
            if isinstance(edge, dict) and "id" not in edge:
                key = str(index) + ":" + str(edge.get("from")) + ":" + str(edge.get("to"))
                edge = {**edge, "id": "legacy-" + uuid5(NAMESPACE_URL, key).hex}
            edges.append(edge)
        data = {**data, "edges": edges}
    return validate(data)

class SaveConflict(ValueError):
    """A different on-disk revision would be overwritten by this save."""


class BackupUpdateWarning(UserWarning):
    """Primary document saved, but the recovery backup could not be updated."""


class PublicationDurabilityWarning(UserWarning):
    """Primary document published; directory metadata sync did not complete."""


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save(path, data, *, expected_sha256=None, require_absent=False, lock_timeout=5.0):
    """Save with an inter-process lock and optimistic disk revision check.

    Cooperating OpenVisio processes serialize their writes. External writers
    ignoring the lock are still detected when possible, not guaranteed.
    Returns SHA-256 of the exact bytes published by this call.
    """
    import os
    import tempfile
    import shutil
    from .save_lock import exclusive_document_lock
    path = Path(path)
    validated = validate(data)
    # Compute the revision from the exact bytes that will be published.
    # Hashing the destination after publication can accidentally adopt an
    # external writer's revision as our own (a data-loss race).
    payload = json.dumps(validated, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    published_sha256 = hashlib.sha256(payload).hexdigest()
    if require_absent and expected_sha256 is not None:
        raise ValueError("Préconditions de sauvegarde incompatibles")
    if expected_sha256 is not None and (
            not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in expected_sha256)):
        raise ValueError("Empreinte de sauvegarde invalide")

    def check_revision():
        if require_absent:
            if path.exists() or path.is_symlink():
                raise SaveConflict("Le fichier de destination a été créé par un autre processus")
        elif expected_sha256 is not None:
            try:
                current = _sha256(path)
            except FileNotFoundError as exc:
                raise SaveConflict("Le fichier a disparu depuis son ouverture") from exc
            if current != expected_sha256:
                raise SaveConflict("Le fichier a été modifié depuis son ouverture ; sauvegarde refusée")

    def _save_locked():
        check_revision()
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".openvisio-", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            check_revision()
            # Stage the previous document, but do NOT replace .bak yet.
            # The old implementation replaced .bak before the final revision
            # check and could destroy the last recovery copy on a conflict.
            backup = path.with_name(path.name + ".bak")
            backup_tmp = None
            if path.is_file():
                backup_fd, backup_tmp = tempfile.mkstemp(
                    prefix=".openvisio-backup-", suffix=".tmp", dir=path.parent)
            try:
                if backup_tmp is not None:
                    with os.fdopen(backup_fd, "wb") as backup_stream:
                        with path.open("rb") as original:
                            shutil.copyfileobj(original, backup_stream)
                        backup_stream.flush()
                        os.fsync(backup_stream.fileno())
                check_revision()
                if require_absent:
                    # Atomic no-clobber publish: link fails if another process created it.
                    try:
                        os.link(tmp, path)
                    except FileExistsError as exc:
                        raise SaveConflict("La destination a été créée entre-temps") from exc
                else:
                    os.replace(tmp, path)
                # Only a successful primary publication may advance .bak.
                # If an earlier operation raises, the prior recovery copy
                # remains untouched. Both temp files are on the same volume.
                if backup_tmp is not None:
                    try:
                        os.replace(backup_tmp, backup)
                        backup_tmp = None
                    except OSError as exc:
                        # The primary file has already been committed. Raising
                        # here would leave the GUI believing it is unsaved,
                        # provoking a false revision conflict on retry.
                        warnings.warn(
                            f"Document enregistré, mais sauvegarde de secours non actualisée : {exc}",
                            BackupUpdateWarning, stacklevel=2)
            finally:
                if backup_tmp is not None and os.path.exists(backup_tmp):
                    os.unlink(backup_tmp)
            if os.name == "posix":
                # This happens AFTER the primary file has been published. An
                # exception here must not make the editor believe the save
                # failed: a retry with the stale revision would conflict.
                directory_fd = None
                try:
                    directory_fd = os.open(path.parent, os.O_RDONLY)
                    os.fsync(directory_fd)
                except OSError as exc:
                    warnings.warn(
                        f"Document publié, mais synchronisation du répertoire "
                        f"non garantie : {exc}",
                        PublicationDurabilityWarning, stacklevel=2)
                finally:
                    if directory_fd is not None:
                        try:
                            os.close(directory_fd)
                        except OSError as exc:
                            warnings.warn(
                                f"Document publié, mais fermeture du répertoire "
                                f"non garantie : {exc}",
                                PublicationDurabilityWarning, stacklevel=2)
            return published_sha256
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    # The entire transaction is enclosed by the stable sibling lock.
    # A lock timeout is reported as a normal save conflict to the editor.
    try:
        with exclusive_document_lock(path, timeout=lock_timeout):
            return _save_locked()
    except TimeoutError as exc:
        raise SaveConflict(str(exc)) from exc
