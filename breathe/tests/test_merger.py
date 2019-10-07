from dragonfly import *
import pytest

from breathe import Master
import time
engine = get_engine("text")
Breathe = Master(engine=engine)

class TText(Text):
    def _execute(self, data):
        pass

def test_global_extras():
    Breathe.add_global_extras(
        IntegerRef("n", 1, 10, 1),
        Dictation("text")
    )
    assert len(Breathe.global_extras) == 2
    assert "text" in Breathe.global_extras

def test_core_commands():
    Breathe.add_commands(
        None,
        {
            "test one": TText("1"),
            "test two": TText("2"),
            "test three": TText("3"),
            "banana [<n>]": TText("banana") * Repeat("n"),
        }
    )
    assert len(Breathe.core_commands) == 4
    assert len(Breathe.core_commands[0]._extras) == 2

def test_context_commands():
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "test [<num>]": TText("%(num)s"),
        },
        [
            Choice("num", {
                "four": "4",
                "five": "5",
                "six": "6",
            }),
        ],
        {
            "num": ""
        }
    )
    assert len(Breathe.context_commands) == 1
    assert len(Breathe.contexts) == 1
    assert len(Breathe.context_commands[0]) == 1
    # Two global extras plus one specific
    assert len(Breathe.context_commands[0][0]._extras) == 3
    assert Breathe.context_commands[0][0]._extras["num"].has_default()


def test_noccr_commands():
    Breathe.add_commands(
        AppContext("firefox"),
        {
            "test <text>": TText("%(text)s"),
        },
        ccr=False
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
    engine.mimic(["test", "three", "test", "two", "banana"])
    with pytest.raises(MimicFailure):
        engine.mimic(["test", "three", "test", "four"])

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
    with pytest.raises(MimicFailure):
        engine.mimic(["test", "three", "test", "twelve"])
