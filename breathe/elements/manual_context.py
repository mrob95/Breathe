from dragonfly import Context

class ManualContext(Context):

    def __init__(self, name):
        Context.__init__(self)
        self._enabled = False
        self.name = name
        self._str = name

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def matches(self, executable, title, handle):
        return self._enabled
