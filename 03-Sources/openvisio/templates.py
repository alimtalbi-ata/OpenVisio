"""Ready-to-edit infrastructure topology templates. Author: Abdelhalim Talbi."""
from uuid import uuid4

TEMPLATES = {
    "SAN double fabric": {
        "nodes": [
            ("host-a", "server", 100, 160), ("host-b", "server", 100, 400),
            ("fabric-a", "san-switch", 400, 160), ("fabric-b", "san-switch", 400, 400),
            ("array", "storage", 700, 280),
        ],
        "edges": [
            ("host-a", "fabric-a", "FC"), ("host-a", "fabric-b", "FC"),
            ("host-b", "fabric-a", "FC"), ("host-b", "fabric-b", "FC"),
            ("fabric-a", "array", "FC"), ("fabric-b", "array", "FC"),
        ],
    },
    "SAN multipath FC (2 fabrics)": {
        "nodes": [
            ("host-a", "server", 100, 160), ("host-b", "server", 100, 420),
            ("fabric-a", "san-switch", 420, 160, "fabric-a"),
            ("fabric-b", "san-switch", 420, 420, "fabric-b"),
            ("array", "storage", 790, 290),
        ],
        "layers": [
            {"id": "fabric-a", "name": "Fabric A", "visible": True, "locked": False},
            {"id": "fabric-b", "name": "Fabric B", "visible": True, "locked": False},
        ],
        # Each tuple is (source, target, protocol, physical-link metadata).
        # Ports are illustrative template labels, not discovered switch WWPNs.
        "edges": [
            ("host-a", "fabric-a", "FC", {"fabric": "A", "source_port": "hba0", "target_port": "fc1", "label": "A / HBA0", "layer": "fabric-a"}),
            ("host-a", "fabric-a", "FC", {"fabric": "A", "source_port": "hba1", "target_port": "fc2", "label": "A / HBA1", "layer": "fabric-a"}),
            ("host-a", "fabric-b", "FC", {"fabric": "B", "source_port": "hba2", "target_port": "fc1", "label": "B / HBA2", "layer": "fabric-b"}),
            ("host-a", "fabric-b", "FC", {"fabric": "B", "source_port": "hba3", "target_port": "fc2", "label": "B / HBA3", "layer": "fabric-b"}),
            ("host-b", "fabric-a", "FC", {"fabric": "A", "source_port": "hba0", "target_port": "fc3", "label": "A / HBA0", "layer": "fabric-a"}),
            ("host-b", "fabric-a", "FC", {"fabric": "A", "source_port": "hba1", "target_port": "fc4", "label": "A / HBA1", "layer": "fabric-a"}),
            ("host-b", "fabric-b", "FC", {"fabric": "B", "source_port": "hba2", "target_port": "fc3", "label": "B / HBA2", "layer": "fabric-b"}),
            ("host-b", "fabric-b", "FC", {"fabric": "B", "source_port": "hba3", "target_port": "fc4", "label": "B / HBA3", "layer": "fabric-b"}),
            ("fabric-a", "array", "FC", {"fabric": "A", "source_port": "fc31", "target_port": "ct0-fc0", "label": "A / CT0", "layer": "fabric-a"}),
            ("fabric-a", "array", "FC", {"fabric": "A", "source_port": "fc32", "target_port": "ct1-fc0", "label": "A / CT1", "layer": "fabric-a"}),
            ("fabric-b", "array", "FC", {"fabric": "B", "source_port": "fc31", "target_port": "ct0-fc1", "label": "B / CT0", "layer": "fabric-b"}),
            ("fabric-b", "array", "FC", {"fabric": "B", "source_port": "fc32", "target_port": "ct1-fc1", "label": "B / CT1", "layer": "fabric-b"}),
        ],
    },
    "NAS et clients": {
        "nodes": [
            ("linux", "server", 100, 140), ("windows", "server", 100, 370),
            ("lan", "network-switch", 390, 260), ("nas", "nas", 690, 260),
        ],
        "edges": [
            ("linux", "lan", "NFS"), ("windows", "lan", "SMB"),
            ("lan", "nas", "Ethernet"),
        ],
    },
    "Application trois tiers": {
        "nodes": [
            ("web", "application", 100, 250), ("app", "server", 390, 250),
            ("db", "database", 680, 250),
        ],
        "edges": [("web", "app", "Ethernet"), ("app", "db", "Ethernet")],
    },
}

def create_template(name):
    """Return a fresh independent document with no shared IDs."""
    if name not in TEMPLATES:
        raise ValueError("Unknown infrastructure template")
    definition = TEMPLATES[name]
    ids = {row[0]: uuid4().hex for row in definition["nodes"]}
    nodes = []
    for row in definition["nodes"]:
        key, kind, x, y = row[:4]
        node = {"id": ids[key], "label": key, "shape": kind, "x": x, "y": y}
        if len(row) == 5:
            node["layer"] = row[4]
        nodes.append(node)
    edges = []
    for row in definition["edges"]:
        source, target, protocol = row[:3]
        edge = {"id": uuid4().hex, "from": ids[source], "to": ids[target],
                "protocol": protocol}
        if len(row) == 4:
            edge.update(row[3])
        edges.append(edge)
    result = {"nodes": nodes, "edges": edges}
    if "layers" in definition:
        result["layers"] = [dict(layer) for layer in definition["layers"]]
    return result
