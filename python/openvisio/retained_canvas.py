"""Incremental Tk Canvas updates from OpenVisio's existing drawing commands.

The same renderer produces the full legacy display list and the retained one.
Only tagged OpenVisio document items are managed; overlays and foreign Canvas
items remain untouched. No assumptions about document object identity are made.
Author: Abdelhalim Talbi.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DrawCommand:
    kind: str
    coordinates: tuple
    options: dict


class _CaptureCanvas:
    """Record the *same* rendering operations without touching a real Tk widget."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.commands = {}

    def winfo_width(self):
        return self.canvas.winfo_width()

    def winfo_height(self):
        return self.canvas.winfo_height()

    def delete(self, selector):
        # draw_document starts with delete('all'); no real canvas is cleared.
        if selector != 'all':
            raise ValueError('Unexpected drawing-list deletion')

    def _append(self, kind, coords, options):
        tags = options.get('tags', ())
        if isinstance(tags, str):
            tags = (tags,)
        if len(tags) != 1:
            raise ValueError('Retained drawing requires one stable object tag')
        key = tags[0]
        if key in self.commands:
            raise ValueError('Duplicate retained Canvas object tag: ' + key)
        self.commands[key] = DrawCommand(kind, tuple(coords), dict(options))

    def create_line(self, *coords, **options):
        self._append('line', coords, options)

    def create_rectangle(self, *coords, **options):
        self._append('rectangle', coords, options)

    def create_text(self, *coords, **options):
        self._append('text', coords, options)


class RetainedCanvasRenderer:
    """Keep Tk item IDs stable and update only changed geometry/style.

    Render plans are built before any Canvas mutation, so an invalid diagram
    cannot half-update the existing scene. On a Tk error, clear only owned
    items and invalidate the cache; the next redraw can recover.
    """

    def __init__(self, canvas):
        self.canvas = canvas
        self._items = {}
        self._commands = {}
        self._order = ()

    def reset(self):
        for item_id in self._items.values():
            self.canvas.delete(item_id)
        self._items.clear()
        self._commands.clear()
        self._order = ()

    def draw(self, document, selected_node=None, selected_edge=None,
             viewport=None, grid=False, grid_spacing=20, selected_nodes=None):
        from .render import draw_document
        captured = _CaptureCanvas(self.canvas)
        draw_document(captured, document, selected_node, selected_edge,
                      viewport, grid, grid_spacing, selected_nodes)
        commands = captured.commands
        old_order = self._order
        try:
            for key in self._commands.keys() - commands.keys():
                self.canvas.delete(self._items.pop(key))
            for key, command in commands.items():
                old = self._commands.get(key)
                if old is not None and old.kind == command.kind:
                    if old.coordinates != command.coordinates:
                        self.canvas.coords(self._items[key], *command.coordinates)
                    if old.options != command.options:
                        updates = {name: value for name, value in command.options.items()
                                   if old.options.get(name) != value}
                        if updates:
                            self.canvas.itemconfigure(self._items[key], **updates)
                else:
                    if old is not None:
                        self.canvas.delete(self._items[key])
                    factory = getattr(self.canvas, 'create_' + command.kind)
                    self._items[key] = factory(*command.coordinates, **command.options)
            new_order = tuple(commands)
            if new_order != old_order:
                for key in new_order:
                    self.canvas.tag_raise(self._items[key])
            self._commands = commands
            self._order = new_order
        except Exception:
            self.reset()
            raise

    @property
    def retained_item_count(self):
        return len(self._items)
