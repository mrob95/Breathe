from dragonfly import (
    get_engine,
    Text as TextBase,
    Dictation,
    IntegerRef,
    MimicFailure,
    AppContext,
    Choice,
    Repeat,
)
import pytest
from breathe import Breathe, ManualContext
from breathe.errors import CommandSkippedWarning
import warnings

engine = get_engine("text")


class TText(TextBase):
    def _execute(self, data):
        pass


def test_global_extras():
    Breathe.add_global_extras(Dictation("text"))
    assert len(Breathe.global_extras) == 1
    assert "text" in Breathe.global_extras


def test_core_commands():
    Breathe.add_commands(
        None,
        {
            "test one": TText("1"),
            "test two": TText("2"),
            "test three": TText("3"),
            "banana [<n>]": TText("banana") * Repeat("n"),
        },
        [IntegerRef("n", 1, 10, 1)],
    )
    assert len(Breathe.core_commands) == 4
    assert len(Breathe.core_commands[0]._extras) == 2


def test_context_commands():
    Breathe.add_commands(
        AppContext("notepad"),
        {"test [<num>]": lambda num: TText(num).execute()},
        [Choice("num", {"four": "4", "five": "5", "six": "6"})],
        {"num": ""},
    )
    assert len(Breathe.context_commands) == 1
    assert len(Breathe.contexts) == 1
    assert len(Breathe.context_commands[0]) == 1
    assert len(Breathe.context_commands[0][0]._extras) == 2
    assert Breathe.context_commands[0][0]._extras["num"].has_default()


def test_nomapping_commands():
    Breathe.add_commands(AppContext("code.exe"), {})


def test_no_extra():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        Breathe.add_commands(
            AppContext("code.exe"),
            {"test that <nonexistent_extra>": TText("%(nonexistent_extra)s")},
        )
        assert len(w) == 1
        assert issubclass(w[0].category, CommandSkippedWarning)


def test_noccr_commands():
    Breathe.add_commands(
        AppContext("firefox"),
        {"dictation <text>": TText("%(text)s"), "testing static": TText("Static")},
        ccr=False,
    )
    assert len(engine.grammars) == 2


def test_merging1():
    Breathe.process_begin("chrome", "", "")
    assert len(Breathe.grammar_map) == 1
    assert (False,) in Breathe.grammar_map
    active_subgrammar = Breathe.grammar_map[(False,)]
    assert len(active_subgrammar.rules) == 2
    active_rule = active_subgrammar.rules[0]
    assert len(active_rule.element._child._children) == 4


def test_merging2():
    Breathe.process_begin("notepad", "", "")
    assert len(Breathe.grammar_map) == 2
    assert (True,) in Breathe.grammar_map
    active_subgrammar = Breathe.grammar_map[(True,)]
    assert active_subgrammar.enabled
    assert len(active_subgrammar.rules) == 2
    active_rule = active_subgrammar.rules[0]
    assert active_rule.active
    assert len(active_rule.element._child._children) == 5


def test_recognition():
    engine.mimic(["test", "three", "test", "two", "banana"])
    # engine.mimic(["testing", "static"], executable="firefox")
    with pytest.raises(MimicFailure):
        engine.mimic(["dictation", "TESTING"])
    # engine.mimic(["dictation", "TESTING"], executable="firefox")
    with pytest.raises(MimicFailure):
        engine.mimic(["test", "three", "test", "four"])
    # engine.mimic(["test", "three", "test", "four"], executable="notepad")

def test_manual_context():
    Breathe.add_commands(
        ManualContext("test"),
        {"pizza": TText("margarita")}
    )
    with pytest.raises(MimicFailure):
        engine.mimic(["pizza", "pizza"])
    engine.mimic(["enable", "test"])
    engine.mimic(["pizza", "banana"])

def test_manual_context_noccr():
    Breathe.add_commands(
        ManualContext("test"),
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
        engine.mimic(["pizza", "banana"])
