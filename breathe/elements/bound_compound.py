from dragonfly import Compound as CompoundBase

class BoundCompound(CompoundBase):
    """
        Compound class whose value property will be an Action.

        When value() is called this action will be bound with the relevant extras and passed up to be executed.
    """
    def value(self, node):
        extras = {"_node": node}
        for name, element in self._extras.items():
            extra_node = node.get_child_by_name(name, shallow=True)
            if extra_node:
                extras[name] = extra_node.value()
            elif element.has_default():
                extras[name] = element.default
        if self._value is not None:
            return self._value.copy_bind(extras)
