from dragonfly import Rule


class SimpleRule(Rule):
    def __init__(
        self, name=None, element=None, context=None, imported=False, exported=True
    ):
        Rule.__init__(
            self,
            name=name,
            element=element,
            context=context,
            imported=imported,
            exported=exported,
        )

    def process_recognition(self, node):
        value = node.value()
        if isinstance(value, list):
            for action in node.value():
                action.execute()
        else:
            value.execute()
