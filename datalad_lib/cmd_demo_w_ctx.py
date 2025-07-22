from datalad_core.constraints import EnsureChoice

from . import RootCmdGroupContext
from .preproc import preproc_parameters


@preproc_parameters(
    test_kwarg=EnsureChoice('dummy', 'blob'),
)
def demo_command_w_ctx(
    ctx: RootCmdGroupContext,
    *,
    test_kwarg: str = 'dummy',
) -> str:
    """A command in a command group that requires some group context"""
    return f'talk context {ctx} {test_kwarg}'
