from functools import partial
from importlib.metadata import entry_points
from inspect import signature

import click
from datalad_core.constraints import Constraint

from datalad_lib.cmdgrp_root import root_cmd_group


def grp_handler(fx, ctx, *args, **kwargs):

    class DummyProbe:
        """"""

    if ctx.obj and 'ctx' in signature(fx).parameters:
        ret = fx(DummyProbe, ctx.obj, *args, **kwargs)
    else:
        ret = fx(DummyProbe, *args, **kwargs)
    ctx.obj = ret.ctx


def cmd_handler(fx, ctx, *args, **kwargs):
    if ctx.obj and 'ctx' in signature(fx).parameters:
        ret = fx(ctx.obj, *args, **kwargs)
    else:
        ret = fx(*args, **kwargs)
    print(f"RET: {ret!r}")


def add_click_api(fx, *, group=False):
    params = signature(fx).parameters
    constraints = fx.preproc._param_constraints \
        if hasattr(fx, 'preproc') else {}
    fx = partial(grp_handler if group else cmd_handler, fx)
    # ATM all handlers require a context to be passed and decide
    # internally whether a command implementation needs to see it
    fx = click.pass_context(fx)
    for p in params.values():
        if group and p.name == 'cls':
            # internal parameter
            # dealth with by the group handler
            continue
        if p.name == 'ctx':
            # internal parameter
            # dealth with by respective handler
            continue
        # click can do per-parameter type validation and conversion,
        # we can recycle any parameter preprocessor for that
        # TODO: evaluate whether that is worth the trouble, it would
        # be limited to individual parameters. One reason to do it
        # would be to expose information for implementing completion
        ptype = None
        phelp = None
        constraint = constraints.get(p.name)
        if constraint is not None:
            ptype = get_click_type(constraint)
            phelp = constraint.input_description
        if p.default is p.empty:
            fx = click.argument(
                get_argument_name(p.name),
                type=ptype,
                phelp=phelp,
            )(fx)
        else:
            fx = click.option(
                *get_option_names(p.name),
                default=p.default,
                type=ptype,
                help=phelp,
            )(fx)

    return fx


def get_click_type(constraint: Constraint):
    # TODO: https://click.palletsprojects.com/en/stable/parameter-types/#id6
    # implement a dynamic custom click type.
    # however, for now just use the constraint directly, click supports
    # a function that raises ValueError as a fallback
    # YES, THIS IS A HACK
    constraint.__name__ = constraint.input_synopsis
    return constraint


def get_argument_name(param_name: str) -> str:
    return param_name.lower().replace('_', '-')


def get_option_names(param_name: str) -> tuple[str]:
    return (f'--{get_argument_name(param_name)}',)


def get_entrypoint_name(ctx):
    name = ctx.command.name

    c = ctx
    while c.parent is not None:
        c = c.parent
        name = f'{c.command.name}:{name}'
    return name.lstrip(':')


class LazyGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        eps = entry_points(group='datalad.api')
        group_ep_name_prefix = f'{get_entrypoint_name(ctx)}:'.strip(':')
        return [
            ep.name[len(group_ep_name_prefix):]
            for ep in eps
            if ep.name.startswith(group_ep_name_prefix)
            and ep.name.count(':') == group_ep_name_prefix.count(':')
        ]

    def get_command(self, ctx, cmd_name):
        ep_name = f'{get_entrypoint_name(ctx)}:{cmd_name}'.lstrip(':')
        ep = entry_points(
            group='datalad.api',
            name=ep_name,
        )[ep_name]

        group = any(e.name.startswith(f'{cmd_name}:')
                    for e in entry_points(group='datalad.api'))

        fx = add_click_api(ep.load(), group=group)

        if group:
            return click.group(
                cls=LazyGroup,
                name=cmd_name,
            )(fx)

        return click.command(
            name=cmd_name,
        )(fx)


if __name__ == '__main__':
    root_group = click.group(
        cls=LazyGroup,
        name='',
    )(add_click_api(root_cmd_group, group=True))

    root_group()
