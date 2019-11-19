from .testutils import DoNothing
import pytest, os
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext
from six import PY2
engine = get_engine("text")

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "my_grammar/fruit.py")

def test_loading_failure():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import DoNothing

Breathe.add_commands(,,,
    None,
    {
        "apple": DoNothing(),
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
    assert len(Breathe.modules) == 1
    assert len(Breathe.core_commands) == 0

def test_loading():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import DoNothing

Breathe.add_commands(
    None,
    {
        "apple": DoNothing(),
    }
)
"""
        )
    engine.mimic("rebuild everything test")
    engine.mimic("apple")

def test_reloading():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import DoNothing

Breathe.add_commands(
    None,
    {
        "parsnip": DoNothing(),
    }
)
"""
        )
    # I have no idea why this is necessary, it's a total hack
    if PY2:
        os.remove(file_path + "c")
    engine.mimic("rebuild everything test")
    with pytest.raises(MimicFailure):
        engine.mimic("apple")
    engine.mimic("parsnip")
    assert len(Breathe.modules) == 1


def test_clear():
    Breathe.clear()
    Breathe.modules = []