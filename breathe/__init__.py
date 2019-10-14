from .grammar.master import Master
from .elements import CommandContext
import os

# Some discussion here of whether this pattern is a good idea, I think it's fine for now.
# https://stackoverflow.com/questions/9561042/python-init-py-and-initialization-of-objects-in-a-code

if os.getenv('BREATHE_TESTING'):
    from dragonfly import get_engine
    Breathe = Master(engine=get_engine("text"))
else:
    Breathe = Master()
