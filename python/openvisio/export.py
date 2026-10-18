"""Native Python SVG export. Author: Abdelhalim Talbi."""
from pathlib import Path
from xml.sax.saxutils import escape
from .model import validate

def to_svg(data, width=1600, height=1000):
    data = validate(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#f8fafc"/>']
    for edge in data["edges"]:
        a, b = nodes[edge["from"]], nodes[edge["to"]]
        lines.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}" stroke="#2563eb" stroke-width="2"/>')
    for node in data["nodes"]:
        x, y = node["x"], node["y"]
        label = escape(str(node.get("label", "Équipement")))
        lines.extend([f'<rect x="{x-70}" y="{y-30}" width="140" height="60" rx="8" fill="white" stroke="#1d4ed8"/>', f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="13" fill="#172554">{label}</text>'])
    lines.append("</svg>")
    return "\n".join(lines)

def export_svg(path, data):
    Path(path).write_text(to_svg(data), encoding="utf-8")
