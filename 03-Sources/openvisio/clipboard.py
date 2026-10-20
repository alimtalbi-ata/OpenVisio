"""Safe diagram selection duplication with regenerated identifiers. Author: Abdelhalim Talbi."""
from copy import deepcopy
from uuid import uuid4

def copy_selection(document, selected_ids):
    ids = set(selected_ids)
    nodes = [deepcopy(n) for n in document["nodes"] if n["id"] in ids]
    selected = {n["id"] for n in nodes}
    edges = [deepcopy(e) for e in document["edges"] if e["from"] in selected and e["to"] in selected]
    return {"nodes": nodes, "edges": edges}

def paste_selection(document, payload, offset=40):
    mapping = {}
    new_nodes = []
    for original in payload.get("nodes", []):
        node = deepcopy(original)
        mapping[node["id"]] = uuid4().hex
        node["id"] = mapping[node["id"]]
        node["x"] += offset
        node["y"] += offset
        new_nodes.append(node)
    new_edges = []
    for original in payload.get("edges", []):
        if original["from"] not in mapping or original["to"] not in mapping:
            continue
        edge = deepcopy(original)
        edge["id"] = uuid4().hex
        edge["from"] = mapping[edge["from"]]
        edge["to"] = mapping[edge["to"]]
        new_edges.append(edge)
    document["nodes"].extend(new_nodes)
    document["edges"].extend(new_edges)
    return {node["id"] for node in new_nodes}
