from dragonfly import Grammar


class SubGrammar(Grammar):

    def process_begin(self, executable, title, handle):
        """
            Enabling and disabling this grammar is handled
            by the merger
        """
        pass

    def _process_begin(self):

        if self._enabled:
            [r.activate() for r in self._rules if not r.active]
        else:
            [r.deactivate() for r in self._rules if r.active]

