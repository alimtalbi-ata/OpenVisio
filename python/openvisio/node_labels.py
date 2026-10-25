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
    return max(1, floor(usable / (float(font_size) * 0.62)))


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
