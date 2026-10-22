"""Document persistence service, independent of Tkinter. Author: Abdelhalim Talbi."""
from pathlib import Path
from hashlib import sha256
from .model import load, load_bytes, save
from .document_recovery import read_backup

def open_document(path):
    """Validate and load a document without changing editor state."""
    return load(path)

def open_document_with_revision(path):
    """Return a document and SHA-256 of the *same* bytes read from disk.

    Reading the file again to compute the revision would allow an external
    writer to change it between the two operations, silently misidentifying
    the document currently displayed by the editor.
    """
    raw = Path(path).read_bytes()
    return load_bytes(raw), sha256(raw).hexdigest()


def save_document_with_revision(path, document, *, expected_sha256=None,
                                require_absent=False, lock_timeout=5.0):
    """Save and return SHA-256 of bytes actually published by this process.

    This is a publication receipt, not a post-save read of the destination.
    Any later external modification is detected by the next guarded save.
    """
    return save(Path(path), document, expected_sha256=expected_sha256,
                require_absent=require_absent, lock_timeout=lock_timeout)


def save_document(path, document, *, expected_sha256=None, require_absent=False, lock_timeout=5.0):
    """Persist validated document and return its normalized destination."""
    destination = Path(path)
    save(destination, document, expected_sha256=expected_sha256, require_absent=require_absent, lock_timeout=lock_timeout)
    return str(destination)

def restore_previous(path):
    """Read and validate the previous saved version without modifying the primary file."""
    return read_backup(path)

def inspect_previous(path):
    """Return validated backup and a snapshot for optimistic concurrency checks."""
    from .document_integrity import snapshot
    from .document_recovery import backup_path
    backup = backup_path(path)
    before = snapshot(backup)
    from .recovery_guard import guarded_backup_read
    document = guarded_backup_read(backup, before)
    return document, before

def restore_inspected(path, expected):
    """Read a backup only if it still matches the user's inspected version."""
    from .document_integrity import verify_snapshot
    from .document_recovery import backup_path
    if expected.path.resolve() != backup_path(path).resolve():
        raise ValueError('Sauvegarde non associée à ce document')
    from .recovery_guard import guarded_backup_read
    return guarded_backup_read(backup_path(path), expected)
