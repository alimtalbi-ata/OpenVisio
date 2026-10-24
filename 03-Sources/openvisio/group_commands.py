"""Native, validated group editing for imported Visio and OpenVisio diagrams.

Groups use the existing visio_group_parent field; coordinates are always
absolute document coordinates, so grouping does not alter connectors.
Author: Abdelhalim Talbi.
"""
from copy import deepcopy
from uuid import uuid4
from .model import validate
from .node_geometry import node_bounds, node_dimensions, checked_size


def _locked_layers(document):
    """IDs of layers whose diagram content cannot be edited."""
    return {layer["id"] for layer in document.get("layers", [])
            if layer.get("locked", False)}


def _reject_locked_nodes(document, node_ids):
    locked = _locked_layers(document)
    if any(node["id"] in node_ids and node.get("layer") in locked
           for node in document["nodes"]):
        raise ValueError("Modification de groupe interdite : calque verrouillé")




def group_members(nodes, selected_ids):
    """Return selected nodes plus all recursive descendants, without mutation."""
    selected = set(selected_ids)
    if not selected:
        return set()
    children = {}
    for node in nodes:
        parent = node.get('visio_group_parent')
        if parent is not None:
            children.setdefault(parent, []).append(node['id'])
    result = set(selected)
    pending = list(selected)
    while pending:
        for child in children.get(pending.pop(), ()):
            if child not in result:
                result.add(child)
                pending.append(child)
    return result


def group_selection(document, node_ids, *, ident=None, label='Groupe'):
    """Group >=2 peer nodes without changing their absolute coordinates."""
    original = validate(document)
    chosen = set(node_ids)
    nodes = {n['id']: n for n in original['nodes']}
    if len(chosen) < 2 or not chosen.issubset(nodes):
        raise ValueError('Sélectionnez au moins deux équipements existants')
    parents = {nodes[i].get('visio_group_parent') for i in chosen}
    layers = {nodes[i].get('layer') for i in chosen}
    if len(parents) != 1 or len(layers) != 1:
        raise ValueError('Les équipements doivent partager le même groupe parent et le même calque')
    _reject_locked_nodes(original, chosen)
    if any(n.get('shape') == 'visio-group' for n in (nodes[i] for i in chosen)):
        # Existing nested groups are supported; selected peers only.
        pass
    new_id = ident or uuid4().hex
    if not isinstance(new_id, str) or not new_id or new_id in nodes:
        raise ValueError('Identifiant de groupe invalide ou déjà utilisé')
    bounds = [node_bounds(nodes[i]) for i in chosen]
    x0, y0 = min(b[0] for b in bounds) - 24, min(b[1] for b in bounds) - 24
    x1, y1 = max(b[2] for b in bounds) + 24, max(b[3] for b in bounds) + 24
    checked_size(x1 - x0, 'width')
    checked_size(y1 - y0, 'height')
    group = {'id': new_id, 'x': (x0+x1)/2, 'y': (y0+y1)/2,
             'width': x1-x0, 'height': y1-y0,
             'label': label, 'shape': 'visio-group'}
    layer = next(iter(layers))
    if layer is not None:
        group['layer'] = layer
    parent = next(iter(parents))
    if parent is not None:
        group['visio_group_parent'] = parent
    result = deepcopy(original)
    for node in result['nodes']:
        if node['id'] in chosen:
            node['visio_group_parent'] = new_id
    result['nodes'].append(group)
    return validate(result), new_id


def ungroup_selection(document, group_ids):
    """Remove group envelopes, keeping child shapes, links and absolute positions."""
    original = validate(document)
    chosen = set(group_ids)
    nodes = {n['id']: n for n in original['nodes']}
    if not chosen or not chosen.issubset(nodes) or any(nodes[i].get('shape') != 'visio-group' for i in chosen):
        raise ValueError('Sélectionnez uniquement des groupes existants')
    _reject_locked_nodes(original, chosen)
    if any(e['from'] in chosen or e['to'] in chosen for e in original['edges']):
        raise ValueError('Groupe connecté : déconnectez ses liaisons avant de le dissocier')
    result = deepcopy(original)
    parent_of = {i: nodes[i].get('visio_group_parent') for i in chosen}
    for node in result['nodes']:
        parent = node.get('visio_group_parent')
        while parent in chosen:
            parent = parent_of[parent]
        if 'visio_group_parent' in node and node['id'] not in chosen:
            if parent is None:
                node.pop('visio_group_parent')
            else:
                node['visio_group_parent'] = parent
    result['nodes'] = [n for n in result['nodes'] if n['id'] not in chosen]
    return validate(result)


def resize_group(document, group_id, width, height):
    """Scale descendants and their dimensions around the group centre atomically."""
    original = validate(document)
    width, height = checked_size(width, 'width'), checked_size(height, 'height')
    root = next((n for n in original['nodes'] if n['id'] == group_id), None)
    if root is None or root.get('shape') != 'visio-group':
        raise ValueError('Groupe introuvable')
    old_w, old_h = node_dimensions(root)
    sx, sy = width/old_w, height/old_h
    ids = group_members(original['nodes'], {group_id})
    _reject_locked_nodes(original, ids)
    locked = _locked_layers(original)
    # Resizing a group moves its children and therefore the endpoints of any
    # incident links. A protected SAN link must not be rerouted indirectly.
    if any(edge.get('layer') in locked and
           (edge['from'] in ids or edge['to'] in ids)
           for edge in original['edges']):
        raise ValueError('Redimensionnement interdit : liaison sur calque verrouillé')
    result = deepcopy(original)
    for node in result['nodes']:
        if node['id'] not in ids:
            continue
        nw, nh = node_dimensions(node)
        node['width'] = checked_size(nw*sx, 'width')
        node['height'] = checked_size(nh*sy, 'height')
        node['x'] = root['x'] + (node['x']-root['x'])*sx
        node['y'] = root['y'] + (node['y']-root['y'])*sy
    return validate(result)
