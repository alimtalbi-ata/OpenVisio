"""Layer lifecycle and non-destructive view projections. Author: Abdelhalim Talbi."""
from copy import deepcopy
from uuid import uuid4
from .model import validate

def _name(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 256:
        raise ValueError("Nom de calque invalide")
    return value.strip()

def _layer(document, identifier):
    for item in document.get("layers", []):
        if item["id"] == identifier:
            return item
    raise ValueError("Calque inexistant")

def create_layer(document, name):
    name = _name(name)
    result = deepcopy(validate(document))
    if any(x["name"].casefold() == name.casefold() for x in result.get("layers", [])):
        raise ValueError("Un calque porte déjà ce nom")
    identifier = "layer-" + uuid4().hex
    result.setdefault("layers", []).append({"id": identifier, "name": name, "visible": True, "locked": False})
    return validate(result), identifier

def rename_layer(document, layer_id, name):
    name = _name(name)
    result = deepcopy(validate(document))
    layer = _layer(result, layer_id)
    if any(x["id"] != layer_id and x["name"].casefold() == name.casefold() for x in result.get("layers", [])):
        raise ValueError("Un calque porte déjà ce nom")
    layer["name"] = name
    return validate(result)

def delete_layer(document, layer_id):
    result = deepcopy(validate(document))
    if _layer(result, layer_id).get("locked"):
        raise ValueError("Déverrouillez le calque avant de le supprimer")
    result["layers"] = [x for x in result["layers"] if x["id"] != layer_id]
    for item in result["nodes"] + result["edges"]:
        if item.get("layer") == layer_id:
            item.pop("layer")
    return validate(result)

def assign_nodes(document, node_ids, layer_id):
    result = deepcopy(validate(document))
    ids = set(node_ids)
    layers = {x["id"] for x in result.get("layers", [])}
    if layer_id is not None and layer_id not in layers:
        raise ValueError("Calque cible inexistant")
    if not ids.issubset({x["id"] for x in result["nodes"]}):
        raise ValueError("Équipement sélectionné inexistant")
    locked = {x["id"] for x in result.get("layers", []) if x.get("locked")}
    if layer_id in locked or any(x["id"] in ids and x.get("layer") in locked for x in result["nodes"]):
        raise ValueError("Calque verrouillé")
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
    hidden = {x["id"] for x in document.get("layers", []) if x.get("visible", True) is False}
    result = deepcopy(document)
    result["nodes"] = [x for x in result["nodes"] if x.get("layer") not in hidden]
    ids = {x["id"] for x in result["nodes"]}
    result["edges"] = [x for x in result["edges"] if x.get("layer") not in hidden and x["from"] in ids and x["to"] in ids]
    return result

def project_editable(document):
    result = project_visible(document)
    locked = {x["id"] for x in document.get("layers", []) if x.get("locked")}
    result["nodes"] = [x for x in result["nodes"] if x.get("layer") not in locked]
    ids = {x["id"] for x in result["nodes"]}
    result["edges"] = [x for x in result["edges"] if x.get("layer") not in locked and x["from"] in ids and x["to"] in ids]
    return result
