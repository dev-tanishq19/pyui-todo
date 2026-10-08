"""pyui.state - when data changes, subscribers (the app) are told to re-render."""


class State:
    def __init__(self, **initial):
        self._data = dict(initial)
        self._subscribers = []

    def subscribe(self, fn):
        self._subscribers.append(fn)

    def __getitem__(self, key):
        return self._data[key]

    def set(self, **changes):
        self._data.update(changes)
        for fn in self._subscribers:      # data changed -> UI updates
            fn()
