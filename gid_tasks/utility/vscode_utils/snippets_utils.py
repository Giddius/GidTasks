"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Union, Iterable

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from pathlib import Path
from collections.abc import Iterable

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def strip_only_wrapping_empty_lines(in_text: str) -> str:
    """

    :param in_text: str:

    """
    empty_line_pattern = re.compile(r"(^\s*)|(\s*$)")
    return empty_line_pattern.sub("", in_text)


def make_snippet_body(in_code_text: str, as_string: bool = True, pre_extra_lines: Iterable[str] = None, post_extra_lines: Iterable[str] = None) -> Union[list[str], str]:
    pre_extra_lines = list(pre_extra_lines) if pre_extra_lines is not None else []
    post_extra_lines = list(post_extra_lines) if post_extra_lines is not None else []
    snippet_body = pre_extra_lines + [l for l in strip_only_wrapping_empty_lines(in_code_text).splitlines()] + post_extra_lines
    if as_string is False:
        return snippet_body

    return json.dumps(snippet_body, sort_keys=False, indent=4, default=str)

# region[Main_Exec]


if __name__ == '__main__':
    a = """

try:
    from .misc import *
except ImportError:
    pass



    """
    print(make_snippet_body(a))
# endregion[Main_Exec]
