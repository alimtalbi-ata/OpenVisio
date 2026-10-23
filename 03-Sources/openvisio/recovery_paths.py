"""Per-editor crash-recovery journal naming. Author: Abdelhalim Talbi."""
from pathlib import Path


def journal_path(path, session_id=None):
    """Return the legacy path or a unique per-session path, rejecting traversal."""
    suffix = ""
    if session_id is not None:
        if (not isinstance(session_id, str) or len(session_id) != 32
                or any(c not in "0123456789abcdef" for c in session_id)):
            raise ValueError("Identifiant de journal invalide")
        suffix = "." + session_id
    return Path(str(Path(path)) + ".autosave" + suffix)
