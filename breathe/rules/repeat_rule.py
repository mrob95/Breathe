from dragonfly import Alternative, Repetition
from .simple_rule import SimpleRule

class RepeatRule(SimpleRule):

    def __init__(self, name, children):

        alts = Alternative(children)
        element = Repetition(alts, 1, 16)
        SimpleRule.__init__(self, name, element)
