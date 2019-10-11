from .testutils import TText
import pytest
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext

engine = get_engine("text")

def test_manual_context():
    Breathe.add_commands(
        CommandContext("test"),
        {"pizza": TText("margarita"),
        "curry": TText("wurst"),
        }
    )
    # Fails because the rule isn't enabled yet
    with pytest.raises(MimicFailure):
        engine.mimic(["pizza", "pizza"])
    engine.mimic(["enable", "test"])
    engine.mimic(["pizza", "curry", "pizza"])

def test_manual_context_noccr():
    Breathe.add_commands(
        CommandContext("test") | AppContext("italy"),
        {"spaghetti": TText("bolognese")},
        ccr=False
    )
    # Loaded rule should be referencing the original
    # "test" context loaded above, which should already be
    # active
    engine.mimic(["spaghetti"])
    engine.mimic(["disable", "test"])
    with pytest.raises(MimicFailure):
        engine.mimic(["spaghetti"])
        engine.mimic(["pizza", "curry"])
    engine.mimic(["spaghetti"], executable="italy")

def test_negated_context():
    Breathe.add_commands(
        ~(CommandContext("america") | AppContext("england")),
        {"steak": TText("chips"),
        }
    )
    engine.mimic(["steak"])
    with pytest.raises(MimicFailure):
        engine.mimic(["steak"], executable="england")
    engine.mimic(["enable", "america"])
    with pytest.raises(MimicFailure):
        engine.mimic(["steak"])

def test_everything_context():
    engine.mimic(["disable", "breathe"])
    with pytest.raises(MimicFailure):
        engine.mimic(["spaghetti"], executable="italy")
    engine.mimic(["enable", "breathe"])
    engine.mimic(["spaghetti"], executable="italy")


def test_clear():
    Breathe.clear()