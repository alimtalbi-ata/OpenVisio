"""Conservative multi-page external Visio VSDX importer. Author: Abdelhalim Talbi."""
import math
import posixpath
from xml.etree import ElementTree as ET

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
PX_PER_IN = 96.0

def _parse_xml(archive, name):
    payload = archive.read(name)
    upper = payload.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("XML VSDX avec entités externes interdit")
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("XML VSDX invalide : " + name) from exc

def _part_target(target):
    if not target or "\\" in target or "?" in target or "#" in target:
        raise ValueError("Relation de page VSDX non sûre")
    if target.startswith("/"):
        path = posixpath.normpath(target.lstrip("/"))
    else:
        path = posixpath.normpath(posixpath.join("visio/pages", target))
    if not path.startswith("visio/pages/") or "/../" in "/" + path + "/":
        raise ValueError("Relation de page VSDX non sûre")
    return path

def _pages(archive):
    names = set(archive.namelist())
    pages_xml = "visio/pages/pages.xml"
    rels_xml = "visio/pages/_rels/pages.xml.rels"
    if pages_xml not in names:
        if "visio/pages/page1.xml" not in names:
            raise ValueError("Page Visio absente")
        return [("Page 1", "visio/pages/page1.xml", None)]
    pages = _parse_xml(archive, pages_xml)
    relations = {}
    if rels_xml in names:
        relroot = _parse_xml(archive, rels_xml)
        for rel in relroot.findall(f"{{{R}}}Relationship"):
            if rel.get("TargetMode", "Internal").lower() == "external":
                continue
            if rel.get("Id"):
                relations[rel.get("Id")] = _part_target(rel.get("Target"))
    result = []
    for i, page in enumerate(pages.findall(f"{{{V}}}Page"), 1):
        rel = page.find(f"{{{V}}}Rel")
        rid = rel.get(f"{{{OR}}}id") if rel is not None else None
        part = relations.get(rid)
        if part is None and not relations:
            part = f"visio/pages/page{i}.xml"
        if not part or part not in names:
            raise ValueError("Relation de page VSDX absente ou invalide")
        height = None
        for cell in page.findall(f"./{{{V}}}PageSheet/{{{V}}}Cell"):
            if cell.get("N") == "PageHeight":
                try:
                    value = float(cell.get("V", ""))
                    if math.isfinite(value) and 0 < value <= 100000:
                        height = value * PX_PER_IN
                except ValueError:
                    pass
        result.append((page.get("Name") or page.get("NameU") or f"Page {i}", part, height))
    if not result or len(result) > 128:
        raise ValueError("Nombre de pages VSDX invalide")
    return result

def _kind(name):
    n = name.lower()
    if "storage" in n or "array" in n or "disk" in n:
        return "storage"
    if "nas" in n or "fileserver" in n:
        return "nas"
    if "firewall" in n:
        return "firewall"
    if "switch" in n or "router" in n:
        return "network-switch"
    if "database" in n or "sql" in n:
        return "database"
    if "application" in n:
        return "application"
    return "server"

def import_external_pages(archive):
    """Return validated OpenVisio diagram; pages become separate visible layers."""
    from .model import validate
    pages = _pages(archive)
    nodes, edges, layers = [], [], []
    offset = 0.0
    for index, (page_name, part, declared_height) in enumerate(pages, 1):
        page = _parse_xml(archive, part)
        layer_id = f"vsdx-page-{index}"
        layers.append({"id": layer_id, "name": page_name[:256], "visible": True})
        candidates = []
        by_sheet = {}
        for shape in page.findall(f".//{{{V}}}Shapes/{{{V}}}Shape"):
            sid = shape.get("ID")
            if not sid or sid in by_sheet:
                continue
            cells = {c.get("N"): c.get("V") for c in shape.findall(f"./{{{V}}}Cell")}
            if cells.get("OneD") == "1" or not all(k in cells for k in ("PinX", "PinY")):
                continue
            try:
                x, pin_y = float(cells["PinX"]) * PX_PER_IN, float(cells["PinY"]) * PX_PER_IN
            except (ValueError, OverflowError, TypeError):
                continue
            if not (math.isfinite(x) and math.isfinite(pin_y)):
                continue
            ident = f"visio-p{index}-s{sid}"
            name = shape.get("NameU") or shape.get("Name") or ident
            text = shape.find(f"./{{{V}}}Text")
            label = "".join(text.itertext()).strip() if text is not None else ""
            candidates.append((ident, sid, x, pin_y, (label or name)[:4096], _kind(name)))
            by_sheet[sid] = ident
        inferred_height = max((candidate[3] for candidate in candidates), default=0) + 96
        height = declared_height if declared_height is not None else max(600, inferred_height)
        for ident, sid, x, pin_y, label, kind in candidates:
            nodes.append({"id": ident, "x": round(x, 3),
                          "y": round(offset + height - pin_y, 3),
                          "label": label, "shape": kind, "layer": layer_id})
        connections = {}
        for link in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect"):
            source, target = link.get("FromSheet"), link.get("ToSheet")
            if source and target in by_sheet and link.get("FromCell") in ("BeginX", "EndX"):
                connections.setdefault(source, {})[link.get("FromCell")] = by_sheet[target]
        for sid, ends in connections.items():
            a, b = ends.get("BeginX"), ends.get("EndX")
            if a and b and a != b:
                edges.append({"id": f"visio-p{index}-link-{sid}",
                              "from": a, "to": b, "layer": layer_id})
        offset += max(height, 600) + 96
    return validate({"nodes": nodes, "edges": edges, "layers": layers,
                     "metadata": {"import_format": "VSDX", "page_count": len(pages),
                                  "import_mode": "flattened-pages",
                                  "omitted_parallel_links": 0,
                                  "import_warning": "",
                                  "limitations": ["masters", "groups", "rotation", "styles", "formulas"]}})
