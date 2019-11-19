
from breathe import Breathe
from ..testutils import DoNothing

Breathe.add_commands(
    None,
    {
        "parsnip": DoNothing(),
    }
)
