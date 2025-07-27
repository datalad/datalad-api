import datalad_lib
from datalad_lib.i18n import get_pkg_translation, i18n

_ = get_pkg_translation(datalad_lib).gettext


cmd_doc = i18n("""\
Some context-free/self-contained command implementation

Just a plain function, could have any arguments
""")


def demo_command() -> str:
    return 'talk shallow'


demo_command.__doc__ = _(cmd_doc)
