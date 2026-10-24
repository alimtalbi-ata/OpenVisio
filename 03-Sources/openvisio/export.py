"""Native Python SVG export with adaptive viewBox. Author: Abdelhalim Talbi."""
from pathlib import Path
from math import isfinite
from xml.sax.saxutils import escape
from .model import validate
from .render import edge_routes, clip_route_to_nodes
from .symbols import draw_symbol

class _SVGCanvas:
    """Tk canvas adapter: SVG uses exactly the editor's symbol geometry."""
    def __init__(self):
        self.elements = []

    def _style(self, style):
        from xml.sax.saxutils import quoteattr
        fields = []
        for key, attribute in (("fill", "fill"), ("outline", "stroke"), ("width", "stroke-width")):
            if key in style:
                fields.append(f'{attribute}={quoteattr(str(style[key] or "none"))}')
        return " ".join(fields)

    def create_rectangle(self, x1, y1, x2, y2, **style):
        self.elements.append(f'<rect x="{min(x1,x2):g}" y="{min(y1,y2):g}" width="{abs(x2-x1):g}" height="{abs(y2-y1):g}" {self._style(style)}/>')

    def create_oval(self, x1, y1, x2, y2, **style):
        self.elements.append(f'<ellipse cx="{(x1+x2)/2:g}" cy="{(y1+y2)/2:g}" rx="{abs(x2-x1)/2:g}" ry="{abs(y2-y1)/2:g}" {self._style(style)}/>')

    def create_line(self, *coords, **style):
        points = " ".join(f"{coords[i]:g},{coords[i+1]:g}" for i in range(0,len(coords),2))
        self.elements.append(f'<polyline points="{points}" {self._style({**style, "fill": "none"})}/>')

def to_svg(data, width=None, height=None, margin=80):
    data = validate(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    if nodes:
        min_x = min(n["x"] - 70 for n in nodes.values()) - margin
        max_x = max(n["x"] + 70 for n in nodes.values()) + margin
        min_y = min(n["y"] - 30 for n in nodes.values()) - margin
        max_y = max(n["y"] + 43 for n in nodes.values()) + margin
    else:
        min_x, min_y, max_x, max_y = 0, 0, 800, 600
    natural_width, natural_height = max_x - min_x, max_y - min_y
    width = natural_width if width is None else width
    height = natural_height if height is None else height
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)) or not isfinite(width) or not isfinite(height) or width <= 0 or height <= 0:
        raise ValueError("Dimensions SVG invalides")
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {natural_width} {natural_height}">', f'<rect x="{min_x}" y="{min_y}" width="{natural_width}" height="{natural_height}" fill="#f8fafc"/>']
    lines.append('<defs><marker id="ov-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#2563eb"/></marker></defs>')
    routes = edge_routes(data["nodes"], data["edges"])
    for edge in data["edges"]:
        route = routes.get(edge["id"])
        if route is None:
            continue
        a, b = nodes[edge["from"]], nodes[edge["to"]]
        (ax, ay), (bx, by) = clip_route_to_nodes(route, a, b)
        lines.append(f'<line x1="{ax:g}" y1="{ay:g}" x2="{bx:g}" y2="{by:g}" stroke="#2563eb" stroke-width="2" marker-end="url(#ov-arrow)"/>')
        details = []
        protocol = str(edge.get("protocol", "")).strip()
        if protocol:
            details.append(protocol)
        speed = str(edge.get("speed_gbps", "")).strip()
        if speed:
            details.append(speed + " Gbit/s")
        fabric = str(edge.get("fabric", "")).strip()
        if fabric:
            details.append("Fabric " + fabric)
        ports = " → ".join(str(edge.get(key, "")).strip() for key in ("source_port", "target_port") if str(edge.get(key, "")).strip())
        if ports:
            details.append(ports)
        if details:
            label = escape(" · ".join(details)[:72])
            lines.append(f'<text x="{(ax+bx)/2:g}" y="{(ay+by)/2-9:g}" text-anchor="middle" font-family="Arial" font-size="9" fill="#334155">{label}</text>')
    canvas = _SVGCanvas()
    for node in data["nodes"]:
        x, y = node["x"], node["y"]
        label = escape(str(node.get("label", "Équipement"))[:40])
        draw_symbol(canvas, node.get("shape", "server"), x, y, lambda xx, yy: (xx, yy))
        lines.append(f'<text x="{x}" y="{y+43}" text-anchor="middle" font-family="Arial" font-size="10" fill="#172554">{label}</text>')
    lines.extend(canvas.elements)
    lines.append("</svg>")
    return "\n".join(lines)

def export_svg(path, data):
    Path(path).write_text(to_svg(data), encoding="utf-8")
