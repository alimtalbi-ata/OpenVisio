"""Pure selection state transitions, independent of Tkinter. Author: Abdelhalim Talbi."""

def select_node(selected_ids, node_id, *, ctrl=False):
    """Return selected node IDs and primary node after a click."""
    ids = set(selected_ids)
    if node_id is None:
        return set(), None
    if ctrl:
        if node_id in ids:
            ids.remove(node_id)
        else:
            ids.add(node_id)
        return ids, None
    if node_id in ids and len(ids) > 1:
        return ids, node_id
    return {node_id}, node_id

def select_rectangle(previous_ids, hit_ids, *, additive=False):
    """Compute marquee selection from the selection saved at drag start."""
    result = set(hit_ids)
    if additive:
        result.update(previous_ids)
    return result

def reconcile_selection(document, selected_ids, primary_id=None, edge_id=None):
    """Discard IDs no longer present after an edit, load or history transition."""
    valid_nodes = {n["id"] for n in document["nodes"]}
    valid_edges = {e["id"] for e in document["edges"]}
    ids = set(selected_ids) & valid_nodes
    primary = primary_id if primary_id in valid_nodes else None
    edge = edge_id if edge_id in valid_edges and not ids and primary is None else None
    return ids, primary, edge
