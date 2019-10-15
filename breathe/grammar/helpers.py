from dragonfly import ElementBase, Function, Repetition
from ..elements import BoundCompound, CommandContext, Nested
from ..errors import CommandSkippedWarning, ModuleSkippedWarning
from six import string_types, PY2
import warnings
import sys
import importlib


def construct_extras(extras=None, defaults=None, global_extras=None):
    """
        Takes a list of extras provided by the user, and merges it with all global
        extras to produce the {name: extra} dictionary that dragonfly expects.

        In naming conflicts global extras will always be overridden, otherwise
        the later extra will win.
    """
    if global_extras is None:
        full_extras = {}
    else:
        full_extras = global_extras.copy()
    if extras:
        assert isinstance(extras, (list, tuple))
        if defaults is None:
            defaults = {}
        assert isinstance(defaults, dict)
        for e in extras:
            assert isinstance(e, ElementBase)
            if not e.has_default() and e.name in defaults:
                e._default = defaults[e.name]
            full_extras[e.name] = e
    return full_extras


def construct_commands(mapping, extras=None):
    """
        Constructs a list of BoundCompound objects from a mapping and an
        extras dict.

        Also automatically converts all callables to dragonfly Function objects,
        allowing e.g.

            mapping = {"foo [<n>]": lambda n: foo(n),}
    """
    children = []
    assert isinstance(mapping, dict)
    for spec, value in mapping.items():
        if callable(value):
            value = Function(value)
        try:
            assert isinstance(spec, string_types)
            c = BoundCompound(spec, extras=extras, value=value)
            children.append(c)
        except Exception as e:
            # No need to raise, we can just skip this command
            # Usually due to missing extras
            if str(e).startswith("Unknown reference name"):
                msg = "Missing extra"
            else:
                msg = str(e)
            warnings.warn_explicit(msg, CommandSkippedWarning, str(spec), 0)
    return children


def check_for_manuals(context, command_dictlist):
    """
        Slightly horrible recursive function which handles the adding of command contexts.

        If we haven't seen it before, we need to add the name of the context to our DictList
        so it can be accessed by the "enable" command.

        If we have seen it before, we need to ensure that there is only the one command
        context object being referenced from multiple rules, rather than one for each.

        This has to be done not only for CommandContext objects but also for ones
        embedded in the children of an e.g. LogicOrContext.
    """
    if isinstance(context, CommandContext):
        if context.name in command_dictlist:
            context = command_dictlist[context.name]
        else:
            command_dictlist[context.name] = context
    elif hasattr(context, "_children"):
        new_children = [
            check_for_manuals(c, command_dictlist) for c in context._children
        ]
        context._children = tuple(new_children)
    elif hasattr(context, "_child"):
        context._child = check_for_manuals(context._child, command_dictlist)
    return context


def load_or_reload(module_name):
    try:
        if module_name not in sys.modules:
            importlib.import_module(module_name)
        else:
            module = sys.modules[module_name]
            if PY2:
                reload(module)
            else:
                importlib.reload(module)
    except Exception as e:
        warnings.warn_explicit(
            "Import failed with '%s'" % str(e), ModuleSkippedWarning, module_name, 0
        )

def process_nested_commands(command_lists, alts):
    matched_nested_commands = []
    for command_list in command_lists:
        new_extras = {}
        for n, e in command_list[0]._extras.items():
            if isinstance(e, Nested):
                new_extras[n] = Repetition(alts, e.min, e.max, e.name, e.default)
            else:
                new_extras[n] = e
        new_command_list = [
            BoundCompound(c._spec, new_extras, value=c._value)
            for c in command_list
        ]
        matched_nested_commands.extend(new_command_list)
    return matched_nested_commands