from dragonfly import Context

class TrueContext(Context):
    def matches(self, *args, **kwargs):
        return True