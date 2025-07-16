import click
from functools import partial
from inspect import signature

from datalad_lib.cmd_demo import demo_command
from datalad_lib.cmd_demo_w_ctx import demo_command_w_ctx
from datalad_lib.cmdgrp_root import root_cmd_group
from datalad_lib.cmdgrp_color import color_cmd_group


def grp_handler(fx, ctx, *args, **kwargs):
    #print(f"FX: {fx}, INCTX: {ctx.obj!r}")

    class DummyProbe:
        """"""

    if ctx.obj and 'ctx' in signature(fx).parameters:
        ret = fx(DummyProbe, ctx.obj, *args, **kwargs)
    else:
        ret = fx(DummyProbe, *args, **kwargs)
    ctx.obj = ret.ctx
    print(f"RET: {ret.ctx!r}")


def cmd_handler(fx, ctx, *args, **kwargs):
    #print(f"INCTX: {ctx.obj!r}")
    if ctx.obj and 'ctx' in signature(fx).parameters:
        ret = fx(ctx.obj, *args, **kwargs)
    else:
        ret = fx(*args, **kwargs)
    print(f"RET: {ret!r}")


if __name__ == '__main__':
    root_group = click.group(
        name='root',
    )(click.pass_context(
        partial(grp_handler, root_cmd_group),
    ))
    root_group.command(
        name='demo',
    )(click.pass_context(
        partial(cmd_handler, demo_command),
    ))

    color_group = root_group.group(
        name='color',
    )(click.pass_context(
        partial(grp_handler, color_cmd_group),
    ))
    color_group.command(
        name='democtx',
    )(click.pass_context(
        partial(cmd_handler, demo_command_w_ctx),
    ))
    root_group()
