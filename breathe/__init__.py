from .grammar.master import Master
import sys

if not hasattr(sys, "_called_from_test"):
    Breathe = Master()
else:
    from dragonfly import get_engine
    engine = get_engine("text")
    Breathe = Master(engine=engine)

