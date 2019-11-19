from dragonfly import ActionBase

class DoNothing(ActionBase):
    def _execute(self, data):
        pass
