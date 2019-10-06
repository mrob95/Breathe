from dragonfly import *

engine = get_engine("text")
from breathe import Master

Breathe = Master()

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
            "test one": Text("1"),
            "test two": Text("2"),
            "test three": Text("3"),
            "test [<n>]": Key("c-t:%(n)s"),
        }
    )
    assert len(Breathe.core_commands) == 4

def test_context_commands():
    Breathe.add_commands(
        AppContext("notepad"),
        {
            "test <num>": Text("%(num)s"),
        },
        [
            Choice("num", {
                "four": "4",
                "five": "5",
                "six": "6",
            })
        ]
    )
    assert len(Breathe.context_commands) == 1
    assert len(Breathe.contexts) == 1
    assert len(Breathe.context_commands[0]) == 1
    # Two global extras plus one specific
    assert len(Breathe.context_commands[0][0]._extras) == 3


def test_noccr_commands():
    Breathe.add_commands(
        AppContext("firefox"),
        {
            "test <text>": Text("%(text)s"),
        },
        ccr=False
    )
    assert len(engine.grammars) == 2

def test_merging():
    Breathe.process_begin("chrome", "", "")
    assert len(Breathe.grammar_map) == 1
    assert (False,) in Breathe.grammar_map
    active_subgrammar = Breathe.grammar_map[(False,)]
    assert len(active_subgrammar.rules) == 2
    active_rule = active_subgrammar.rules[0]
    assert len(active_rule.element._child._children) == 4

    Breathe.process_begin("notepad", "", "")
    assert len(Breathe.grammar_map) == 2
    assert (True,) in Breathe.grammar_map
    active_subgrammar = Breathe.grammar_map[(True,)]
    assert len(active_subgrammar.rules) == 2
    active_rule = active_subgrammar.rules[0]
    assert len(active_rule.element._child._children) == 5
