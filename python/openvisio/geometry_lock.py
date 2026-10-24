"""Protect SAN path geometry across UI and headless editing commands.

A link locked by its own fabric layer, or by either endpoint's layer, must
not be rerouted indirectly by dragging, aligning or resizing its endpoint.
Read-only metadata changes remain permitted on otherwise editable nodes.
Author: Abdelhalim Talbi.
"""


def assert_geometry_editable(document, node_ids):
    """Raise ValueError before any geometry mutation affecting protected links.

    The check is linear in the diagram size and never mutates the document.
    Callers must expand selected groups to descendants before calling it.
    """
    selected = set(node_ids)
    if not selected:
        return
    locked = {layer['id'] for layer in document.get('layers', [])
              if layer.get('locked', False)}
    by_id = {node['id']: node for node in document['nodes']}
    if any(by_id[ident].get('layer') in locked for ident in selected):
        raise ValueError('Géométrie non modifiable : équipement sur calque verrouillé')
    for edge in document['edges']:
        source, target = edge['from'], edge['to']
        if source not in selected and target not in selected:
            continue
        if (edge.get('layer') in locked
                or by_id[source].get('layer') in locked
                or by_id[target].get('layer') in locked):
            raise ValueError('Géométrie non modifiable : liaison SAN verrouillée')
