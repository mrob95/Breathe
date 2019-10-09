from dragonfly import Alternative, Repetition
from .simple_rule import SimpleRule

class RepeatRule(SimpleRule):

    def __init__(self, name, children, max_reps=16):

        alts = Alternative(children)
        element = Repetition(alts, 1, max_reps)
        SimpleRule.__init__(self, name, element)
