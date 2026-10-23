"""Layer lifecycle, protection and non-destructive view projections.

Author: Abdelhalim Talbi.
All mutations validate a copy so undo/redo and persistence retain their data.
"""
from copy import deepcopy
from uuid import uuid4
from .model import validate


def _checked_name(name):
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 256:
        raise ValueError("Nom de calque invalide")
    return name.strip()


def _layer(result, layer_id):
    for layer in result.get("layers", []):
        if layer["id"] == layer_id:
            return layer
    raise ValueError("Calque inexistant")


def create_layer(document, name):
    normalized = _checked_name(name)
    result = deepcopy(validate(document))
    if any(layer.get("name", "").casefold() == normalized.casefold()
           for layer in result.get("layers", [])):
        raise ValueError("Un calque porte déjà ce nom")
    identifier = "layer-" + uuid4().hex
    result.setdefault("layers", []).append({"id": identifier, "name": normalized, "visible": True, "locked": False})
    return validate(result), identifier


def rename_layer(document, layer_id, name):
    normalized = _checked_name(name)
    result = deepcopy(validate(document))
    layer = _layer(result, layer_id)
    if any(other["id"] != layer_id and other.get("name", "").casefold() == normalized.casefold()
           for other in result.get("layers", [])):
        raise ValueError("Un calque porte déjà ce nom")
    layer["name"] = normalized
    return validate(result)


def delete_layer(document, layer_id):
    """Detach objects instead of deleting them; require unlocking first."""
    result = deepcopy(validate(document))
    layer = _layer(result, layer_id)
    if layer.get("locked", False):
        raise ValueError("Déverrouillez le calque avant de le supprimer")
    result["layers"] = [item for item in result["layers"] if item["id"] != layer_id]
    for item in result["nodes"] + result["edges"]:
        if item.get("layer") == layer_id:
            item.pop("layer")
    return validate(result)


def assign_nodes(document, node_ids, layer_id):
    result = deepcopy(validate(document))
    ids = set(node_ids)
    layers = {layer["id"] for layer in result.get("layers", [])}
    if layer_id is not None and layer_id not in layers:
        raise ValueError("Calque cible inexistant")
    actual_ids = {node["id"] for node in result["nodes"]}
    if not ids.issubset(actual_ids):
        raise ValueError("Équipement sélectionné inexistant")
    from .group_commands import group_members
    ids = group_members(result["nodes"], ids)
    # A child cannot be moved to a different layer while remaining attached
    # to a parent on the previous layer; this would split an editable group.
    by_id = {node["id"]: node for node in result["nodes"]}
    if any(node.get("visio_group_parent") not in ids and
           node.get("visio_group_parent") is not None and
           node.get("layer") != layer_id
           for node in result["nodes"] if node["id"] in ids):
        raise ValueError("Déplacez le groupe parent plutôt qu'un enfant isolé")
    locked = {layer["id"] for layer in result.get("layers", []) if layer.get("locked", False)}
    if layer_id in locked:
        raise ValueError("Calque cible verrouillé")
    if any(node["id"] in ids and node.get("layer") in locked for node in result["nodes"]):
        raise ValueError("Impossible de déplacer un équipement depuis un calque verrouillé")
    for node in result["nodes"]:
        if node["id"] in ids:
            if layer_id is None:
                node.pop("layer", None)
            else:
                node["layer"] = layer_id
    return validate(result)


def set_visibility(document, layer_id, visible):
    if not isinstance(visible, bool):
        raise ValueError("Visibilité invalide")
    result = deepcopy(validate(document))
    _layer(result, layer_id)["visible"] = visible
    return validate(result)


def set_locked(document, layer_id, locked):
    if not isinstance(locked, bool):
        raise ValueError("Verrouillage invalide")
    result = deepcopy(validate(document))
    _layer(result, layer_id)["locked"] = locked
    return validate(result)


def project_visible(document):
    """Non-destructive projection; hidden links and incident links are not drawn."""
    hidden = {layer["id"] for layer in document.get("layers", [])
              if layer.get("visible", True) is False}
    if not hidden:
        return deepcopy(document)
    nodes = [node for node in document["nodes"] if node.get("layer") not in hidden]
    visible_ids = {node["id"] for node in nodes}
    edges = [edge for edge in document["edges"]
             if edge.get("layer") not in hidden
             and edge["from"] in visible_ids and edge["to"] in visible_ids]
    return deepcopy({**document, "nodes": nodes, "edges": edges})


def project_editable(document):
    """Exclude locked layers and their incident links from editing hit-tests."""
    visible = project_visible(document)
    locked = {layer["id"] for layer in document.get("layers", [])
              if layer.get("locked", False)}
    if not locked:
        return visible
    nodes = [node for node in visible["nodes"] if node.get("layer") not in locked]
    ids = {node["id"] for node in nodes}
    edges = [edge for edge in visible["edges"]
             if edge.get("layer") not in locked
             and edge["from"] in ids and edge["to"] in ids]
    return deepcopy({**visible, "nodes": nodes, "edges": edges})
