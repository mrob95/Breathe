from dragonfly import Repetition, ActionBase, Empty

class Nested(Repetition):
    def __init__(self, name, max=4, min=1, default=None):
        Repetition.__init__(
            self, child=Empty(), min=min, max=max, name=name, default=default
        )


class ExecNested(ActionBase):
    def __init__(self, name):
        self._name = name
        ActionBase.__init__(self)

    def _execute(self, data=None):
        action_list = data[self._name]
        if not isinstance(action_list, list):
            raise TypeError
        for action in action_list:
            action.execute()
