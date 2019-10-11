from dragonfly import Context

class CommandContext(Context):

    def __init__(self, name, enabled=False):
        Context.__init__(self)
        self._enabled = enabled
        self.name = name
        self._str = name

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def matches(self, executable, title, handle):
        return self._enabled
