"""Crash-recovery journal for saved OpenVisio diagrams.

A journal never overwrites the native document and is recoverable only against
exactly the disk version from which editing started. Author: Abdelhalim Talbi.
"""
import hashlib
import json
import os
import tempfile
from pathlib import Path

from .model import validate

SCHEMA = 1
MAX_JOURNAL_BYTES = 20_000_000


class RecoveryConflict(ValueError):
    """The on-disk document changed since the recovery snapshot was made."""


from .recovery_paths import journal_path
from .saved_recovery_lock import session_is_active, journal_deletion_guard


def list_journals(path, *, limit=64):
    """Enumerate validated legacy and per-session candidates, newest first.

    Each candidate is a mapping {session, document, path}. An invalid journal
    becomes a warning; it cannot hide the other recoverable versions.
    """
    if not isinstance(limit, int) or not 1 <= limit <= 256:
        raise ValueError("Limite de récupération invalide")
    legacy = journal_path(path)
    candidates = []
    if legacy.is_file() or legacy.is_symlink():
        candidates.append((None, legacy))
    prefix = legacy.name + "."
    if legacy.parent.is_dir():
        for entry in legacy.parent.iterdir():
            if entry.name.startswith(prefix):
                suffix = entry.name[len(prefix):]
                if len(suffix) == 32 and all(c in "0123456789abcdef" for c in suffix):
                    candidates.append((suffix, entry))
    warnings = []
    def modified(candidate):
        try:
            return candidate[1].stat().st_mtime_ns
        except OSError:
            return -1
    candidates.sort(key=modified, reverse=True)
    if len(candidates) > limit:
        warnings.append("Nombre de journaux supérieur à la limite d'inspection")
    found = []
    for session_id, entry in candidates[:limit]:
        try:
            if session_is_active(path, session_id):
                continue  # Another editor still owns this recovery journal.
            document = read_journal(path, session_id=session_id)
            if document is not None:
                found.append({"session": session_id, "document": document, "path": entry})
        except (OSError, ValueError, TypeError) as exc:
            warnings.append(entry.name + " : " + str(exc))
    return found, warnings


def digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _document_bytes(document):
    return json.dumps(validate(document), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def write_journal(path, document, base_digest, *, session_id=None):
    """Atomically store pending edits without changing the original or .bak.

    Refuses a stale base so an external editor's newer changes cannot be
    mistaken for a safe recovery candidate.
    """
    if not isinstance(base_digest, str) or len(base_digest) != 64 or any(
            c not in "0123456789abcdef" for c in base_digest):
        raise ValueError("Empreinte de base invalide")
    path = Path(path)
    if digest_file(path) != base_digest:
        raise RecoveryConflict("Le document a changé sur le disque : récupération suspendue")
    payload = _document_bytes(document)
    envelope = {
        "schema": SCHEMA,
        "base_sha256": base_digest,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "document": json.loads(payload),
    }
    destination = journal_path(path, session_id)
    if session_id is not None:
        envelope["session"] = session_id
    raw = json.dumps(envelope, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > MAX_JOURNAL_BYTES:
        raise ValueError("Journal de récupération trop volumineux")
    fd, tmp = tempfile.mkstemp(prefix=".openvisio-autosave-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # Recheck immediately before publication: external modifications must
        # never be presented as belonging to this editing session.
        if digest_file(path) != base_digest:
            raise RecoveryConflict("Document modifié pendant la sauvegarde automatique")
        os.replace(tmp, destination)
        if os.name == "posix":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return destination


def read_journal(path, *, session_id=None):
    """Return a validated recovery document, or None if no journal exists."""
    recovery = journal_path(path, session_id)
    if not recovery.exists():
        return None
    if recovery.is_symlink():
        raise ValueError("Journal de récupération symbolique interdit")
    if recovery.stat().st_size > MAX_JOURNAL_BYTES:
        raise ValueError("Journal de récupération trop volumineux")
    try:
        envelope = json.loads(recovery.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Journal de récupération illisible") from exc
    if not isinstance(envelope, dict) or envelope.get("schema") != SCHEMA:
        raise ValueError("Version du journal de récupération invalide")
    if envelope.get("session") != session_id:
        raise ValueError("Session du journal incohérente")
    base = envelope.get("base_sha256")
    expected = envelope.get("payload_sha256")
    if (not isinstance(base, str) or len(base) != 64
            or not isinstance(expected, str) or len(expected) != 64):
        raise ValueError("Empreintes du journal invalides")
    doc = validate(envelope.get("document"))
    if hashlib.sha256(_document_bytes(doc)).hexdigest() != expected:
        raise ValueError("Journal de récupération altéré")
    if digest_file(path) != base:
        raise RecoveryConflict("Le document a été modifié depuis l'enregistrement du journal")
    return doc


def discard_journal(path, *, session_id=None, lease=None):
    """Discard one session, refusing journals held by another live editor."""
    with journal_deletion_guard(path, session_id, lease=lease):
        journal_path(path, session_id).unlink(missing_ok=True)
