from dragonfly import Repetition, ActionBase, Empty

class CommandsRef(Repetition):
    """
        An extra which references an arbitrary sequence of breathe CCR commands.
        Initially this is just a placeholder, it is populated with commands
        when a sub grammar is created.

        Adjust "max" and "min" to control how many commands may be recognised
        in the sequence.
    """
    def __init__(self, name, max=4, min=1, default=None):
        Repetition.__init__(
            self, child=Empty(), min=min, max=max+1, name=name, default=default
        )


class Exec(ActionBase):
    """
        Dragonfly Action which executes a sequence of commands in a top-level rule.
        If the sequence is optional and is omitted then this will do nothing.

        Use this as a template if you want to do more complex things like
        recording commands before execution.
    """
    def __init__(self, name):
        self._name = name
        ActionBase.__init__(self)

    def _execute(self, data=None):
        if self._name not in data:
            return
        action_list = data[self._name]
        if not isinstance(action_list, list):
            raise TypeError
        for action in action_list:
            action.execute()
