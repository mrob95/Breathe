from .grammar.master import Master
from .elements import CommandContext
import sys as _sys

if not hasattr(_sys, "_called_from_test"):
    # Some discussion here of whether this pattern is a good idea, I think it's fine for now.
    # https://stackoverflow.com/questions/9561042/python-init-py-and-initialization-of-objects-in-a-code
    Breathe = Master()
else:
    from dragonfly import get_engine
    engine = get_engine("text")
    Breathe = Master(engine=engine)
