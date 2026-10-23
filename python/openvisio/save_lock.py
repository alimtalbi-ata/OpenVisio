"""Cross-process advisory save lock for local OpenVisio documents.

Locks remain in a stable sibling inode: deleting the lockfile would permit
concurrent processes to lock different inodes. Author: Abdelhalim Talbi.
"""
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import time


def lock_path(destination):
    """Canonical parent path; the document's filename is never dereferenced."""
    destination = Path(destination)
    return destination.parent.resolve() / ("." + destination.name + ".openvisio.lock")


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


@contextmanager
def exclusive_document_lock(destination, *, timeout=5.0):
    """Lock the full read-check/backup/replace transaction across processes.

    Only cooperating OpenVisio writers participate; external editors may not.
    The lock is advisory on POSIX and a one-byte Windows byte-range lock.
    """
    if not isinstance(timeout, (int, float)) or not 0 <= timeout <= 300:
        raise ValueError("Délai de verrouillage invalide")
    lockfile = lock_path(destination)
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(lockfile, flags, 0o600)
    acquired = False
    try:
        # A nonempty byte range is required by msvcrt.locking on Windows.
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"\0")
        deadline = time.monotonic() + timeout
        while True:
            try:
                _try_lock(fd)
                acquired = True
                break
            except OSError as exc:
                transient = (exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK)
                             or getattr(exc, "winerror", None) in (33, 36))
                if not transient:
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError("Document utilisé par une autre instance ; réessayez") from exc
                time.sleep(min(0.05, max(0, deadline - time.monotonic())))
        yield
    finally:
        try:
            if acquired:
                _unlock(fd)
        finally:
            os.close(fd)
