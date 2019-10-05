# Breathe
A convenient API for creating dragonfly grammars.

```python
from breathe import *

Breathe.add_commands(
    context = AppContext(title=".py"),
    mapping = {
        "for each"          : Text("for  in :") + Key("left:5"),
        "for loop"          : Text("for i in range():") + Key("left:2"),
        "from import"       : Text("from  import ") + Key("home, right:5"),
        "function"          : Text("def ():") + Key("left:3"),
        "(iffae | iffy)"    : Text("if :") + Key("left"),
        "iffae not"         : Text("if not :") + Key("left"),
        "import"            : Text("import "),
        "lambda"            : Text("lambda :") + Key("left"),
        "while loop"        : Text("while :") + Key("left"),
        "shell iffae"       : Text("elif :") + Key("left"),
        "shells"            : Text("else:"),
        "return"            : Text("return "),
        # ------------------------------------------------
        "method [<under>] <snaketext>": Text("def %(under)s%(snaketext)s(self):")
        + Key("left:2"),
        "function <snaketext>": Text("def %(snaketext)s():") + Key("left:2"),
        "selfie [<under>] [<snaketext>]": Text("self.%(under)s%(snaketext)s"),
        "pointer [<under>] [<snaketext>]": Text(".%(under)s%(snaketext)s"),
        "classy [<classtext>]": Text("class %(classtext)s:") + Key("left"),
    },
    extras = [
        Dictation("snaketext", default="").lower().replace(" ", "_"),
        Dictation("classtext", default="").title().replace(" ", ""),
        Choice("under", "_", default=""),
    ]
)
```