from dragonfly import (
    get_engine,
    Dictation,
    IntegerRef,
    MimicFailure,
    AppContext,
    Choice,
    Repeat,
)
from .testutils import TText

import pytest
from breathe import Breathe, CommandContext
from breathe.errors import CommandSkippedWarning
from breathe.elements import Sequence, ExecSequence
import warnings

engine = get_engine("text")


def test_nested_command():
    Breathe.add_commands(None, {"orange": TText("juice"), "grapefruit": TText("juice")})
    Breathe.add_commands(
        AppContext("notepad"), {"lemon": TText("juice"), "banana": TText("juice")}
    )
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "fruit from <sequence1> and <sequence2> [<n>]": TText("something")
            + ExecSequence("sequence1")
            + TText("something else")
            + ExecSequence("sequence2")* Repeat("n")
        },
        extras=[Sequence("sequence1"), Sequence("sequence2", 2), IntegerRef("n", 1, 10, 1)],
        nested=True,
    )

def test_nested_command2():
    Breathe.add_commands(
        AppContext(title="chrome"), {"pear": TText("juice"), "grape": TText("juice")}
    )

def test_global_nested():
    Breathe.add_commands(
        None,
        {
            "<sequence1> are preferable to <sequence2>": TText("something")
            + ExecSequence("sequence1")
            + TText("something else")
            + ExecSequence("sequence2")
        },
        extras=[Sequence("sequence1"), Sequence("sequence2", 3)],
        nested=True,
    )

def test_recognition():
    engine.mimic("lemon", executable="notepad")
    engine.mimic("fruit from lemon banana orange and grapefruit five", executable="notepad")

    engine.mimic(
        "fruit from pear banana orange and grapefruit",
        executable="notepad",
        title="chrome",
    )
    with pytest.raises(MimicFailure):
        engine.mimic(
            "fruit from pear banana orange and grapefruit", executable="notepad"
        )

    engine.mimic("orange grapefruit are preferable to grapefruit")
    engine.mimic("orange grapefruit are preferable to lemon banana", executable="notepad")

def test_clear():
    Breathe.clear()
