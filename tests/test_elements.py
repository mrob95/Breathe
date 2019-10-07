from dragonfly import *

from breathe.elements import BoundCompound

def test_bound_compound():
    c1 = BoundCompound(
        spec="test <n> [<text>]",
        extras=[IntegerRef("n", 1, 10), Dictation("text", "")],
        value=Text("test %(text)s")*Repeat("n")
        )

    bound_value = c1._value.copy_bind({"n": "3", "text": "test"})
    assert isinstance(bound_value, ActionBase)
    assert bound_value._data == {"n": "3", "text": "test"}
    assert bound_value._action == c1._value