"""Deterministic obstacle-avoiding orthogonal routing for rectangular nodes.

Explicit opt-in (edge['routing'] == 'orthogonal'). Never silently degrades to
straight segments. All segments are checked against *all* equipment rectangles.
Not a Visio dynamic glue or group-transform implementation.
Author: Abdelhalim Talbi.
"""
from bisect import bisect_left, bisect_right
from collections import OrderedDict
from copy import deepcopy
from functools import lru_cache
from heapq import heappush, heappop
from math import isfinite

from .connector_geometry import connector_endpoints, lane_endpoints
from .parallel_geometry import display_edges
from .lane_clearance import lane_clearance, expanded_intermediate_bounds
from .node_geometry import (node_bounds, node_half_sizes,
                            DEFAULT_WIDTH, DEFAULT_HEIGHT)
from .geometry_lock import assert_link_editable

HALF_WIDTH = 70.0
HALF_HEIGHT = 30.0
CLEARANCE = 12.0
STUB = CLEARANCE + 1.0
# Bound the *local* search, not the total number of nodes in a diagram.
# Every returned segment is checked against the complete obstacle set.
MAX_GRID_CELLS = 32000
INITIAL_CORRIDOR = 160.0
MAX_CORRIDOR_ATTEMPTS = 12
BEND_PENALTY = 18.0


class RoutingError(ValueError):
    """The requested safe orthogonal path could not be constructed."""


class RoutingDensityError(RoutingError):
    """A candidate exceeds the bounded search grid; other ports may work."""


def _bounds(node, clearance=CLEARANCE):
    x, y = float(node['x']), float(node['y'])
    if not (isfinite(x) and isfinite(y)):
        raise RoutingError('Coordonnées de routage non finies')
    return node_bounds(node, padding=clearance)


def _blocked(p, q, rectangles):
    """True when an axis-aligned segment crosses an expanded rectangle interior."""
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        lo, hi = sorted((y1, y2))
        return any(left < x1 < right and max(lo, top) < min(hi, bottom)
                   for left, top, right, bottom in rectangles)
    if y1 == y2:
        lo, hi = sorted((x1, x2))
        return any(top < y1 < bottom and max(lo, left) < min(hi, right)
                   for left, top, right, bottom in rectangles)
    raise RoutingError('Un segment orthogonal ne peut pas être diagonal')



class RectangleIndex:
    """Exact interval filter for repeated corridor/segment queries.

    Sorted left edges plus prefix-max right edges discard all rectangles that
    provably cannot overlap a query's X interval. The Y overlap is checked
    exactly; no rasterisation, approximation or dropped oversized shapes.
    """

    def __init__(self, entries):
        # Entries are (node_id, expanded_bounds) pairs.
        ordered = sorted(entries, key=lambda item: (item[1][0], str(item[0])))
        self._items = tuple(ordered)
        self._lefts = tuple(rect[0] for _, rect in ordered)
        max_right = float('-inf')
        prefix = []
        for _, rect in ordered:
            max_right = max(max_right, rect[2])
            prefix.append(max_right)
        self._prefix_rights = tuple(prefix)

    def query_items(self, window):
        """Yield every overlapping rectangle and its node id (inclusive edges)."""
        left, top, right, bottom = window
        start = bisect_left(self._prefix_rights, left)
        stop = bisect_right(self._lefts, right)
        for node_id, rect in self._items[start:stop]:
            if rect[2] >= left and rect[1] <= bottom and rect[3] >= top:
                yield node_id, rect

    def query(self, window):
        return [rect for _, rect in self.query_items(window)]


def _static_route_window(edge):
    """Return a bounded world-space envelope for a candidate static VSDX route.

    This is only a broad-phase filter: strict route validation and exact
    rectangle/segment checks remain authoritative. Invalid metadata returns
    None so callers conservatively inspect every node.
    """
    record = edge.get('visio_route') if isinstance(edge, dict) else None
    if not isinstance(record, dict):
        return None
    points = record.get('points')
    if not isinstance(points, (list, tuple)) or not 2 <= len(points) <= 2048:
        return None
    xs, ys = [], []
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return None
        x, y = point
        if (isinstance(x, bool) or not isinstance(x, (int, float))
                or isinstance(y, bool) or not isinstance(y, (int, float))):
            return None
        x, y = float(x), float(y)
        if not (isfinite(x) and isfinite(y) and abs(x) <= 10_000_000.0
                and abs(y) <= 10_000_000.0):
            return None
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


class RoutingScene:
    """Immutable node-geometry snapshot with bounded per-edge route memoization.

    One scene is shared by canvas rendering, selection and exporters when node
    geometry is unchanged. Edge attributes irrelevant to geometry are excluded
    from the key; changed endpoints/mode or changed node geometry invalidate it.
    Cached routes are returned as new lists to prevent caller mutation.
    """

    MAX_ROUTES = 8192

    def __init__(self, signature):
        self.nodes = {
            node_id: {'id': node_id, 'x': x, 'y': y,
                      'width': width, 'height': height, 'shape': shape}
            for node_id, x, y, width, height, shape in signature
        }
        self._geometry = None
        self._routing_index = None
        self._routes = OrderedDict()
        # Exact conservative query envelopes for routes computed in this scene.
        self._route_dependencies = {}

    def geometry(self):
        if self._geometry is None:
            indexed = {key: _bounds(node) for key, node in self.nodes.items()}
            obstacles = tuple(indexed.values())
            outer = (min(r[0] for r in obstacles), min(r[1] for r in obstacles),
                     max(r[2] for r in obstacles), max(r[3] for r in obstacles))
            self._geometry = (indexed, obstacles, outer,
                              RectangleIndex(indexed.items()))
        return self._geometry

    def routing_obstacle_index(self):
        """Group containers are visual envelopes, not solid routing obstacles.

        Their child shapes remain individual obstacles. The general geometry
        index still includes groups for viewport culling and selection.
        """
        if self._routing_index is None:
            indexed = self.geometry()[0]
            self._routing_index = RectangleIndex(
                (key, rect) for key, rect in indexed.items()
                if self.nodes[key].get('shape') != 'visio-group')
        return self._routing_index

    def route_points(self, edge):
        # Public static VSDX waypoints are used only while they remain attached
        # to the exact imported endpoint geometry and do not cross equipment.
        # This happens before memoization because two parallel connectors may
        # carry distinct imported routes for identical endpoint pairs.
        if isinstance(edge, dict) and edge.get('visio_route') is not None:
            try:
                source = self.nodes[edge['from']]
                target = self.nodes[edge['to']]
                from .visio_route import active_visio_route
                # Broad phase: the route envelope is queried against the existing
                # rectangle index. Its padded bounds can add candidates, never
                # remove a real blocker. Exact endpoint/segment checks remain the
                # authority. Untrusted metadata retains the full-scan fail-safe.
                window = _static_route_window(edge)
                route_nodes = self.nodes.values()
                if window is not None:
                    candidate_ids = {node_id for node_id, _ in
                                     self.routing_obstacle_index().query_items(window)}
                    candidate_ids.update((edge['from'], edge['to']))
                    route_nodes = tuple(self.nodes[node_id] for node_id in candidate_ids
                                        if node_id in self.nodes)
                preserved = active_visio_route(edge, source, target, route_nodes)
            except (KeyError, TypeError, ValueError, OverflowError):
                preserved = None
            if preserved is not None:
                return list(preserved)
        key = (edge['from'], edge['to'], edge.get('routing', 'straight'))
        lane = float(edge.get('_lane_offset', 0.0))
        if lane:
            key += (lane,)
        if key in self._routes:
            self._routes.move_to_end(key)
            return list(self._routes[key])
        windows = []
        # Parallel orthogonal lanes need different obstacle clearance around
        # *intermediate* equipment. Their original ports and safety checks
        # remain unchanged. A congested diagram must still be routable using
        # the original safe path when extra separation is impossible.
        extra = lane_clearance(lane, CLEARANCE) if lane and edge.get('routing') == 'orthogonal' else 0.0
        if extra:
            try:
                points = _route_points_in_scene(edge, self, query_windows=windows,
                                                extra_clearance=extra)
            except RoutingError:
                points = _route_points_in_scene(edge, self, query_windows=windows)
        else:
            points = _route_points_in_scene(edge, self, query_windows=windows)
        self._routes[key] = tuple(points)
        if windows:
            self._route_dependencies[key] = (
                min(w[0] for w in windows), min(w[1] for w in windows),
                max(w[2] for w in windows), max(w[3] for w in windows))
        if len(self._routes) > self.MAX_ROUTES:
            evicted, _ = self._routes.popitem(last=False)
            self._route_dependencies.pop(evicted, None)
        return list(points)

    def inherit_unaffected_routes(self, previous):
        """Reuse only routes provably independent of edited node geometry.

        Every spatial query of the original orthogonal search was recorded.
        If neither old nor new bounds of changed *non-endpoint* nodes touch
        any query, the search sees identical obstacles and returns the exact
        same path. Changes to the global outer bounds disable this shortcut:
        the corridor expansion stop condition depends on those bounds.
        """
        if previous is self or not previous._routes or self._routes:
            return 0
        old_ids = tuple(previous.nodes)
        if tuple(self.nodes) != old_ids:
            return 0  # add/remove/reorder: avoid speculative reuse
        changed = [key for key in old_ids if previous.nodes[key] != self.nodes[key]]
        if not changed or len(changed) > 2:
            return 0
        if previous.geometry()[2] != self.geometry()[2]:
            return 0
        changed_bounds = [rect for key in changed
                          for rect in (_bounds(previous.nodes[key]), _bounds(self.nodes[key]))]
        reused = 0
        for key, points in previous._routes.items():
            source, target, mode = key[:3]
            if source in changed or target in changed:
                continue
            if mode == 'orthogonal':
                # Lane-aware searches use expanded obstacles. Their dependency
                # bounds are not equivalent to the base scene's node bounds.
                # Recompute instead of risking a stale route after an edit.
                if len(key) > 3 and key[3]:
                    continue
                envelope = previous._route_dependencies.get(key)
                if envelope is None or any(_intersects(rect, envelope)
                                           for rect in changed_bounds):
                    continue
                self._route_dependencies[key] = envelope
            elif mode != 'straight':
                continue
            self._routes[key] = points
            reused += 1
        return reused


@lru_cache(maxsize=6)
def _scene_for_signature(signature):
    return RoutingScene(signature)


def routing_scene(nodes):
    """Return a cached scene keyed by *all* geometry, never by mutable IDs alone.

    Width and height are normalised to their existing defaults, so a diagram
    opened from older releases and its equivalent explicit-size representation
    use identical geometry. Node order remains in the key for determinism.
    """
    values = nodes.values() if isinstance(nodes, dict) else nodes
    signature = tuple((node['id'], node['x'], node['y'],
                       node.get('width', DEFAULT_WIDTH),
                       node.get('height', DEFAULT_HEIGHT),
                       node.get('shape', 'server')) for node in values)
    previous = getattr(routing_scene, '_latest_scene', None)
    scene = _scene_for_signature(signature)
    if previous is not None and scene is not previous:
        scene.inherit_unaffected_routes(previous)
    routing_scene._latest_scene = scene
    return scene

def _port(node, side, lane=0.0):
    x, y = float(node['x']), float(node['y'])
    hw, hh = node_half_sizes(node)
    # Offset along the boundary tangent, not across the equipment interior.
    # The lane generator bounds this value, but clamp for direct callers too.
    if side in ('right', 'left'):
        y += max(-hh + 1e-6, min(hh - 1e-6, lane))
        sign = 1 if side == 'right' else -1
        return (x + sign * hw, y), (x + sign * (hw + STUB), y)
    x += max(-hw + 1e-6, min(hw - 1e-6, lane))
    sign = 1 if side == 'bottom' else -1
    return (x, y + sign * hh), (x, y + sign * (hh + STUB))


def _simplify(points):
    out = []
    for point in points:
        if out and point == out[-1]:
            continue
        out.append(point)
        while len(out) >= 3:
            a, b, c = out[-3:]
            if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
                out.pop(-2)
            else:
                break
    return out


def _corridor(start, finish, margin):
    return (min(start[0], finish[0]) - margin,
            min(start[1], finish[1]) - margin,
            max(start[0], finish[0]) + margin,
            max(start[1], finish[1]) + margin)


def _intersects(rect, window):
    return (rect[0] <= window[2] and rect[2] >= window[0]
            and rect[1] <= window[3] and rect[3] >= window[1])


def _local_grid_path(start, finish, obstacles, window):
    """Route inside a bounded corridor, considering every intersecting obstacle.

    No geometry outside this window can affect a path wholly inside it. Use
    clipped obstacle *coordinates* but full rectangles for collision checks,
    preventing routes through shapes spanning the corridor boundary.
    """
    local = (obstacles.query(window) if isinstance(obstacles, RectangleIndex)
             else [r for r in obstacles if _intersects(r, window)])
    left, top, right, bottom = window
    xs = sorted({start[0], finish[0], left, right,
                 *(v for r in local for v in (max(left, r[0]), min(right, r[2])))})
    ys = sorted({start[1], finish[1], top, bottom,
                 *(v for r in local for v in (max(top, r[1]), min(bottom, r[3])))})
    if len(xs) * len(ys) > MAX_GRID_CELLS:
        raise RoutingDensityError('Routage orthogonal trop dense pour la limite de sécurité')
    return _grid_path(start, finish, local, xs=xs, ys=ys)


def _grid_path(start, finish, obstacles, *, xs=None, ys=None):
    """Dijkstra over sparse Manhattan visibility grid, penalizing extra bends."""
    if xs is None:
        xs = sorted({start[0], finish[0], *(v for r in obstacles for v in (r[0], r[2]))})
    if ys is None:
        ys = sorted({start[1], finish[1], *(v for r in obstacles for v in (r[1], r[3]))})
    if len(xs) * len(ys) > MAX_GRID_CELLS:
        raise RoutingDensityError('Routage orthogonal trop dense pour la limite de sécurité')
    xidx = {v: i for i, v in enumerate(xs)}
    yidx = {v: i for i, v in enumerate(ys)}
    origin = (xidx[start[0]], yidx[start[1]], 0)
    destination = (xidx[finish[0]], yidx[finish[1]])
    distances = {origin: 0.0}
    previous = {}
    def heuristic(ix, iy):
        return abs(xs[ix] - finish[0]) + abs(ys[iy] - finish[1])
    queue = [(heuristic(origin[0], origin[1]), 0.0, origin)]
    segment_ok = {}
    end = None
    while queue:
        _, cost, state = heappop(queue)
        if cost != distances.get(state):
            continue
        ix, iy, direction = state
        if (ix, iy) == destination:
            end = state
            break
        for nx, ny, ndir in ((ix - 1, iy, 1), (ix + 1, iy, 1),
                             (ix, iy - 1, 2), (ix, iy + 1, 2)):
            if not (0 <= nx < len(xs) and 0 <= ny < len(ys)):
                continue
            p, q = (xs[ix], ys[iy]), (xs[nx], ys[ny])
            key = (min(ix, nx), min(iy, ny), ndir)
            if key not in segment_ok:
                segment_ok[key] = not _blocked(p, q, obstacles)
            if not segment_ok[key]:
                continue
            weight = abs(q[0] - p[0]) + abs(q[1] - p[1])
            new_cost = cost + weight + (BEND_PENALTY if direction and direction != ndir else 0)
            candidate = (nx, ny, ndir)
            if new_cost < distances.get(candidate, float('inf')):
                distances[candidate] = new_cost
                previous[candidate] = state
                heappush(queue, (new_cost + heuristic(nx, ny), new_cost, candidate))
    if end is None:
        return None
    points = []
    while True:
        points.append((xs[end[0]], ys[end[1]]))
        if end == origin:
            break
        end = previous[end]
    return list(reversed(points))


def route_points(edge, nodes):
    """Return a detached world-space route, reusing immutable geometry safely."""
    return routing_scene(nodes).route_points(edge)


def _route_points_in_scene(edge, scene, *, query_windows=None,
                           extra_clearance=0.0):
    by_id = scene.nodes
    try:
        source, target = by_id[edge['from']], by_id[edge['to']]
    except KeyError as exc:
        raise RoutingError('Équipement source ou cible introuvable') from exc
    mode = edge.get('routing', 'straight')
    lane = float(edge.get('_lane_offset', 0.0))
    if mode == 'straight':
        return list(lane_endpoints(source, target, lane))
    if mode != 'orthogonal':
        raise RoutingError('Mode de routage inconnu')
    indexed, obstacles, outer, _ = scene.geometry()
    index = scene.routing_obstacle_index()
    # Extra clearance is only a routing preference for intermediate shapes.
    # Never enlarge source/target obstacles: their boundary ports and stubs
    # must stay attached to the actual equipment geometry.
    search_index = index
    if extra_clearance:
        search_index = RectangleIndex(
            (node_id, expanded_intermediate_bounds(
                node_id, rect, source['id'], target['id'], extra_clearance))
            for node_id, rect in index._items)
    dx, dy = target['x'] - source['x'], target['y'] - source['y']
    horizontal = ('right', 'left') if dx >= 0 else ('left', 'right')
    vertical = ('bottom', 'top') if dy >= 0 else ('top', 'bottom')
    reverse_h = (horizontal[1], horizontal[0])
    reverse_v = (vertical[1], vertical[0])
    candidates = (horizontal, vertical, reverse_h, reverse_v)
    best = None
    best_cost = float('inf')
    # A dense grid in one port orientation must not reject another safe port.
    # Preserve an explicit density failure when every candidate is unusable.
    density_limited = False
    for start_side, end_side in candidates:
        start_port, start_stub = _port(source, start_side, lane)
        end_port, end_stub = _port(target, end_side, lane)
        # A narrow spatial query is sufficient for an exact stub collision test.
        start_window = (min(start_port[0], start_stub[0]),
                        min(start_port[1], start_stub[1]),
                        max(start_port[0], start_stub[0]),
                        max(start_port[1], start_stub[1]))
        end_window = (min(end_port[0], end_stub[0]),
                      min(end_port[1], end_stub[1]),
                      max(end_port[0], end_stub[0]),
                      max(end_port[1], end_stub[1]))
        if query_windows is not None:
            query_windows.extend((start_window, end_window))
        others_start = [rect for key, rect in index.query_items(start_window)
                        if key != source['id']]
        others_end = [rect for key, rect in index.query_items(end_window)
                      if key != target['id']]
        if _blocked(start_port, start_stub, others_start) or _blocked(end_port, end_stub, others_end):
            continue
        if query_windows is not None:
            query_windows.extend(((start_stub[0], start_stub[1],
                                   start_stub[0], start_stub[1]),
                                  (end_stub[0], end_stub[1],
                                   end_stub[0], end_stub[1])))
        if any(l < start_stub[0] < r and t < start_stub[1] < b
               for l, t, r, b in index.query((start_stub[0], start_stub[1],
                                             start_stub[0], start_stub[1]))):
            continue
        if any(l < end_stub[0] < r and t < end_stub[1] < b
               for l, t, r, b in index.query((end_stub[0], end_stub[1],
                                             end_stub[0], end_stub[1]))):
            continue
        route = None
        margin = INITIAL_CORRIDOR
        for _ in range(MAX_CORRIDOR_ATTEMPTS):
            window = _corridor(start_stub, end_stub, margin)
            if query_windows is not None:
                query_windows.append(window)
            try:
                route = _local_grid_path(start_stub, end_stub, search_index, window)
            except RoutingDensityError:
                # A larger corridor cannot reduce the number of grid cells.
                # Try a different pair of ports instead of failing globally.
                density_limited = True
                break
            if route is not None:
                break
            if (window[0] <= outer[0] and window[1] <= outer[1]
                    and window[2] >= outer[2] and window[3] >= outer[3]):
                break
            margin *= 2
        if route is None:
            continue
        points = _simplify([start_port, *route, end_port])
        # Recheck against the complete obstacle set, not just corridor samples.
        if any(_blocked(a, b, search_index.query((min(a[0], b[0]), min(a[1], b[1]),
                                                  max(a[0], b[0]), max(a[1], b[1]))))
               for a, b in zip(route, route[1:])):
            raise RoutingError('Trajet orthogonal non sûr')
        distance = sum(abs(b[0] - a[0]) + abs(b[1] - a[1])
                       for a, b in zip(points, points[1:]))
        cost = distance + BEND_PENALTY * max(0, len(points) - 2)
        if cost < best_cost:
            best, best_cost = points, cost
    if best is None:
        if density_limited:
            raise RoutingDensityError('Routage orthogonal trop dense pour la limite de sécurité')
        raise RoutingError('Aucun trajet orthogonal sans collision disponible')
    return best


def set_edge_routing(document, edge_id, mode):
    """Transactional routing change; never commit a mode that cannot be drawn."""
    from .model import validate
    if mode not in ('straight', 'orthogonal'):
        raise ValueError('Mode de routage inconnu')
    updated = deepcopy(validate(document))
    edge = next((item for item in updated['edges'] if item['id'] == edge_id), None)
    if edge is None:
        raise ValueError('Liaison introuvable')
    # Protect the physical SAN path even when this command is invoked outside
    # the Tk editor (which already filters locked links from selection).
    assert_link_editable(updated, edge)
    edge['routing'] = mode
    for display_edge in display_edges(updated['edges'], updated['nodes']):
        if display_edge['id'] == edge_id:
            route_points(display_edge, updated['nodes'])
            break
    return validate(updated)
