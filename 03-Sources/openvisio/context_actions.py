"""Pure context menu selection and action policy. Author: Abdelhalim Talbi."""

def context_selection(node_id, edge_id, selected_ids):
    """Preserve a multi-selection when right-clicking a member."""
    if node_id is not None:
        ids = set(selected_ids)
        if node_id not in ids:
            ids = {node_id}
        return ids, node_id, None
    if edge_id is not None:
        return set(), None, edge_id
    return set(), None, None

def context_actions(node_id=None, edge_id=None):
    """Return the action IDs to present for a context."""
    if node_id is not None:
        return ("properties", "link", "duplicate", "delete")
    if edge_id is not None:
        return ("link_properties", "delete")
    return ("add_server", "paste", "fit")
