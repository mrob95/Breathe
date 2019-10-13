from .testutils import TText
import pytest, os
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext
from six import PY2
engine = get_engine("text")

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "my_grammar/fruit.py")

def test_loading():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import TText

Breathe.add_commands(
    None,
    {
        "apple": TText("fruit"),
    }
)
"""
        )
    modules = {
        "tests": {
            "my_grammar": ["fruit"],
        }
    }
    Breathe.load_modules(modules)
    engine.mimic("apple")

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
    # I have no idea why this is necessary, it's a total hack
    if PY2:
        os.remove(file_path + "c")
    engine.mimic("rebuild everything")
    with pytest.raises(MimicFailure):
        engine.mimic("apple")
    engine.mimic("parsnip")


def test_clear():
    Breathe.clear()
    Breathe.imported_modules = []