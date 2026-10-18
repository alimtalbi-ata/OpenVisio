"""Native Python SVG export with adaptive viewBox. Author: Abdelhalim Talbi."""
from pathlib import Path
from xml.sax.saxutils import escape
from .model import validate
from .shapes import get_shape

def to_svg(data, width=None, height=None, margin=80):
    data = validate(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    if nodes:
        min_x = min(n["x"] - 70 for n in nodes.values()) - margin
        max_x = max(n["x"] + 70 for n in nodes.values()) + margin
        min_y = min(n["y"] - 30 for n in nodes.values()) - margin
        max_y = max(n["y"] + 30 for n in nodes.values()) + margin
    else:
        min_x, min_y, max_x, max_y = 0, 0, 800, 600
    natural_width, natural_height = max_x - min_x, max_y - min_y
    width = natural_width if width is None else width
    height = natural_height if height is None else height
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)) or width <= 0 or height <= 0:
        raise ValueError("Dimensions SVG invalides")
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {natural_width} {natural_height}">', f'<rect x="{min_x}" y="{min_y}" width="{natural_width}" height="{natural_height}" fill="#f8fafc"/>']
    for edge in data["edges"]:
        a, b = nodes[edge["from"]], nodes[edge["to"]]
        lines.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}" stroke="#2563eb" stroke-width="2"/>')
    for node in data["nodes"]:
        x, y = node["x"], node["y"]
        label = escape(str(node.get("label", "Équipement")))
        fill = get_shape(node.get("shape", "server"))["fill"]
        lines.extend([f'<rect x="{x-70}" y="{y-30}" width="140" height="60" rx="8" fill="{fill}" stroke="#1d4ed8"/>', f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="13" fill="#172554">{label}</text>'])
    lines.append("</svg>")
    return "\n".join(lines)

def export_svg(path, data):
    Path(path).write_text(to_svg(data), encoding="utf-8")
