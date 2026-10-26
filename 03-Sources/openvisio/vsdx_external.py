"""Conservative, multi-page import of external Visio VSDX page geometry.

This is a flattening importer, not a Visio fidelity certification. Every Visio
page is mapped to a named OpenVisio layer and vertically offset to avoid overlap.
Masters, exact rotations and style formulas are not
recreated; numeric nested group transforms are flattened to bounding boxes. Author: Abdelhalim Talbi.
"""
import math
import posixpath
import re
from xml.etree import ElementTree as ET
from xml.parsers import expat
from .vsdx_geometry import (shape_center_inches, shape_axis_aligned_dimensions_inches,
                            nested_shape_geometry_inches)
from .visio_formula import evaluate_geometry_formula_cells, GEOMETRY_CELL_NAMES

# ShapeSheet geometry cells are resolved case-insensitively by the bounded
# formula evaluator. Normalize their XML cell names at the importer boundary as
# well, so a spelling alias cannot bypass formula detection or omit the shape.
_GEOMETRY_CELL_CANONICAL = {name.casefold(): name for name in GEOMETRY_CELL_NAMES}

def _canonical_geometry_cell_name(name):
    return _GEOMETRY_CELL_CANONICAL.get(name.casefold(), name)

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
PX_PER_IN = 96.0


def _parse_xml(archive, name, *, expected_root=None):
    payload = archive.read(name)
    # A raw-byte <!DOCTYPE check is insufficient: UTF-16 Visio XML can
    # encode every ASCII character with a NUL byte. ElementTree would then
    # expand internal entities before the importer validates the page.
    # Expat recognizes the XML declaration/encoding and rejects any DTD at
    # the parser level, independently of UTF-8/UTF-16 byte representation.
    # Run the preflight before constructing an ElementTree from untrusted XML.
    parser = expat.ParserCreate()

    def reject_dtd(*_args):
        raise ValueError("XML VSDX avec entités externes interdit")

    parser.StartDoctypeDeclHandler = reject_dtd
    parser.EntityDeclHandler = reject_dtd
    parser.ExternalEntityRefHandler = reject_dtd
    try:
        parser.Parse(payload, True)
        root = ET.fromstring(payload)
        if expected_root is not None and root.tag != expected_root:
            raise ValueError("racine XML VSDX invalide : " + name)
        return root
    except (expat.ExpatError, ET.ParseError) as exc:
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
        return [("Page 1", "visio/pages/page1.xml", None, {})]
    pages = _parse_xml(archive, pages_xml, expected_root=f"{{{V}}}Pages")
    relations = {}
    if rels_xml in names:
        relroot = _parse_xml(archive, rels_xml, expected_root=f"{{{R}}}Relationships")
        seen_relation_ids = set()
        for rel in relroot.findall(f"{{{R}}}Relationship"):
            rid = rel.get("Id")
            # OPC relationship IDs are unique within a .rels part. Silently
            # overwriting one changes which Visio page a layer imports.
            if rid:
                if rid in seen_relation_ids:
                    raise ValueError("Identifiant de relation VSDX dupliqué : " + rid)
                seen_relation_ids.add(rid)
            if rel.get("TargetMode", "Internal").lower() == "external":
                continue
            if rid:
                relations[rid] = _part_target(rel.get("Target"))
    result = []
    seen_page_ids = set()
    seen_page_parts = set()
    for i, page in enumerate(pages.findall(f"{{{V}}}Page"), 1):
        page_id = page.get("ID")
        if page_id:
            if page_id in seen_page_ids:
                raise ValueError("Identifiant de page VSDX dupliqué : " + page_id)
            seen_page_ids.add(page_id)
        rel = page.find(f"{{{V}}}Rel")
        rid = rel.get(f"{{{OR}}}id") if rel is not None else None
        part = relations.get(rid)
        # Legacy sequential fallback is valid only when the page does not
        # declare an OPC relationship. A missing/empty/external .rels entry
        # must never silently redirect a named page to page{i}.xml.
        if part is None and not relations and rel is None:
            part = f"visio/pages/page{i}.xml"
        if not part or part not in names:
            raise ValueError("Relation de page VSDX absente ou invalide")
        # Distinct logical pages must not alias one XML part: duplicate imports
        # would fabricate SAN equipment and FC connections.
        if part in seen_page_parts:
            raise ValueError("Partie de page VSDX réutilisée par plusieurs pages : " + part)
        seen_page_parts.add(part)
        page_values = {}
        for cell in page.findall(f"./{{{V}}}PageSheet/{{{V}}}Cell"):
            name = cell.get("N")
            if name not in {"PageWidth", "PageHeight"} or cell.get("F") is not None:
                continue
            try:
                value = float(cell.get("V", ""))
                if math.isfinite(value) and 0 < value <= 100000:
                    page_values[name] = value
            except (TypeError, ValueError, OverflowError):
                pass
        height = page_values.get("PageHeight")
        height = height * PX_PER_IN if height is not None else None
        result.append((page.get("Name") or page.get("NameU") or f"Page {i}", part, height, page_values))
    if not result or len(result) > 128:
        raise ValueError("Nombre de pages VSDX invalide")
    return result


def _kind(name):
    # Recognize our exported infrastructure catalogue without relying on the
    # private OpenVisio JSON payload. Preserve SAN vs network switch types.
    if name.startswith("OpenVisio "):
        from .shapes import SHAPES
        kind = name[len("OpenVisio "):]
        if kind in SHAPES:
            return kind
    n = name.lower()
    # External vendor stencils frequently use product IDs without the words
    # "SAN", "FC" or "switch". Keep a narrow, model-number-based allowlist:
    # a bare vendor name or an unrelated management/server label is not enough.
    # These are shape identity hints, not evidence of hardware connectivity.
    if any(re.search(pattern, n) for pattern in (
            r"\b(?:cisco[\s_-]+)?mds[\s_-]*\d{4}[a-z]?\b",
            r"\bbrocade[\s_-]+(?:g\d{3,4}|dcx(?:[\s_-]*\d{4})?)\b",
            r"\bconnectrix[\s_-]+ds[\s_-]*\d{4}[a-z]?\b",
            r"\bhpe[\s_-]+sn\d{4}[a-z]?\b",
            r"\bibm[\s_-]+san\d{3,4}[a-z]?(?:-\d+)?\b",
    )):
        return "san-switch"
    # External Visio NameU values are not OpenVisio catalogue IDs. Preserve
    # explicitly named FC/SAN fabric equipment instead of treating every
    # occurrence of "switch" as a LAN switch. Require adjacent SAN tokens so
    # location names such as "San Francisco Switch" are not misclassified.
    if (re.search(r"\b(?:san[\s_-]*(?:switch|fabric|director)|"
                  r"(?:switch|fabric|director)[\s_-]*san)\b", n)
            or re.search(r"\bfc[\s_-]*(?:switch|fabric|director)\b", n)
            or (re.search(r"\b(?:fibre|fiber)[\s_-]+channel\b", n)
                and re.search(r"\b(?:switch|fabric|director)\b", n))):
        return "san-switch"
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


def _master_shape_kinds(archive):
    """Resolve external Visio stencil identities from the public master index.

    Generic Shape NameU values such as Sheet.42 carry no equipment identity.
    The Visio Master attribute points to a named stencil in masters.xml;
    captions are deliberately excluded from classification. This is a
    conservative name-based mapping, not master geometry/style fidelity.
    """
    part = "visio/masters/masters.xml"
    if part not in archive.namelist():
        return {}
    root = _parse_xml(archive, part, expected_root=f"{{{V}}}Masters")
    kinds = {}
    for master in root.findall(f"{{{V}}}Master"):
        ident = master.get("ID")
        if not ident:
            continue
        if ident in kinds:
            raise ValueError("Identifiant Master VSDX dupliqué : " + ident)
        # Stable NameU is preferred, but a generic stencil NameU may coexist
        # with a descriptive display Name (e.g. Brocade G720).
        hints = (master.get("NameU") or "", master.get("Name") or "")
        # OpenVisio's explicit public type remains authoritative. In external
        # vendor stencils, a generic NameU="Network Switch" may coexist with
        # a specific display Name="Brocade G720". The latter is more precise
        # than the generic network class and must not be discarded.
        explicit = next((hint for hint in hints if hint.startswith("OpenVisio ")), None)
        if explicit is not None:
            kinds[ident] = _kind(explicit)
        else:
            classifications = [_kind(hint) for hint in hints]
            kinds[ident] = ("san-switch" if "san-switch" in classifications
                            else next((kind for kind in classifications
                                       if kind != "server"), "server"))
    return kinds


def _connector_endpoint_cell(cell):
    """Normalize Visio's X/Y glue cells to one physical connector end.

    Visio Connects rows may glue BeginY/EndY rather than BeginX/EndX,
    or glue both axes of the same end. Never treat the two axes as two
    independent FC links, and reject conflicting endpoint destinations.
    """
    if cell in ("BeginX", "BeginY"):
        return "BeginX"
    if cell in ("EndX", "EndY"):
        return "EndX"
    return None



def _public_orthogonal_connector_points(shape):
    """Extract verifiable static waypoints from OpenVisio's public VSDX form.

    The returned tuples are page-space inches. Arbitrary Visio formulas,
    unsupported local coordinate frames and non-orthogonal segments are not
    evaluated or guessed. Callers must still bind the route to its endpoint
    geometry and revalidate it against current obstacles before displaying it.
    """
    endpoint_cells = shape.findall(f"./{{{V}}}Cell")
    if any(cell.get("F") is not None for cell in endpoint_cells
           if cell.get("N") in ("BeginX", "BeginY", "EndX", "EndY")):
        return None  # Evaluating Visio formulas is outside this importer.
    cells = {cell.get("N"): cell.get("V") for cell in endpoint_cells}
    try:
        bx, by, ex, ey = (float(cells[key]) for key in
                          ("BeginX", "BeginY", "EndX", "EndY"))
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if not all(math.isfinite(v) and abs(v) <= 100000 for v in (bx, by, ex, ey)):
        return None
    dx, dy = ex - bx, ey - by
    length = math.hypot(dx, dy)
    if length <= 1e-8:
        return None
    ux, uy = dx / length, dy / length
    for section in shape.findall(f"./{{{V}}}Section"):
        if section.get("N") != "Geometry":
            continue
        rows = section.findall(f"./{{{V}}}Row")
        if not 3 <= len(rows) <= 2048:
            continue
        if rows[0].get("T") != "MoveTo" or any(
                row.get("T") != "LineTo" for row in rows[1:]):
            continue
        local = []
        try:
            for row in rows:
                row_cells = row.findall(f"./{{{V}}}Cell")
                if any(cell.get("F") is not None for cell in row_cells):
                    raise ValueError("formula-driven connector geometry")
                coords = {cell.get("N"): cell.get("V") for cell in row_cells}
                x, y = float(coords["X"]), float(coords["Y"])
                if not math.isfinite(x) or not math.isfinite(y) or abs(x) > 100000 or abs(y) > 100000:
                    raise ValueError("out-of-range connector geometry")
                local.append((x, y))
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        # This explicit local frame is emitted by OpenVisio's public VSDX
        # writer. Do not assume arbitrary Visio formulas or rotated frames.
        tolerance = 0.001  # inches, less than one tenth of a display pixel
        if (math.hypot(*local[0]) > tolerance or
                math.hypot(local[-1][0] - length, local[-1][1]) > tolerance):
            continue
        points = [(bx + x * ux - y * uy, by + x * uy + y * ux)
                  for x, y in local]
        valid = True
        orientations = set()
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            sx, sy = abs(x2 - x1), abs(y2 - y1)
            if max(sx, sy) <= tolerance:
                valid = False
                break
            if sx > tolerance and sy > tolerance:
                valid = False
                break
            orientations.add("horizontal" if sy <= tolerance else "vertical")
        if valid and len(orientations) == 2:
            return points
    return None


def _public_orthogonal_connector(shape):
    """Compatibility predicate for the verifiable static-route subset."""
    return _public_orthogonal_connector_points(shape) is not None


def import_external_pages(archive):
    """Return validated OpenVisio diagram; pages become separate visible layers."""
    from .model import validate

    pages = _pages(archive)
    master_kinds = _master_shape_kinds(archive)
    nodes, edges, layers = [], [], []
    offset = 0.0
    rotated_count = 0
    # Only a bounded ShapeSheet scalar subset is evaluated; other formulas
    # retain cached values and are reported as a fidelity loss.
    formula_geometry_shapes = 0
    formula_geometry_examples = []
    formula_geometry_evaluated_shapes = 0
    formula_geometry_cells_evaluated = 0
    formula_geometry_unresolved_shapes = 0
    formula_geometry_unresolved_examples = []
    orthogonal_routes_preserved = 0
    orthogonal_routes_approximated = 0
    # External Visio pages may contain one-ended or unsupported connectors.
    # Never silently report a complete topology when those links are omitted.
    skipped_connectors = {"incomplete": 0, "self_loop": 0, "unresolved": 0}
    skipped_connector_examples = []
    grouped_children_omitted = 0
    grouped_children_imported = 0
    page_extent_expanded = 0
    page_bottom_overflow_total = 0.0
    MAX_GROUP_DEPTH = 16
    for index, (page_name, part, declared_height, page_values) in enumerate(pages, 1):
        page = _parse_xml(archive, part, expected_root=f"{{{V}}}PageContents")
        layer_id = f"vsdx-page-{index}"
        layers.append({"id": layer_id, "name": page_name[:256], "visible": True})
        candidates = []
        by_sheet = {}
        # Walk nested groups with explicit local-to-page transforms. Keep
        # parent containers as nodes for compatibility with V42.26; children
        # are flattened with their original page-global sheet identifiers.
        # A malformed parent must never cause a guessed child position.
        def descendants_count(shape):
            return len(shape.findall(f".//{{{V}}}Shapes/{{{V}}}Shape"))

        def visit(shape, ancestors=(), parent_id=None, depth=0):
            nonlocal rotated_count, grouped_children_omitted, grouped_children_imported
            nonlocal formula_geometry_shapes, formula_geometry_evaluated_shapes
            nonlocal formula_geometry_cells_evaluated, formula_geometry_unresolved_shapes
            children = shape.findall(f"./{{{V}}}Shapes/{{{V}}}Shape")
            sid = shape.get("ID")
            shape_cells = shape.findall(f"./{{{V}}}Cell")
            # Direct ShapeSheet cells are unique. Building a dict without first
            # checking the XML silently made the last duplicate win, allowing a
            # malformed VSDX to alter geometry based on source order.
            cells = {}
            seen_cell_names = {}
            for cell in shape_cells:
                cell_name = cell.get("N")
                if not cell_name:
                    continue
                folded_name = cell_name.casefold()
                if folded_name in seen_cell_names:
                    previous = seen_cell_names[folded_name]
                    raise ValueError(
                        "Duplicate ShapeSheet cell name (case-insensitive): "
                        f"{previous!r} / {cell_name!r} on sheet {sid or '<unnamed>'}"
                    )
                seen_cell_names[folded_name] = cell_name
                # Keep original spelling for ambiguity diagnostics but use
                # canonical names for the seven supported geometry cells. The
                # downstream geometry reader uses canonical ShapeSheet keys;
                # without this normalization a valid pinx cell was skipped
                # before its formula could be evaluated.
                cells[_canonical_geometry_cell_name(cell_name)] = cell.get("V")
            if depth > MAX_GROUP_DEPTH:
                grouped_children_omitted += 1 + descendants_count(shape)
                return
            if not sid or sid in by_sheet or cells.get("OneD") == "1" or not all(
                    key in cells for key in ("PinX", "PinY")):
                grouped_children_omitted += descendants_count(shape) + (1 if parent_id is not None else 0)
                return
            shape_formulas = {
                _canonical_geometry_cell_name(cell.get("N")): cell.get("F")
                for cell in shape_cells
                if cell.get("N") and cell.get("F") is not None
            }
            formula_cells = sorted(name for name in shape_formulas if name in GEOMETRY_CELL_NAMES)
            if formula_cells:
                formula_geometry_shapes += 1
                example = f"page {index} / sheet {sid}: {', '.join(formula_cells)}"
                if len(formula_geometry_examples) < 12:
                    formula_geometry_examples.append(example)
                evaluated, unresolved = evaluate_geometry_formula_cells(cells, shape_formulas, page_values)
                if unresolved:
                    formula_geometry_unresolved_shapes += 1
                    if len(formula_geometry_unresolved_examples) < 12:
                        formula_geometry_unresolved_examples.append(
                            example + " (unresolved: " + ", ".join(unresolved) + ")")
                else:
                    candidate_cells = dict(cells)
                    candidate_cells.update({name: format(value, ".17g") for name, value in evaluated.items()})
                    try:
                        # A syntactically valid result can still be an unusable
                        # ShapeSheet geometry (for example Width=0). Validate
                        # before replacing the cached values so bad formulas do
                        # not silently drop a shape during the normal geometry pass.
                        nested_shape_geometry_inches(candidate_cells, ancestors)
                    except (ValueError, TypeError, OverflowError):
                        formula_geometry_unresolved_shapes += 1
                        if len(formula_geometry_unresolved_examples) < 12:
                            formula_geometry_unresolved_examples.append(
                                example + " (invalid evaluated geometry)")
                    else:
                        cells = candidate_cells
                        formula_geometry_evaluated_shapes += 1
                        formula_geometry_cells_evaluated += len(evaluated)
            try:
                x_in, y_in, width_in, height_in, total_angle = nested_shape_geometry_inches(
                    cells, ancestors)
            except ValueError:
                grouped_children_omitted += descendants_count(shape) + (1 if parent_id is not None else 0)
                return
            if not math.isclose(math.remainder(total_angle, math.tau), 0.0, abs_tol=1e-10):
                rotated_count += 1
            ident = f"visio-p{index}-s{sid}"
            name_u = shape.get("NameU") or ""
            display_name = shape.get("Name") or ""
            name = name_u or display_name or ident
            # OpenVisio keeps the stable NameU="OpenVisio node" for older
            # consumers, while the public Name encodes the infrastructure kind.
            if name == "OpenVisio node" and display_name.startswith("OpenVisio "):
                name = display_name
            # Visio stencils can retain a generic NameU (e.g. Sheet.42) while
            # the visible Name identifies the physical FC switch. Consider
            # both names, but never infer hardware identity from arbitrary
            # user-entered caption text or overwrite a specific NameU kind.
            kind = _kind(name)
            if kind == "server" and display_name and display_name != name:
                visible_kind = _kind(display_name)
                if visible_kind != "server":
                    kind = visible_kind
            master_kind = master_kinds.get(shape.get("Master"))
            # A named public OpenVisio kind wins over any stale Master value.
            # Only generic/unknown sheet identities may inherit the stencil
            # identity; never reclassify an explicit LAN switch as FC/SAN.
            explicit_kind = any(value.startswith("OpenVisio ") for value in
                                (name_u, display_name))
            # A generic Sheet.N or Switch.N stencil identity plus a generic
            # display caption "Switch" does not prove LAN connectivity. A
            # precise FC/SAN Master is authoritative in this narrow case.
            def weak_switch_hint(value):
                return bool(re.fullmatch(r"(?:Sheet\.\d+|Switch(?:\.\d+)?|Generic Switch)",
                                         value.strip(), flags=re.IGNORECASE))

            generic_switch = (weak_switch_hint(name_u or name)
                              and (not display_name or weak_switch_hint(display_name)))
            if (not explicit_kind and master_kind and master_kind != "server"
                    and (kind == "server" or (generic_switch and kind == "network-switch"))):
                kind = master_kind
            text_element = shape.find(f"./{{{V}}}Text")
            label = "".join(text_element.itertext()).strip() if text_element is not None else ""
            # A synthetic Sheet.N identifier is not a useful visible label.
            fallback_label = (display_name if display_name and re.fullmatch(
                r"Sheet\.\d+", name, flags=re.IGNORECASE) else name)
            candidates.append((ident, sid, x_in * PX_PER_IN, y_in * PX_PER_IN,
                               (label or fallback_label)[:4096],
                               "visio-group" if children or shape.get("Type") == "Group" else kind,
                               width_in * PX_PER_IN, height_in * PX_PER_IN, parent_id))
            by_sheet[sid] = ident
            if parent_id is not None:
                grouped_children_imported += 1
            if children:
                # Child geometry cannot be placed without the parent group's
                # explicit Width/Height and valid local pivot/rotation.
                try:
                    from .vsdx_geometry import group_local_to_parent_inches
                    group_local_to_parent_inches(cells, 0.0, 0.0)
                except ValueError:
                    grouped_children_omitted += descendants_count(shape)
                    return
                for child in children:
                    visit(child, ancestors + (cells,), ident, depth + 1)

        for shape in page.findall(f"./{{{V}}}Shapes/{{{V}}}Shape"):
            visit(shape)
        top_extent = max((candidate[3] + candidate[7] / 2
                          for candidate in candidates), default=0)
        bottom_extent = min((candidate[3] - candidate[7] / 2
                             for candidate in candidates), default=0)
        # Visio Y increases upwards. Shapes below the page's zero line map
        # below the OpenVisio display band, so the NEXT page needs additional
        # clearance; growing only the current band's height cannot fix this.
        bottom_overflow = max(0.0, -bottom_extent)
        page_bottom_overflow_total += bottom_overflow
        inferred_height = top_extent + 96
        # Preserve coordinates on valid pages. Expand the band above the
        # page only for actual top overflow; reserve bottom overflow in the
        # following page offset without shifting the current page's shapes.
        if declared_height is not None and top_extent <= declared_height:
            height = max(600.0, declared_height)
        else:
            height = max(600.0, inferred_height, declared_height or 0.0)
        if (declared_height is not None and top_extent > declared_height) or bottom_overflow:
            page_extent_expanded += 1
        for ident, sid, x, pin_y, label, kind, width, shape_height, parent_id in candidates:
            node = {"id": ident, "x": round(x, 3),
                    "y": round(offset + height - pin_y, 3),
                    "width": round(width, 3), "height": round(shape_height, 3),
                    "label": label, "shape": kind, "layer": layer_id}
            if parent_id is not None:
                node["visio_group_parent"] = parent_id
            nodes.append(node)
        # Visio connectors are separate Shape elements. Their public Text
        # must survive a source-free import, including formatted Text runs.
        # The label is a caption, not evidence of physical FC port metadata.
        connector_captions = {}
        # Visio connectors can be nested inside group Shapes. The Connects
        # relationship table still references their page-global sheet IDs;
        # searching only top-level shapes silently loses their SAN captions.
        for connector in page.findall(f".//{{{V}}}Shape"):
            sid = connector.get("ID")
            text_element = connector.find(f"./{{{V}}}Text")
            if sid and text_element is not None:
                caption = "".join(text_element.itertext()).strip()
                if caption:
                    connector_captions[sid] = caption[:4096]
        # Only an existing connector sheet may originate a SAN link. A
        # malformed Connects table can otherwise fabricate an edge from a
        # device sheet or an ID that does not exist in the page at all.
        # Nested group connectors are included in this inventory.
        page_shapes = page.findall(f".//{{{V}}}Shape")
        page_sheet_ids = {shape.get("ID") for shape in page_shapes if shape.get("ID")}
        # A duplicate equipment sheet ID referenced by a connector is not a
        # harmless decorative duplicate: the first shape wins in by_sheet,
        # silently rewiring the SAN edge to an arbitrary physical endpoint.
        # Keep compatibility with unused duplicate decorative shapes, but
        # refuse any ambiguous endpoint actually used by the topology.
        referenced_endpoints = {
            row.get("ToSheet")
            for row in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect")
            if _connector_endpoint_cell(row.get("FromCell")) and row.get("ToSheet")
        }
        seen_endpoints = set()
        for shape in page_shapes:
            sid = shape.get("ID")
            if sid in referenced_endpoints:
                if sid in seen_endpoints:
                    raise ValueError("Identifiant d'équipement VSDX dupliqué : " + sid)
                seen_endpoints.add(sid)
        # Visio Connects references a sheet ID, not an individual XML element.
        # If two connector shapes share that ID, their captions and physical
        # SAN links collapse into one ambiguous edge. Reject only duplicate
        # IDs used as connector sources; legacy duplicate non-connector group
        # children are still handled by the existing omission policy.
        connector_sources = {
            row.get("FromSheet")
            for row in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect")
            if _connector_endpoint_cell(row.get("FromCell")) and row.get("FromSheet")
        }
        # Validate every referenced connector source, even when its target
        # is a grouped/unsupported shape that cannot become an OpenVisio node.
        for sid in connector_sources:
            if sid not in page_sheet_ids or sid in by_sheet:
                raise ValueError(
                    "Connexion VSDX invalide : feuille de connecteur absente "
                    f"ou équipement utilisé comme connecteur ({sid})")
        seen_connector_sources = set()
        for shape in page_shapes:
            sid = shape.get("ID")
            if sid in connector_sources:
                if sid in seen_connector_sources:
                    raise ValueError("Identifiant de connecteur VSDX dupliqué : " + sid)
                seen_connector_sources.add(sid)
        # Preserve only public, static, formula-free route geometry. The
        # active route record is endpoint-bound and the routing engine rejects
        # it after node edits or if a new obstacle intersects a segment.
        connector_route_points = {
            shape.get("ID"): route
            for shape in page_shapes
            if shape.get("ID") in connector_sources
            for route in [_public_orthogonal_connector_points(shape)]
            if route is not None
        }
        connections = {}
        for link in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect"):
            source, target = link.get("FromSheet"), link.get("ToSheet")
            end = _connector_endpoint_cell(link.get("FromCell"))
            if end is not None and source in connector_sources and target not in page_sheet_ids:
                # Do not silently drop a SAN fabric endpoint pointing at a
                # nonexistent Visio sheet. Existing but unsupported grouped
                # children still follow the conservative omission policy.
                raise ValueError(
                    "Connexion VSDX invalide : extrémité SAN absente "
                    f"({source} -> {target})")
            if source and target in by_sheet and end is not None:
                if source in by_sheet or source not in page_sheet_ids:
                    raise ValueError(
                        "Connexion VSDX invalide : feuille de connecteur absente "
                        f"ou équipement utilisé comme connecteur ({source})")
                # A connector end may appear more than once in external Visio
                # Connects tables. Identical rows are harmless, but competing
                # targets would silently change the SAN topology depending on
                # XML ordering. Never invent a winner for an ambiguous link.
                destination = by_sheet[target]
                previous = connections.setdefault(source, {}).get(end)
                if previous is not None and previous != destination:
                    raise ValueError(
                        "Connexion VSDX ambiguë : extrémité de connecteur "
                        f"{source}/{end} reliée à plusieurs équipements")
                connections[source][end] = destination
        for sid in sorted(connector_sources):
            ends = connections.get(sid, {})
            a, b = ends.get("BeginX"), ends.get("EndX")
            if a and b and a != b:
                # Distinct Visio connector sheets represent distinct links,
                # even when both terminate on the same pair of devices.
                # Never invent FC port numbers during a geometric import.
                edge = {"id": f"visio-p{index}-link-{sid}",
                        "from": a, "to": b, "layer": layer_id,
                        "visio_connector_sheet_id": str(sid)}
                if sid in connector_captions:
                    edge["label"] = connector_captions[sid]
                if sid in connector_route_points:
                    from .visio_route import node_route_signature, validate_visio_route
                    # Visio page coordinates are inches with Y increasing up;
                    # OpenVisio uses pixels with Y increasing down. Store the
                    # converted route only after endpoint IDs resolve to the
                    # flattened nodes created for this page.
                    page_nodes = {node["id"]: node for node in nodes}
                    source_node, target_node = page_nodes.get(a), page_nodes.get(b)
                    if source_node is not None and target_node is not None:
                        route = {
                            "schema": 1,
                            "source": node_route_signature(source_node),
                            "target": node_route_signature(target_node),
                            "points": [[round(x * PX_PER_IN, 3),
                                        round(offset + height - y * PX_PER_IN, 3)]
                                       for x, y in connector_route_points[sid]],
                        }
                        # Reuse the same strict bounds and orthogonality rules
                        # applied to user-opened JSON documents.
                        edge["visio_route"] = validate_visio_route(route)
                        edge["routing"] = "orthogonal"
                        orthogonal_routes_preserved += 1
                    else:
                        edge["routing"] = "orthogonal"
                        orthogonal_routes_approximated += 1
                edges.append(edge)
            else:
                # A one-ended or self-connected Visio link cannot be represented
                # as an OpenVisio equipment-to-equipment edge. Keep the import
                # usable but make the missing physical path visible in the GUI.
                reason = ("self_loop" if a and b else
                          "incomplete" if a or b else "unresolved")
                skipped_connectors[reason] += 1
                if len(skipped_connector_examples) < 12:
                    skipped_connector_examples.append(f"page {index} / sheet {sid}: {reason}")
        offset += max(height, 600) + 96 + bottom_overflow
    metadata = {"import_format": "VSDX", "page_count": len(pages),
                "import_mode": "flattened-pages",
                "limitations": ["masters", "group-rotation", "rotation", "styles",
                                "unsupported-formulas", "connector-waypoints"],
                "orthogonal_connector_routes_preserved": orthogonal_routes_preserved,
                "orthogonal_connector_routes_approximated": orthogonal_routes_approximated,
                "connector_waypoint_preservation_scope": (
                    "public formula-free static orthogonal geometry only; other Visio formulas, "
                    "frames and dynamic glue are not evaluated"),
                "connector_links_skipped": sum(skipped_connectors.values()),
                "connector_links_skipped_by_reason": skipped_connectors,
                "connector_links_skipped_examples": skipped_connector_examples,
                "rotated_shapes_as_bounding_boxes": rotated_count,
                "formula_driven_geometry_shapes": formula_geometry_shapes,
                "formula_driven_geometry_examples": formula_geometry_examples,
                "formula_driven_geometry_evaluated_shapes": formula_geometry_evaluated_shapes,
                "formula_driven_geometry_cells_evaluated": formula_geometry_cells_evaluated,
                "formula_driven_geometry_unresolved_shapes": formula_geometry_unresolved_shapes,
                "formula_driven_geometry_unresolved_examples": formula_geometry_unresolved_examples,
                "formula_evaluation_scope": "bounded arithmetic, cached scalar cell references, numeric ThePage dimensions and allowlisted scalar functions; no complete ShapeSheet interpreter",
                "group_children_omitted": grouped_children_omitted,
                "group_children_imported": grouped_children_imported,
                "page_extent_expanded": page_extent_expanded,
                "page_bottom_overflow_px_total": round(page_bottom_overflow_total, 3)}
    if (rotated_count or formula_geometry_unresolved_shapes or grouped_children_omitted
            or grouped_children_imported or page_extent_expanded
            or orthogonal_routes_approximated or sum(skipped_connectors.values())):
        metadata["fidelity_warnings"] = (
            [f"{rotated_count} rotated Visio shape(s) approximated by axis-aligned bounding boxes"]
            if rotated_count else []) + (
            [f"{grouped_children_omitted} nested group child shape(s) omitted: local transforms unsupported"]
            if grouped_children_omitted else []) + (
            [f"{grouped_children_imported} nested group child shape(s) imported with hierarchy; exact group transforms/rotation not preserved"]
            if grouped_children_imported else []) + (
            [f"{page_extent_expanded} Visio page(s) expanded to contain out-of-page shapes; page layout is approximate"]
            if page_extent_expanded else []) + (
            [f"{orthogonal_routes_approximated} orthogonal Visio connector(s) "
             "could not retain their original bend coordinates"]
            if orthogonal_routes_approximated else []) + (
            [f"{sum(skipped_connectors.values())} Visio connector(s) omitted: "
             f"{skipped_connectors['incomplete']} incomplete, "
             f"{skipped_connectors['self_loop']} self-linked, "
             f"{skipped_connectors['unresolved']} unsupported endpoints; "
             "review connector_links_skipped_examples before relying on SAN topology"]
            if sum(skipped_connectors.values()) else []) + (
            [f"{formula_geometry_unresolved_shapes} Visio shape(s) use formula-driven geometry that could not be evaluated safely within the supported scalar subset and geometry bounds; "
             "cached cell values were used"
             + (": " + "; ".join(formula_geometry_unresolved_examples)
                if formula_geometry_unresolved_examples else "")]
            if formula_geometry_unresolved_shapes else [])
    return validate({"nodes": nodes, "edges": edges, "layers": layers, "metadata": metadata})
