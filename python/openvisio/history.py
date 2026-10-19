"""Document snapshot history for reversible editing. Author: Abdelhalim Talbi."""
from copy import deepcopy
from .model import validate

class History:
    def __init__(self, document, limit=100):
        self.limit = max(1, int(limit))
        self.past = []
        self.future = []
        self.current = deepcopy(validate(document))

    def record(self, document):
        snapshot = deepcopy(validate(document))
        if snapshot == self.current:
            return False
        self.past.append(self.current)
        self.past = self.past[-self.limit:]
        self.current = snapshot
        self.future.clear()
        return True

    def undo(self):
        if not self.past:
            return None
        self.future.append(self.current)
        self.current = self.past.pop()
        return deepcopy(self.current)

    def redo(self):
        if not self.future:
            return None
        self.past.append(self.current)
        self.current = self.future.pop()
        return deepcopy(self.current)

    def reset(self, document):
        self.past.clear()
        self.future.clear()
        self.current = deepcopy(document)
