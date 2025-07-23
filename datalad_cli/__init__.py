from functools import partial
from inspect import signature

import click

from datalad_lib.cmd_demo import demo_command
from datalad_lib.cmd_demo_w_ctx import demo_command_w_ctx
from datalad_lib.cmdgrp_color import color_cmd_group
from datalad_lib.cmdgrp_root import root_cmd_group

from datalad_core.constraints import Constraint


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
    return ret


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
        # TODO evaluate whether that is worth the trouble, it would
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
    # TODO https://click.palletsprojects.com/en/stable/parameter-types/#id6
    # implement a dynamic custom click type.
    # however, for now just use the constraint directly, click supports
    # a function that raises ValueError as a fallback
    #breakpoint()
    constraint.__name__ = constraint.input_synopsis
    return constraint


def get_argument_name(param_name: str) -> str:
    return param_name.lower().replace('_', '-')


def get_option_names(param_name: str) -> str:
    return (f'--{get_argument_name(param_name)}',)


if __name__ == '__main__':
    # TODO read argument spec from command implementations
    # or rather their decorated interfaces
    root_group = click.group(
        name='root',
    )(add_click_api(root_cmd_group, group=True))
    root_group.command(
        name='demo',
    )(add_click_api(demo_command))

    color_group = root_group.group(
        name='color',
    )(add_click_api(color_cmd_group, group=True))
    color_group.command(
        name='democtx',
    )(add_click_api(demo_command_w_ctx))

    root_group()
