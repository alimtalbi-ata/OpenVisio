"""Strict diagram integrity checks and lossless document envelope.

Author: Abdelhalim Talbi.
"""
import math
from .node_geometry import node_dimensions
from .san_multipath import ParallelLinkIndex


def validate_document(data):
    if not isinstance(data, dict):
        raise ValueError("Le document doit être un objet JSON")
    nodes, edges = data.get("nodes", []), data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Collections nodes/edges invalides")
    if len(nodes) > 100000 or len(edges) > 200000:
        raise ValueError("Document trop volumineux")
    layers = data.get("layers", [])
    if not isinstance(layers, list) or len(layers) > 1000:
        raise ValueError("Collection layers invalide")
    layer_ids = set()
    for layer in layers:
        if not isinstance(layer, dict):
            raise ValueError("Calque invalide")
        ident = layer.get("id")
        if not isinstance(ident, str) or not ident or len(ident) > 256 or ident in layer_ids:
            raise ValueError("Identifiant calque invalide ou dupliqué")
        layer_ids.add(ident)
        if "name" in layer and (not isinstance(layer["name"], str) or len(layer["name"]) > 256):
            raise ValueError("Nom de calque invalide")
        for flag in ("visible", "locked"):
            if flag in layer and not isinstance(layer[flag], bool):
                raise ValueError("État de calque invalide : " + flag)
    if "metadata" in data and not isinstance(data["metadata"], dict):
        raise ValueError("Métadonnées invalides")
    node_ids, edge_ids, directed_pairs = set(), set(), ParallelLinkIndex()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Équipement invalide")
        ident = node.get("id")
        if not isinstance(ident, str) or not ident or ident in node_ids:
            raise ValueError("Identifiant équipement invalide ou dupliqué")
        node_ids.add(ident)
        node_dimensions(node)  # Preserve only finite, usable optional shape dimensions.
        for key in ("x", "y"):
            value = node.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Coordonnée invalide")
        for key in ("label", "shape", "hostname", "address", "vendor", "model", "role", "location", "serial_number", "firmware", "notes"):
            if key in node and (not isinstance(node[key], str) or len(node[key]) > 4096):
                raise ValueError("Propriété équipement invalide : " + key)
        if "layer" in node and (not isinstance(node["layer"], str) or node["layer"] not in layer_ids):
            raise ValueError("Calque d'équipement inexistant")
    # A group is an actual editable hierarchy, not an unchecked extension.
    # Validate after all node IDs are known to allow forward references.
    by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        parent = node.get("visio_group_parent")
        if parent is None:
            continue
        if not isinstance(parent, str) or parent not in by_id or parent == node["id"]:
            raise ValueError("Parent de groupe absent ou invalide")
        if by_id[parent].get("shape") != "visio-group":
            raise ValueError("Le parent doit être un groupe")
        if node.get("layer") != by_id[parent].get("layer"):
            raise ValueError("Le groupe et son enfant doivent appartenir au même calque")
        seen = {node["id"]}
        current = parent
        while current is not None:
            if current in seen or len(seen) > 16:
                raise ValueError("Hiérarchie de groupes cyclique ou trop profonde")
            seen.add(current)
            current = by_id[current].get("visio_group_parent")
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Liaison invalide")
        ident = edge.get("id")
        if not isinstance(ident, str) or not ident or ident in edge_ids or ident in node_ids:
            raise ValueError("Identifiant liaison invalide ou dupliqué")
        edge_ids.add(ident)
        source, target = edge.get("from"), edge.get("to")
        if not isinstance(source, str) or not isinstance(target, str) or source not in node_ids or target not in node_ids:
            raise ValueError("Liaison vers un équipement inexistant")
        if source == target:
            raise ValueError("Une liaison ne peut pas relier un équipement à lui-même")
        for key in ("protocol", "source_port", "target_port", "fabric", "speed_gbps", "visio_connector_sheet_id", "label"):
            if key in edge and (not isinstance(edge[key], str) or len(edge[key]) > 4096):
                raise ValueError("Propriété liaison invalide : " + key)
        if "routing" in edge and edge["routing"] not in ("straight", "orthogonal"):
            raise ValueError("Mode de routage invalide")
        if "visio_route" in edge:
            if edge.get("routing") != "orthogonal":
                raise ValueError("Une route VSDX statique doit être orthogonale")
            from .visio_route import validate_visio_route
            try:
                validate_visio_route(edge["visio_route"])
            except ValueError as exc:
                raise ValueError("Route statique VSDX invalide : " + str(exc)) from exc
        if "layer" in edge and (not isinstance(edge["layer"], str) or edge["layer"] not in layer_ids):
            raise ValueError("Calque de liaison inexistant")
        # Validate metadata types before using them as hash keys. This also
        # converts malformed JSON objects/lists into a stable ValueError.
        # Qualified parallel FC links are indexed in average O(1) time.
        directed_pairs.add(source, target, edge)
    # Do not strip top-level fields: older code silently discarded metadata,
    # layer definitions and extension data during save and undo/redo.
    return {**data, "nodes": nodes, "edges": edges}
