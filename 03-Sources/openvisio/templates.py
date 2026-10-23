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
    ids = {key: uuid4().hex for key, *_ in definition["nodes"]}
    nodes = [
        {"id": ids[key], "label": key, "shape": kind, "x": x, "y": y}
        for key, kind, x, y in definition["nodes"]
    ]
    edges = [
        {"id": uuid4().hex, "from": ids[source], "to": ids[target], "protocol": protocol}
        for source, target, protocol in definition["edges"]
    ]
    return {"nodes": nodes, "edges": edges}
