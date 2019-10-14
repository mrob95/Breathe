from .testutils import TText
import pytest, os, warnings
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext
from breathe.errors import ModuleSkippedWarning
from six import PY2
engine = get_engine("text")

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "my_grammar/fruit.py")

def test_failed_reload():
    with pytest.raises(ModuleNotFoundError):
        Breathe.reload_modules()

def test_loading_failure():
    with open(file_path, "w") as f:
        f.write("""
from breathe import Breathe
from ..testutils import TText

Breathe.add_commands(,,,
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
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        Breathe.load_modules(modules)
        assert issubclass(w[0].category, ModuleSkippedWarning)

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
    engine.mimic("rebuild everything")
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