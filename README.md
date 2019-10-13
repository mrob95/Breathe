# Breathe [![Build Status](https://travis-ci.org/mrob95/Breathe.svg?branch=master)](https://travis-ci.org/mrob95/Breathe)
A convenient API for creating [dragonfly](https://github.com/dictation-toolbox/dragonfly) grammars with automatic CCR (continuous command recognition).

* Very quick start-up
* Command activity can be controlled either using dragonfly contexts or using "enable" and "disable" commands.
* All commands which match the current context may be chained together in any order in the same utterance.

## Installation
```
pip install dfly-breathe
```

## Example
### Adding commands

```python
from dragonfly import *
from breathe import Breathe, CommandContext

Breathe.add_commands(
    # Commands will be active either when we are editing a python file
    # or after we say "enable python". pass None for the commands to be global.
    context = AppContext(title=".py") | CommandContext("python"),
    mapping = {
        "for each"              : Text("for  in :") + Key("left:5"),
        "for loop"              : Text("for i in range():") + Key("left:2"),
        "from import"           : Text("from  import ") + Key("home, right:5"),
        "function"              : Text("def ():") + Key("left:3"),
        "(iffae | iffy)"        : Text("if :") + Key("left"),
        "iffae not"             : Text("if not :") + Key("left"),
        "import"                : Text("import "),
        "lambda"                : Text("lambda :") + Key("left"),
        "while loop"            : Text("while :") + Key("left"),
        "shell iffae"           : Text("elif :") + Key("left"),
        "shells"                : Text("else:"),
        "return"                : Text("return "),
        # ------------------------------------------------
        "method <snaketext>"    : Text("def %(snaketext)s(self):") + Key("left:2"),
        "function [<snaketext>]": Text("def %(snaketext)s():") + Key("left:2"),
        "selfie [<snaketext>]"  : Text("self.%(snaketext)s"),
        "pointer [<snaketext>]" : Text(".%(snaketext)s"),
        "classy [<classtext>]"  : Text("class %(classtext)s:") + Key("left"),
    },
    extras = [
        Dictation("snaketext", default="").lower().replace(" ", "_"),
        Dictation("classtext", default="").title().replace(" ", ""),
    ]
)
```

For full details of the available contexts, actions and extras you can use, see the [dragonfly documentation](https://dragonfly.readthedocs.io/en/latest/).

### Loading command files
Breathe provides the command "rebuild everything" for reloading all of your commands,
allowing you to modify commands without restarting the engine. In order for this to work,
your command files need to be loaded by giving your directory structure to
`Breathe.load_modules()`.

For example, given a directory set up like this:
```
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
```

Inside `_main.py`, the file which will be loaded by the engine, we load all of our command
files by passing a dictionary with keys representing folder name and values being either a
single module to import, a list of modules to import, or another dictionary. Like so:
```
from breathe import Breathe

Breathe.load_modules(
    {
        "my_commands": {
            "apps": ["chrome", "notepad"],
            "language": ["python", "c"],
            "core": ["keys", "alphabet"],
        }
    }
)
```

Given this setup, calling the "rebuild everything" command will reload all of your command
files, making any changes available.

## Notes
* If you are using the kaldi backend, you will need to set `lazy_compilation=False` in the `get_engine` function in your loader file.
