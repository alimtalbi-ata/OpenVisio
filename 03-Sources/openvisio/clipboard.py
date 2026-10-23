"""Validated, transactional diagram clipboard operations. Author: Abdelhalim Talbi."""
from copy import deepcopy
from uuid import uuid4
from .model import validate


def copy_selection(document, selected_ids):
    from .group_commands import group_members
    ids = group_members(document["nodes"], selected_ids)
    nodes = [deepcopy(n) for n in document["nodes"] if n["id"] in ids]
    selected = {n["id"] for n in nodes}
    edges = [deepcopy(e) for e in document["edges"]
             if e["from"] in selected and e["to"] in selected]
    return {"nodes": nodes, "edges": edges}


def paste_selection(document, payload, offset=40):
    """Paste atomically; never create new objects on a locked or unknown layer.

    The editor owns the document dict, so commit the validated candidate in-place.
    Existing node/edge IDs are never reused; failed validation leaves it untouched.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("nodes", []), list) or not isinstance(payload.get("edges", []), list):
        raise ValueError("Presse-papiers invalide")
    candidate = deepcopy(validate(document))
    layers = {layer["id"]: layer for layer in candidate.get("layers", [])}
    mapping = {}
    # Preallocate all IDs before rewriting parent references. VSDX imports
    # commonly store children before their parent in clipboard selections.
    for original in payload.get("nodes", []):
        if not isinstance(original, dict) or not isinstance(original.get("id"), str):
            raise ValueError("Équipement du presse-papiers invalide")
        if original["id"] in mapping:
            raise ValueError("Identifiant dupliqué dans le presse-papiers")
        mapping[original["id"]] = uuid4().hex
    new_nodes = []
    for original in payload.get("nodes", []):
        node = deepcopy(original)
        node["id"] = mapping[node["id"]]
        parent = node.get("visio_group_parent")
        if parent is not None:
            if parent in mapping:
                node["visio_group_parent"] = mapping[parent]
            else:
                node.pop("visio_group_parent")
        node["x"] += offset
        node["y"] += offset
        layer = layers.get(node.get("layer"))
        if "layer" in node and (layer is None or layer.get("locked", False)):
            node.pop("layer", None)
        new_nodes.append(node)
    new_edges = []
    for original in payload.get("edges", []):
        if not isinstance(original, dict):
            raise ValueError("Liaison du presse-papiers invalide")
        if original.get("from") not in mapping or original.get("to") not in mapping:
            continue
        edge = deepcopy(original)
        edge["id"] = uuid4().hex
        edge["from"] = mapping[edge["from"]]
        edge["to"] = mapping[edge["to"]]
        layer = layers.get(edge.get("layer"))
        if "layer" in edge and (layer is None or layer.get("locked", False)):
            edge.pop("layer", None)
        new_edges.append(edge)
    candidate["nodes"].extend(new_nodes)
    candidate["edges"].extend(new_edges)
    validate(candidate)
    document.clear()
    document.update(candidate)
    return {node["id"] for node in new_nodes}
