from dragonfly import (
    Grammar,
    Rule,
    Text,
    ElementBase,
    Function,
    Context,
    Alternative,
    Compound,
    DictList,
)
from ..rules import RepeatRule, SimpleRule, ContextSwitcher
from .subgrammar import SubGrammar
from ..elements import BoundCompound, CommandContext
from ..errors import CommandSkippedWarning
from six import string_types, PY2
import warnings, importlib

"""
    Example:

    We have added a set of core commands (context=None) and two sets of context commands,
    all ccr. This produces a list of core command, a list of lists of context commands,
    and a list of contexts.

        self.core_commands = [BoundCompound(...), ...]
        self.context_commands = [[BoundCompound(...), ...], [...]]
        self.contexts = [AppContext("notepad"), AppContext("chrome")]

    We now start an utterance in notepad. process_begin is called, active contexts are
    (True, False). We look this up in the grammar map and since we haven't seen this
    combination of contexts before, we need to add a new grammar for it. We combine the
    core commands with the notepad command list from context_commands, create a repeat
    rule and load it in a new sub grammar. We add this subgrammar to the grammar map
    so that we never need to create it again. We continue in this way, adding subgrammars
    on-the-fly for whatever combination of contexts comes up.
"""


class Master(Grammar):

    MAX_REPETITIONS = 16

    def __init__(self, **kwargs):
        Grammar.__init__(self, "Merger", context=None, **kwargs)

        self.count = 0
        # List[Compound]
        self.core_commands = []
        # List[List[Compound]]
        self.context_commands = []
        # List[Context]
        self.contexts = []

        # Dict[Tuple[bool], SubGrammar]
        # Key of dictionary is the contexts the rule matched
        self.grammar_map = {}
        # List[Grammar]
        self.non_ccr_grammars = []

        # Dict[str, ElementBase]
        self.global_extras = {}

        # Command contexts are switched by user commands like "enable breathe"
        self.everything_context = CommandContext("breathe", enabled=True)
        # The DictList makes it easy to add new mappings from command context names
        # which will be recognised by the "enable/disable" command to the contexts themselves
        self.command_context_dictlist = DictList(
            "manual_contexts", {"breathe": self.everything_context}
        )
        self.add_rule(ContextSwitcher(self.command_context_dictlist))
        self.add_rule(SimpleRule(
            "rebuilder",
            BoundCompound(
                "rebuild everything",
                value = Function(lambda: self.reload_modules())
                )
            )
        )

        self.imported_modules = []

        self.load()

    # ------------------------------------------------
    # API

    def add_commands(
        self, context=None, mapping=None, extras=None, defaults=None, ccr=True
    ):
        """Add a set of commands which can be recognised continuously.

        Keyword Arguments:
            context (Context) -- Context in which these commands will be active, if None, commands will be global (default: None)
            mapping (dict) -- Dictionary of rule specs to dragonfly Actions (default: None)
            extras (list) -- Extras which will be available for these commands (default: None)
            defaults (dict) -- Defaults for the extras, if necessary (default: None)
            ccr (bool) -- Whether these commands should be recognised continuously (default: True)
        """
        full_extras = self._construct_extras(extras, defaults)
        children = self._construct_commands(mapping, full_extras)
        if not children:
            return
        if context is not None:
            context = self.everything_context & self._check_for_manuals(context)

        if not ccr:
            rule = SimpleRule(element=Alternative(children), context=context)
            grammar = Grammar("NonCCR" + self.counter())
            grammar.add_rule(rule)
            grammar.load()
            self.non_ccr_grammars.append(grammar)
        elif context is None:
            self.core_commands.extend(children)
        else:
            assert isinstance(context, Context)
            self.context_commands.append(children)
            self.contexts.append(context)
            self._pad_matches()

    def add_global_extras(self, *extras):
        """
            Global extras will be available to all commands,
            but must be added before the commands which use them.

            Defaults should be assigned on the extras themselves.
        """
        if len(extras) == 1 and isinstance(extras[0], list):
            extras = extras[0]
        for e in extras:
            assert isinstance(e, ElementBase)
            self.global_extras.update({e.name: e})

    def load_modules(self, modules, namespace=""):
        """
            Loads a set of modules into breathe, and makes them available for reloading
            using the "rebuild everything" command.

            Modules should be passed as a dictionary, with keys representing folder names
            and values being either a single module to import, a list of modules to import,
            or another dictionary. These can be nested arbitrarily deep. e.g.

                Breathe.load_modules(
                    {
                        "my_commands": {
                            "apps": ["chrome", "notepad"],
                            "language": ["python", "c"],
                            "core": ["keys", "alphabet"],
                        }
                    }
                )

            Called from _main.py in a folder structure that looks like:
                |   _main.py
                |   __init__.py
                +---my_commands
                |   |   __init__.py
                |   +---apps
                |   |       chrome.py
                |   |       notepad.py
                |   |       __init__.py
                |   +---core
                |   |       alphabet.py
                |   |       keys.py
                |   |       __init__.py
                |   +---language
                |   |       c.py
                |   |       python.py
                |   |       __init__.py
        """
        if isinstance(modules, dict):
            for k, v in modules.items():
                deeper_namespace = "%s.%s" % (namespace, k) if namespace else k
                self.load_modules(v, deeper_namespace)
        elif isinstance(modules, list):
            for module in modules:
                self.load_modules(module, namespace)
        elif isinstance(modules, str):
            module_name = "%s.%s" % (namespace, modules) if namespace else modules
            self.imported_modules.append(importlib.import_module(module_name))

    # ------------------------------------------------
    # Loading helpers

    def reload_modules(self):
        """
            Reload all modules loaded using load_modules.
        """
        self.clear()
        for module in self.imported_modules:
            if PY2:
                reload(module)
            else:
                importlib.reload(module)

    def clear(self):
        """
            Removes all added rules, unloads all grammars, etc.
        """
        self.core_commands = []
        self.context_commands = []
        self.contexts = []
        for subgrammar in self.grammar_map.values():
            subgrammar.unload()
        for grammar in self.non_ccr_grammars:
            grammar.unload()
        self.grammar_map = {}
        self.non_ccr_grammars = []
        self.global_extras = {}
        self.command_context_dictlist.clear()

    def counter(self):
        """
            Generate numbers for unique naming of rules and grammars
        """
        self.count += 1
        return str(self.count)

    def _construct_extras(self, extras=None, defaults=None):
        """
            Takes a list of extras provided by the user, and merges it with all global
            extras to produce the {name: extra} dictionary that dragonfly expects.

            In naming conflicts global extras will always be overridden, otherwise
            the later extra will win.
        """
        full_extras = self.global_extras.copy()
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

    def _construct_commands(self, mapping, extras=None):
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
                warnings.warn(str(e), CommandSkippedWarning)
        return children

    def _check_for_manuals(self, context):
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
            if context.name in self.command_context_dictlist:
                context = self.command_context_dictlist[context.name]
            else:
                self.command_context_dictlist[context.name] = context
        elif hasattr(context, "_children"):
            new_children = [self._check_for_manuals(c) for c in context._children]
            context._children = tuple(new_children)
        elif hasattr(context, "_child"):
            context._child = self._check_for_manuals(context._child)
        return context

    def _pad_matches(self):
        """
            If a new context is added after we have already started creating subgrammars,
            then to avoid pointlessly recreating them we use the already existing grammars
            when the new context is inactive.
        """
        for k, v in self.grammar_map.copy().items():
            padded = list(k)
            padded.append(False)
            matches = tuple(padded)
            if matches not in self.grammar_map:
                self.grammar_map[matches] = v

    # ------------------------------------------------
    # Runtime grammar management

    def _add_repeater(self, matches):
        """
            Takes a tuple of bools, corresponding to which contexts were matched,
            and loads a SubGrammar containing a RepeatRule with all relevant commands in.
        """
        matched_commands = []
        for command_list in [l for (l, b) in zip(self.context_commands, matches) if b]:
            matched_commands.extend(command_list)
        matched_commands.extend(self.core_commands)

        if not matched_commands:
            return

        rule = RepeatRule(
            "Repeater%s" % self.counter(), matched_commands, self.MAX_REPETITIONS
        )
        subgrammar = SubGrammar("SG%s" % self.counter())
        subgrammar.add_rule(rule)

        subgrammar.load()
        self.grammar_map[matches] = subgrammar

    def process_begin(self, executable, title, handle):
        """
            Check which of our contexts the current window matches and look this up in our grammar map.

            If we haven't seen this combination before, add a new subgrammar for it.

            Enable the subgrammar which matches the window, and disable all others.
        """
        active_contexts = tuple(
            [c.matches(executable, title, handle) for c in self.contexts]
        )

        if active_contexts not in self.grammar_map:
            self._add_repeater(active_contexts)

        for contexts, subgrammar in self.grammar_map.items():
            if active_contexts == contexts:
                subgrammar.enable()
            else:
                subgrammar.disable()

            subgrammar._process_begin()
