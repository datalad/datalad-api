from __future__ import annotations

from functools import (
    wraps,
)
from inspect import (
    Parameter,
    signature,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import (
        Container,
        Iterable,
        Mapping,
    )

    from datalad_core.commands.param_constraint import ParamSetConstraint
    from datalad_core.constraints import Constraint

from datalad_core.commands.preproc import JointParamProcessor


# this could be a function decorator, but we use a class, because
# it is less confusing to read (compared to the alternative decorator
# factory
class preproc_parameters:  # noqa: N801  MIH wants lower-case
    def __init__(
        self,
        *,
        _proc_defaults: Container[str] | None = None,
        _set_constraints: Iterable[ParamSetConstraint] | None = None,
        _tailor_for_dataset: Mapping[str, str] | None = None,
        _on_error: str | None = None,
        **kwargs: Constraint,
    ):
        self.preproc = JointParamProcessor(
            param_constraints=kwargs,
            proc_defaults=_proc_defaults,
            paramset_constraints=_set_constraints,
            tailor_for_dataset=_tailor_for_dataset,
            on_error=_on_error,
        )

    def __call__(self, wrapped):
        @wraps(wrapped)
        def command_wrapper(*args, **kwargs):
            # produce a single dict (parameter name -> parameter value)
            # from all parameter sources
            allkwargs, params_at_default = get_allargs_as_kwargs(
                wrapped,
                args,
                kwargs,
            )
            # preprocess the ful parameterization
            if self.preproc is not None:
                allkwargs = self.preproc(
                    allkwargs,
                    at_default=params_at_default,
                )

            # let the result handler drive the underlying command and
            # let it do whatever it considers best to do with the
            # results
            return wrapped(**allkwargs)

        sig = signature(wrapped)
        command_wrapper.__signature__ = sig

        # make decorator parameterization accessible to postprocessing
        # consumers
        command_wrapper.preproc = self.preproc
        return command_wrapper


def update_with_extra_kwargs(
    handler_kwarg_specs: dict[str, Parameter],
    deco_kwargs: dict[str, Any],
    **call_kwargs,
) -> dict[str, Any]:
    """Helper to update command kwargs with additional arguments

    Two sets of additional arguments are supported:

    - kwargs specifications (result handler provided) to extend the signature
      of an underlying command
    - ``extra_kwarg_defaults`` (given to the ``datalad_command`` decorator)
      that override the defaults of handler-provided kwarg specifications
    """
    # retrieve common options from kwargs, and fall back on the command
    # class attributes, or general defaults if needed
    updated_kwargs = {
        p_name: call_kwargs.get(
            # go with any explicitly given value
            p_name,
            # otherwise ifall back on what the command has been decorated with
            deco_kwargs.get(
                p_name,
                # or lastly go with the implementation default
                param.default,
            ),
        )
        for p_name, param in handler_kwarg_specs.items()
    }
    return dict(call_kwargs, **updated_kwargs)


def get_allargs_as_kwargs(call, args, kwargs, extra_kwarg_specs=None):
    """Generate a kwargs dict from a call signature and actual parameters

    The first return value is a mapping of all argument names to their
    respective values.

    The second return value is a set of argument names for which the effective
    value is identical to the default declared in the signature of the
    callable (or extra kwarg specification).
    """
    # we base the parsing off of the callables signature
    params = dict(signature(call).parameters.items())
    # and also add the common parameter definitions to get a joint
    # parameter set inspection
    if extra_kwarg_specs is not None:
        params.update(extra_kwarg_specs)

    args = list(args)
    allkwargs = {}
    at_default = set()
    missing_args = []
    for pname, param in params.items():
        val = args.pop(0) if len(args) else kwargs.get(pname, param.default)
        allkwargs[pname] = val
        if val == param.default:
            at_default.add(pname)
        if val is param.empty:
            missing_args.append(pname)

    if missing_args:
        ma = missing_args
        multi_ma = len(ma) > 1
        # imitate standard TypeError message
        msg = (
            f'{call.__name__}() missing {len(ma)} required '
            f'positional argument{"s" if multi_ma else ""}: '
            f'{", ".join(repr(a) for a in ma[:-1 if multi_ma else None])}'
        )
        if multi_ma:
            msg += f' and {ma[-1]!r}'
        raise TypeError(msg)

    return allkwargs, at_default
