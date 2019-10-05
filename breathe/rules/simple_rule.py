from dragonfly import Rule

class SimpleRule(Rule):

    def process_recognition(self, node):
        value = node.value()
        if isinstance(value, list):
            for action in node.value():
                action.execute()
        else:
            value.execute()