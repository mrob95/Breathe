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
from breathe.errors import CommandSkippedWarning, ExtraSkippedWarning
from breathe.elements import CommandsRef, Exec
import warnings

engine = get_engine("text")


def test_top_level_command():
    Breathe.add_commands(None, {"orange": TText("juice"), "grapefruit": TText("juice")})
    Breathe.add_commands(
        AppContext("notepad"), {"lemon": TText("juice"), "banana": TText("juice")}
    )
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "fruit from <sequence1> and [<sequence2>] [<n>]": TText("something")
            + Exec("sequence1")
            + TText("something else")
            + Exec("sequence2")* Repeat("n")
        },
        extras=[CommandsRef("sequence1"), CommandsRef("sequence2", 2), IntegerRef("n", 1, 10, 1)],
        top_level=True,
    )

def test_top_level_command2():
    Breathe.add_commands(
        AppContext(title="chrome"), {"pear": TText("juice"), "grape": TText("juice")}
    )

def test_global_top_level():
    Breathe.add_commands(
        None,
        {
            "<sequence1> are preferable to <sequence2>": TText("something")
            + Exec("sequence1")
            + TText("something else")
            + Exec("sequence2")
        },
        extras=[CommandsRef("sequence1"), CommandsRef("sequence2", 3)],
        top_level=True,
    )

def test_recognition():
    engine.mimic("lemon", executable="notepad")
    engine.mimic("fruit from lemon banana orange and five", executable="notepad")

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

def test_top_level_command_failure():
    with warnings.catch_warnings(record=True) as w:
        Breathe.add_commands(
            AppContext("china"),
            {
                "fruit from <sequence1> and <sequence2> [<n>]": TText("something")
                + Exec("sequence1")
                + TText("something else")
                + Exec("sequence2")* Repeat("n")
            },
            extras=[CommandsRef("sequence1"), CommandsRef("sequence2", 2), IntegerRef("n", 1, 10, 1)],
            top_level=False,
        )
        assert len(w) == 3
        assert issubclass(w[0].category, ExtraSkippedWarning)
        assert issubclass(w[2].category, CommandSkippedWarning)

def test_clear():
    Breathe.clear()
