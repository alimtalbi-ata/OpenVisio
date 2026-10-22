"""Unambiguous, scalable SAN/Visio connector identity validation.

A fabric may legitimately contain thousands of independent FC paths between
one host and one array. Keep validation linear in the number of links rather
than comparing every path with every previously validated path.
Author: Abdelhalim Talbi.
"""


def physical_link_identity(edge):
    """Return a hashable identity or None for an unqualified physical path.

    Visio sheet IDs are provenance, not fabricated physical port numbers.
    Real endpoint ports take precedence when both are present.
    """
    ports = (edge.get('protocol', 'FC'), edge.get('source_port'),
             edge.get('target_port'), edge.get('fabric', ''))
    if all(isinstance(value, str) and value.strip() for value in ports[1:3]):
        return ('ports', *ports)
    sheet = edge.get('visio_connector_sheet_id')
    if isinstance(sheet, str) and sheet:
        return ('vsdx', sheet)
    return None


class ParallelLinkIndex:
    """O(1) average incremental identity check for each directed pair.

    The first unqualified link is legal. A second link on that pair is
    ambiguous even if it carries ports or a Visio sheet ID. Qualified links
    coexist only when all identities are distinct. Reverse direction is a
    different pair, preserving historical OpenVisio semantics.
    """

    def __init__(self):
        self._by_pair = {}

    def add(self, source, target, edge):
        identity = physical_link_identity(edge)
        previous = self._by_pair.setdefault((source, target), set())
        if previous and (identity is None or None in previous or identity in previous):
            raise ValueError('Liaison orientée dupliquée ou ports insuffisants')
        previous.add(identity)


def reject_ambiguous_parallel_link(previous, edge):
    """Compatibility API for callers holding a list of previous identities.

    New bulk validation uses ParallelLinkIndex to avoid O(n²) comparisons.
    """
    identity = physical_link_identity(edge)
    if previous and (identity is None or any(old is None or old == identity for old in previous)):
        raise ValueError('Liaison orientée dupliquée ou ports insuffisants')
    previous.append(identity)
