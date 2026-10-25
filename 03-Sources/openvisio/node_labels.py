"""Lossless wrapping helpers for equipment labels in Tk and SVG.

Only the visual projection is wrapped; persisted node labels are never rewritten.
Author: Abdelhalim Talbi.
"""
from math import floor, isfinite


def label_char_limit(width, *, font_size=13, padding=12):
    """Estimate a conservative characters-per-line limit from shape width.

    This deterministic estimate avoids font/device-specific measurements, so
    the editor and SVG exporter use the same normal-zoom line breaks. Tk may
    impose a stricter limit at extremely low zoom.
    """
    for value, name in ((width, "width"), (font_size, "font_size"),
                        (padding, "padding")):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not isfinite(value)):
            raise ValueError(f"Invalid {name}")
    if width <= 0 or font_size <= 0 or padding < 0:
        raise ValueError("Label geometry out of range")
    usable = max(1.0, float(width) - float(padding))
    return max(1, floor(usable / (float(font_size) * 0.68)))


def wrap_label_lines(value, max_chars):
    """Wrap without dropping, normalizing, or duplicating any label characters.

    Existing CRLF/CR/LF breaks are honored, including blank and trailing lines.
    A separating whitespace character stays at the preceding visual row's end;
    long tokens are hard-wrapped only when no whitespace fits. Joining wrapped
    rows within each original paragraph exactly reproduces that paragraph.
    """
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise ValueError("max_chars must be a positive integer")
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    result = []
    for paragraph in text.split("\n"):
        remaining = paragraph
        while len(remaining) > max_chars:
            cut = max(remaining.rfind(" ", 0, max_chars),
                      remaining.rfind("\t", 0, max_chars))
            if cut > 0:
                result.append(remaining[:cut + 1])
                remaining = remaining[cut + 1:]
            else:
                result.append(remaining[:max_chars])
                remaining = remaining[max_chars:]
        result.append(remaining)
    return tuple(result)


def fit_node_label(value, width, height, *, font_size=13, padding=12,
                   vertical_padding=8, minimum_font_size=6):
    """Return lossless wrapped rows and a font size fitted to the node height.

    Font size is reduced only in the visual projection when a caption needs
    more rows than the shape can hold. If the minimum size still cannot fit an
    unusually large caption, every row is returned instead of truncating it.
    """
    for number, name in ((height, "height"), (vertical_padding, "vertical_padding"),
                         (minimum_font_size, "minimum_font_size")):
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not isfinite(number):
            raise ValueError(f"Invalid {name}")
    if height <= 0 or vertical_padding < 0 or minimum_font_size < 1:
        raise ValueError("Label height out of range")
    if isinstance(font_size, bool) or not isinstance(font_size, (int, float)) or not isfinite(font_size) or font_size < 1:
        raise ValueError("Invalid font_size")
    start = max(int(minimum_font_size), int(font_size))
    smallest = max(1, int(minimum_font_size))
    available_height = max(1.0, float(height) - float(vertical_padding))
    for size in range(start, smallest - 1, -1):
        lines = wrap_label_lines(value, label_char_limit(width, font_size=size, padding=padding))
        if len(lines) * size * 1.35 <= available_height:
            return lines, size
    size = smallest
    return wrap_label_lines(value, label_char_limit(width, font_size=size, padding=padding)), size
