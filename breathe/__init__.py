from .grammar.master import Master
import sys

if not hasattr(sys, "_called_from_test"):
    Breathe = Master()
