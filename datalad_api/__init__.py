from __future__ import annotations

from datalad_api._version import __version__

__all__ = [
    '__version__',
    'api',
]


from functools import partial
from inspect import signature

# TODO: Demo command parameter validation
# TODO: Demo command group parameter validation
# TODO: Make command load lazily


from datalad_lib.cmd_demo import demo_command
from datalad_lib.cmd_demo_w_ctx import demo_command_w_ctx
from datalad_lib.cmdgrp_root import root_cmd_group
from datalad_lib.cmdgrp_color import color_cmd_group


class CmdGroup:
    """Base for implementing command groups"""

    def __getattribute__(self, name):
        if name == 'ctx':
            return super().__getattribute__(name)

        # TODO: here would be some kind of "entrypoint" lookup for the
        # command group
        if name == 'demo':
            fx = demo_command
        elif name == 'democtx':
            fx = demo_command_w_ctx
        elif name == 'color':
            fx = ColorCmdGroup
        else:
            raise RuntimeError

        # TODO: within click the equivalent would be achieved via
        # the pass_obj decorator
        return partial(fx, self.ctx) if 'ctx' in signature(fx).parameters else fx


RootCmdGroup = type(
    "RootCmdGroup",
    (CmdGroup, ),
    {
        '__new__': root_cmd_group,
    },
)


ColorCmdGroup = type(
    "ColorCmdGroup",
    (CmdGroup, ),
    {
        '__new__': color_cmd_group,
    },
)

api = RootCmdGroup
