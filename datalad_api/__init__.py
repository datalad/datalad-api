from __future__ import annotations

from importlib.metadata import entry_points

from datalad_api._version import __version__

__all__ = [
    '__version__',
    'api',
]


from functools import partial
from inspect import signature

# TODO: Demo command group parameter validation
from datalad_lib.cmdgrp_root import root_cmd_group


def get_entrypoint_name(ctx: CmdGroup):
    return ''


class CmdGroup:
    """Base for implementing command groups"""

    def __getattribute__(self, name):
        if name in ('ctx', 'api_entrypoint'):
            return super().__getattribute__(name)

        parent_ep_name = getattr(self, 'api_entrypoint', '')
        cmd_name = name
        ep_name = f'{parent_ep_name}:{cmd_name}'.lstrip(':')
        ep = entry_points(
            group='datalad.api',
            name=ep_name,
        )[ep_name]

        group = any(e.name.startswith(f'{cmd_name}:')
                    for e in entry_points(group='datalad.api'))

        fx = ep.load()
        if group:
            fx = type(
                f'{fx.__name__}_cls',
                (CmdGroup,),
                {
                    '__new__': fx,
                    'api_entrypoint': ep_name,
                }
            )

        # TODO: within click the equivalent would be achieved via
        # the pass_obj decorator
        return partial(fx, ctx=self.ctx) if 'ctx' in signature(fx).parameters else fx


RootCmdGroup = type(
    "RootCmdGroup",
    (CmdGroup, ),
    {
        '__new__': root_cmd_group,
    },
)

api = RootCmdGroup
