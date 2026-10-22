"""Crash recovery for untitled OpenVisio diagrams (V42.14).

Every editor process holds a lock for its private session. Only abandoned
journals are offered for recovery, preventing a second running editor from
stealing a live untitled diagram. No native document is ever overwritten.

Author: Abdelhalim Talbi.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .model import validate

SCHEMA = 1
MAX_BYTES = 20_000_000
MAX_CANDIDATES = 64


def recovery_directory():
    """Use the user's local, non-roaming state directory on Windows."""
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if not root:
            root = str(Path.home() / "AppData" / "Local")
    else:
        root = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(root) / "OpenVisio" / "Recovery"


def _payload(document):
    return json.dumps(validate(document), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _lock_file(handle):
    handle.seek(0)
    if os.name == "nt":
        import msvcrt
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
    else:
        import fcntl
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
    return True


def _unlock_file(handle):
    handle.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _journal_path(root, session_id):
    return Path(root) / ("untitled-" + session_id + ".json")


def _read_journal(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Journal de récupération non fiable ou trop volumineux")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Journal de récupération illisible") from exc
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Version du journal de récupération invalide")
    sid = path.name.removeprefix("untitled-").removesuffix(".json")
    if data.get("session") != sid or len(sid) != 32 or any(c not in "0123456789abcdef" for c in sid):
        raise ValueError("Identifiant de session invalide")
    expected = data.get("payload_sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError("Empreinte du journal invalide")
    updated = data.get("updated_utc")
    if not isinstance(updated, str) or len(updated) > 64:
        raise ValueError("Horodatage de récupération invalide")
    try:
        timestamp = datetime.fromisoformat(updated)
    except ValueError as exc:
        raise ValueError("Horodatage de récupération invalide") from exc
    if timestamp.tzinfo is None:
        raise ValueError("Horodatage de récupération sans fuseau")
    doc = validate(data.get("document"))
    if not hmac.compare_digest(hashlib.sha256(_payload(doc)).hexdigest(), expected):
        raise ValueError("Journal de récupération altéré")
    return {"session": sid, "document": doc, "updated_utc": updated,
            "path": path}


def _available(path):
    """True if a journal's owner no longer holds its advisory session lock."""
    lock = path.with_suffix(".lock")
    if lock.is_symlink():
        return False
    if not lock.exists():
        return True
    try:
        with lock.open("r+b") as stream:
            if not _lock_file(stream):
                return False
            _unlock_file(stream)
        return True
    except OSError:
        return False


def recoverable_sessions(root=None):
    """Return (recoverable journals, warnings), never modifying any journal."""
    root = Path(root) if root is not None else recovery_directory()
    if not root.exists():
        return [], []
    if root.is_symlink() or not root.is_dir():
        return [], ["Répertoire de récupération non fiable"]
    found, warnings = [], []
    paths = sorted(root.glob("untitled-*.json"), key=lambda p: p.name)
    if len(paths) > MAX_CANDIDATES:
        warnings.append("Trop de journaux : seuls les 64 premiers sont inspectés")
    for path in paths[:MAX_CANDIDATES]:
        if not _available(path):
            continue
        try:
            found.append(_read_journal(path))
        except (ValueError, OSError, TypeError) as exc:
            warnings.append(path.name + " : " + str(exc))
    found.sort(key=lambda entry: entry["updated_utc"] or "", reverse=True)
    return found, warnings


def discard_session(root, session_id):
    """Discard only a validated, inactive session; do not touch live journals."""
    if len(session_id) != 32 or any(c not in "0123456789abcdef" for c in session_id):
        raise ValueError("Identifiant de session invalide")
    path = _journal_path(root, session_id)
    if not _available(path):
        raise ValueError("Journal utilisé par une autre instance")
    if path.is_symlink():
        raise ValueError("Journal symbolique interdit")
    path.unlink(missing_ok=True)
    lock = path.with_suffix(".lock")
    if not lock.is_symlink():
        lock.unlink(missing_ok=True)


class UntitledSession:
    """Process-owned, crash-safe journal for one untitled editor session."""
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else recovery_directory()
        if self.root.is_symlink():
            raise ValueError("Répertoire de récupération symbolique interdit")
        self.root.mkdir(parents=True, exist_ok=True)
        self.session = uuid4().hex
        self.path = _journal_path(self.root, self.session)
        self.lock_path = self.path.with_suffix(".lock")
        self._handle = self.lock_path.open("w+b")
        self._handle.write(b"0")
        self._handle.flush()
        if not _lock_file(self._handle):
            self._handle.close()
            raise OSError("Verrouillage de la session impossible")
        self._closed = False

    def write(self, document):
        if self._closed:
            raise ValueError("Session de récupération fermée")
        payload = _payload(document)
        envelope = {"schema": SCHEMA, "session": self.session,
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                    "payload_sha256": hashlib.sha256(payload).hexdigest(),
                    "document": json.loads(payload)}
        raw = json.dumps(envelope, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(raw) > MAX_BYTES:
            raise ValueError("Journal de récupération trop volumineux")
        fd, tmp = tempfile.mkstemp(prefix=".openvisio-untitled-", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self.path)
            if os.name == "posix":
                directory_fd = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return self.path

    def discard(self):
        if self._closed:
            raise ValueError("Session de récupération fermée")
        self.path.unlink(missing_ok=True)

    def close(self):
        if not self._closed:
            try:
                _unlock_file(self._handle)
            finally:
                self._handle.close()
                self._closed = True
            # Retain the lock file if a journal exists (crash-recovery marker).
            if not self.path.exists():
                self.lock_path.unlink(missing_ok=True)
