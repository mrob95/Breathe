from .testutils import TText
import pytest
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext

engine = get_engine("text")

import os

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "my_grammar/main.py")

def test_loading():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import TText

Breathe.add_commands(
    None,
    {
        "banana": TText("fruit"),
    }
)
"""
        )
    modules = {
        "tests": {
            "my_grammar": ["main"],
        }
    }
    Breathe.load_modules(modules)
    engine.mimic("banana")

def test_reloading():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import TText

Breathe.add_commands(
    None,
    {
        "parsnip": TText("vegetable"),
    }
)
"""
        )
    engine.mimic("rebuild everything")
    engine.mimic("parsnip")
    with pytest.raises(MimicFailure):
        engine.mimic("banana")


def test_clear():
    Breathe.clear()
    Breathe.imported_modules = []