"""Pure world/screen coordinate transforms for diagram navigation. Author: Abdelhalim Talbi."""

class Viewport:
    def __init__(self, zoom=1.0, offset_x=0.0, offset_y=0.0):
        self.zoom = float(zoom)
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    def screen(self, x, y):
        return x * self.zoom + self.offset_x, y * self.zoom + self.offset_y

    def world(self, x, y):
        return (x - self.offset_x) / self.zoom, (y - self.offset_y) / self.zoom

    def zoom_at(self, factor, x, y):
        wx, wy = self.world(x, y)
        self.zoom = max(0.2, min(4.0, self.zoom * factor))
        self.offset_x = x - wx * self.zoom
        self.offset_y = y - wy * self.zoom

    def pan(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy

    def fit(self, nodes, screen_width, screen_height, margin=80):
        if not nodes:
            self.zoom, self.offset_x, self.offset_y = 1.0, 0.0, 0.0
            return
        left = min(n["x"] - 70 for n in nodes)
        right = max(n["x"] + 70 for n in nodes)
        top = min(n["y"] - 30 for n in nodes)
        bottom = max(n["y"] + 30 for n in nodes)
        usable_width = max(1, screen_width - 2 * margin)
        usable_height = max(1, screen_height - 2 * margin)
        self.zoom = max(0.2, min(4.0, min(usable_width / max(1, right - left), usable_height / max(1, bottom - top))))
        self.offset_x = screen_width / 2 - (left + right) / 2 * self.zoom
        self.offset_y = screen_height / 2 - (top + bottom) / 2 * self.zoom
