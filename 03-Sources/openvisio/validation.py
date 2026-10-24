"""Strict diagram integrity checks. Author: Abdelhalim Talbi."""
import math
import json

def validate_document(data):
    if not isinstance(data, dict):
        raise ValueError("Le document doit être un objet JSON")
    nodes, edges = data.get("nodes", []), data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Collections nodes/edges invalides")
    if len(nodes) > 100000 or len(edges) > 200000:
        raise ValueError("Document trop volumineux")
    node_ids, edge_ids, directed_pairs = set(), set(), set()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Équipement invalide")
        ident = node.get("id")
        if not isinstance(ident, str) or not ident or ident in node_ids:
            raise ValueError("Identifiant équipement invalide ou dupliqué")
        node_ids.add(ident)
        for key in ("x", "y"):
            value = node.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Coordonnée invalide")
        for key in ("label", "shape", "hostname", "address", "vendor", "model", "role", "location", "serial_number", "firmware", "notes"):
            if key in node and (not isinstance(node[key], str) or len(node[key]) > 4096):
                raise ValueError("Propriété équipement invalide : " + key)
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
        if (source, target) in directed_pairs:
            raise ValueError("Liaison orientée dupliquée")
        directed_pairs.add((source, target))
        for key in ("protocol", "source_port", "target_port", "fabric", "speed_gbps"):
            if key in edge and (not isinstance(edge[key], str) or len(edge[key]) > 4096):
                raise ValueError("Propriété liaison invalide : " + key)
    result = {"nodes": nodes, "edges": edges}
    if "layers" not in data and any("layer" in item for item in nodes + edges):
        raise ValueError("Référence à un calque sans collection de calques")
    if "layers" in data:
        layers = data["layers"]
        if not isinstance(layers, list) or len(layers) > 1024:
            raise ValueError("Collection de calques invalide")
        layer_ids = set()
        for layer in layers:
            if not isinstance(layer, dict):
                raise ValueError("Calque invalide")
            ident, name = layer.get("id"), layer.get("name")
            if not isinstance(ident, str) or not ident or len(ident) > 256 or ident in layer_ids:
                raise ValueError("Identifiant calque invalide ou dupliqué")
            if not isinstance(name, str) or not name.strip() or len(name) > 256:
                raise ValueError("Nom de calque invalide")
            for key in ("visible", "locked"):
                if key in layer and not isinstance(layer[key], bool):
                    raise ValueError("Propriété calque invalide : " + key)
            layer_ids.add(ident)
        for item in nodes + edges:
            if "layer" in item:
                layer_ref = item["layer"]
                if not isinstance(layer_ref, str) or layer_ref not in layer_ids:
                    raise ValueError("Référence à un calque inexistante ou invalide")
        result["layers"] = layers
    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, dict) or len(metadata) > 128:
            raise ValueError("Métadonnées invalides")
        if any(not isinstance(key, str) for key in metadata):
            raise ValueError("Clé de métadonnée non textuelle")
        try:
            json.dumps(metadata, allow_nan=False)
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise ValueError("Métadonnées non sérialisables en JSON") from exc
        result["metadata"] = metadata
    return result
