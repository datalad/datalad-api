import gettext
from pathlib import Path


def get_pkg_localedir(pkg_root_mod) -> Path:
    return Path(pkg_root_mod.__file__).parent / 'locales'


def get_pkg_translation(pkg_root_mod):
    return gettext.translation(
        'messages',
        localedir=str(get_pkg_localedir(pkg_root_mod)),
        fallback=True,
    )


def i18n(text: str) -> str:
    """Dummy function to mark strings as translatable.

    This cannot be used in places that actually require retrieving
    the translation. This is only to mark up translatable string
    when and where no immediate translation is needed.
    """
    return text
