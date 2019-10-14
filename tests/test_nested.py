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
    Breathe.add_commands(
        None,
        {
            "orange": TText("juice"),
            "grapefruit": TText("juice"),
        }
    )
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "lemon": TText("juice"),
            "banana": TText("juice"),
        }
    )
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "fruit from <sequence1> and <sequence2>": TText("something") + ExecSequence("sequence1") + TText("something else") + ExecSequence("sequence2")
        },
        extras=[
            Sequence("sequence1"),
            Sequence("sequence2", 2),
        ],
        nested=True
    )
    engine.mimic("fruit from lemon banana orange and grapefruit", executable="notepad")