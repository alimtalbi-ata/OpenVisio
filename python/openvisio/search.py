"""Case-insensitive equipment search across common infrastructure metadata."""
FIELDS = ("label", "hostname", "address", "vendor", "model", "shape")

def find_nodes(nodes, query):
    term = query.strip().casefold()
    if not term:
        return []
    return [node for node in nodes if any(term in str(node.get(field, "")).casefold() for field in FIELDS)]
