from dataclasses import dataclass


@dataclass
class CmdGroupContext:
    """"""


@dataclass
class RootCmdGroupContext(CmdGroupContext):
    """Parameter set of a specific command group"""

    log_level: int


@dataclass
class ColorCmdGroupContext(RootCmdGroupContext):
    """Parameter set of a specific command subgroup

    There is no need to derive from a context. Only if there
    is a specific desire to pass some parameters from the parent
    context down.
    """
    new_stuff: str
