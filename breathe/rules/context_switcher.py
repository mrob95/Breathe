from dragonfly import DictListRef, Function, Alternative
from .simple_rule import SimpleRule
from ..elements import BoundCompound

class ContextSwitcher(SimpleRule):

    def __init__(self, dictlist):
        ref = DictListRef("context", dictlist)
        enable = BoundCompound(
                        "enable <context>",
                        extras=[ref],
                        value=Function(lambda context: context.enable())
                    )
        disable = BoundCompound(
                        "disable <context>",
                        extras=[ref],
                        value=Function(lambda context: context.disable())
                    )
        SimpleRule.__init__(self, element=Alternative(children=(enable, disable)))