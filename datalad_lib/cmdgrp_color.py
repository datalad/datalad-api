from . import ColorCmdGroupContext, RootCmdGroupContext


def color_cmd_group(
    cls,
    ctx: RootCmdGroupContext,
    new_stuff: str = 'fresh',
):
    obj = super(cls, cls).__new__(cls)
    obj.ctx = ColorCmdGroupContext(
        log_level=ctx.log_level,
        new_stuff=new_stuff,
    )
    return obj
