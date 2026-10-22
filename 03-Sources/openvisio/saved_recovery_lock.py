"""Cross-process ownership for saved-diagram crash-recovery journals.

The lock belongs to the journal session, not the document-save transaction.
A live editor must never be offered as an abandoned recovery candidate.
Lock files are intentionally not unlinked: unlinking a locked inode permits
another process to lock a different inode at the same path.

Author: Abdelhalim Talbi.
"""
from contextlib import contextmanager
import errno
import os
from pathlib import Path

from .recovery_paths import journal_path


def session_lock_path(path, session_id):
    if session_id is None:
        raise ValueError("Un journal historique ne possède pas de verrou de session")
    return Path(str(journal_path(path, session_id)) + ".lock")


def _open_lock(path, *, create):
    if path.is_symlink():
        raise ValueError("Verrou symbolique interdit")
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0)
    if create:
        flags |= os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")  # Windows locks require an existing byte.
        return fd
    except BaseException:
        os.close(fd)
        raise


def _try_lock(fd):
    if os.name == "nt":
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(fd):
    if os.name == "nt":
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)


def _busy(exc):
    return (exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK)
            or getattr(exc, "winerror", None) in (33, 36))


def session_is_active(path, session_id):
    """Return True for a live owner; raise for an unsafe/inaccessible lock."""
    if session_id is None:
        return False  # Legacy journals have no ownership metadata.
    lock = session_lock_path(path, session_id)
    try:
        fd = _open_lock(lock, create=False)
    except FileNotFoundError:
        return False  # Pre-V42.18 journal: retain legacy recoverability.
    try:
        try:
            _try_lock(fd)
        except OSError as exc:
            if _busy(exc):
                return True
            raise
        _unlock(fd)
        return False
    finally:
        os.close(fd)


class SavedJournalLease:
    """Held for the lifetime of an editor's association with one saved file."""
    def __init__(self, path, session_id):
        self.path = Path(path).resolve()
        self.session_id = session_id
        self._fd = _open_lock(session_lock_path(self.path, session_id), create=True)
        try:
            _try_lock(self._fd)
        except BaseException:
            os.close(self._fd)
            self._fd = None
            raise

    @property
    def active(self):
        return self._fd is not None

    def owns(self, path, session_id):
        return (self.active and self.session_id == session_id
                and self.path == Path(path).resolve())

    def close(self):
        if self._fd is not None:
            try:
                _unlock(self._fd)
            finally:
                os.close(self._fd)
                self._fd = None


@contextmanager
def journal_deletion_guard(path, session_id, *, lease=None):
    """Prevent a foreign editor deleting a journal while its owner is alive."""
    if session_id is None:
        yield
        return
    if lease is not None and lease.owns(path, session_id):
        yield
        return
    fd = _open_lock(session_lock_path(path, session_id), create=True)
    acquired = False
    try:
        try:
            _try_lock(fd)
            acquired = True
        except OSError as exc:
            if _busy(exc):
                raise ValueError("Journal utilisé par une autre instance") from exc
            raise
        yield
    finally:
        try:
            if acquired:
                _unlock(fd)
        finally:
            os.close(fd)
