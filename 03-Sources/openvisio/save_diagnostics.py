"""Capture post-publication save warnings without treating a committed save as failed.

A successful disk publication must update the editor's revision even when its
backup or directory durability step fails. Author: Abdelhalim Talbi.
"""
import warnings

from .model import BackupUpdateWarning, PublicationDurabilityWarning


SAVE_WARNING_TYPES = (BackupUpdateWarning, PublicationDurabilityWarning)


def save_with_diagnostics(save_function, *args, **kwargs):
    """Return (publication receipt, warnings) or propagate a genuine save error.

    Only our two explicit post-publication warning categories are consumed;
    unrelated warnings remain visible to the caller's normal warning handlers.
    """
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always', BackupUpdateWarning)
        warnings.simplefilter('always', PublicationDurabilityWarning)
        receipt = save_function(*args, **kwargs)
    issues = tuple(str(item.message) for item in captured
                   if issubclass(item.category, SAVE_WARNING_TYPES))
    # Preserve unexpected warnings: do not silently suppress deprecations or
    # unrelated runtime issues just because a save was being monitored.
    for item in captured:
        if not issubclass(item.category, SAVE_WARNING_TYPES):
            warnings.warn_explicit(item.message, item.category, item.filename,
                                   item.lineno)
    return receipt, issues


def display_save_diagnostics(editor, issues):
    """Display durable, explicit feedback after the editor accepted the receipt."""
    if not issues:
        return
    from tkinter import messagebox
    summary = '; '.join(issues)
    editor.status.set('Document enregistré avec avertissement : ' + summary)
    messagebox.showwarning(
        'Document enregistré — protection incomplète',
        'Le document principal a bien été enregistré. '
        'Cependant, une garantie de récupération ou de durabilité '
        'n’a pas pu être assurée :\n\n' + '\n'.join(issues)
        + '\n\nVérifiez le dossier de destination et conservez une copie externe.',
        parent=editor,
    )
