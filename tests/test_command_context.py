from .testutils import DoNothing
import pytest
from dragonfly import get_engine, MimicFailure, AppContext
from breathe import Breathe, CommandContext

engine = get_engine("text")

def test_manual_context():
    Breathe.add_commands(
        CommandContext("test"),
        {"pizza": DoNothing(),
        "curry": DoNothing(),
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
        {"spaghetti": DoNothing()},
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
        {"steak": DoNothing(),
        }
    )
    engine.mimic(["steak"])
    with pytest.raises(MimicFailure):
        engine.mimic(["steak"], executable="england")
    engine.mimic(["enable", "america"])
    with pytest.raises(MimicFailure):
        engine.mimic(["steak"])


def test_clear():
    Breathe.clear()