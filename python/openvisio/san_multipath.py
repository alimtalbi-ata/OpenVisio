"""Linear-time identity validation for parallel SAN paths. Author: Abdelhalim Talbi."""


def physical_link_identity(edge):
    ports = (edge.get("protocol", "FC"), edge.get("source_port"),
             edge.get("target_port"), edge.get("fabric", ""))
    if all(isinstance(value, str) and value.strip() for value in ports[1:3]):
        return ("ports", *ports)
    sheet = edge.get("visio_connector_sheet_id")
    if isinstance(sheet, str) and sheet:
        return ("vsdx", sheet)
    return None


class ParallelLinkIndex:
    """First unqualified path is valid; duplicates or ambiguous paths fail."""

    def __init__(self):
        self._by_pair = {}

    def add(self, source, target, edge):
        identity = physical_link_identity(edge)
        previous = self._by_pair.setdefault((source, target), set())
        if previous and (identity is None or None in previous or identity in previous):
            raise ValueError("Liaison orientée dupliquée ou ports insuffisants")
        previous.add(identity)


def reject_ambiguous_parallel_link(previous, edge):
    """Compatibility API for existing list-based callers."""
    identity = physical_link_identity(edge)
    if previous and (identity is None or any(old is None or old == identity for old in previous)):
        raise ValueError("Liaison orientée dupliquée ou ports insuffisants")
    previous.append(identity)
