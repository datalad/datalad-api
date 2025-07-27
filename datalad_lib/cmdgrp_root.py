from . import RootCmdGroupContext


def root_cmd_group(
    cls,
    version: bool = False,
    log_level: int = 10,
):
    """A specific command group

    Implementation requires a definition of the group-specific API
    in the signature of __new__. And it require the creation of
    a dataclass instance with all arguments that define the context
    available to any subcommand in the group that wants it. This
    context may not be identical to the group API from the signature
    of __new__().

    TODO: check that __new__() can be decorated with a parameter
    validator.
    """
    # implementation of an "inline command"
    # return not a `cls` instance, hence no chaining
    if version:
        return 'VERSION'

    # all about subcommands from here
    obj = super(cls, cls).__new__(cls)
    obj.ctx = RootCmdGroupContext(
        log_level=log_level,
    )
    return obj


