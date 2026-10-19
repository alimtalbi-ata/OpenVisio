"""Pure document and selection presentation state. Author: Abdelhalim Talbi."""

def document_summary(document, selected_ids=(), selected_edge=None, dirty=False, path=None):
    """Create an auditable status description independent of Tkinter."""
    nodes = document["nodes"]
    edges = document["edges"]
    selected = len(set(selected_ids))
    selection = f"{selected} équipement(s) sélectionné(s)" if selected else (
        "1 liaison sélectionnée" if selected_edge is not None else "Aucune sélection"
    )
    name = str(path) if path else "Sans titre"
    return f"{name} {'● Modifié' if dirty else '✓ Enregistré'} | {len(nodes)} équipements | {len(edges)} liaisons | {selection}"

def document_dirty(document_snapshot, saved_snapshot):
    """Single source of truth for unsaved state."""
    return document_snapshot != saved_snapshot
