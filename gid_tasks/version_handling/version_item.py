"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Any, Union

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.utility.enums import PipManager

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def convert_maybe_int(in_data: Union[int, str, None]) -> Union[int, str, None]:
    if in_data is None:
        return

    if isinstance(in_data, int):
        return in_data

    if in_data.isnumeric():
        return int(in_data)

    return in_data


def convert_maybe_path(in_data: Union[str, os.PathLike, Path, None]) -> Union[Path, None]:
    if in_data is None:
        return

    return Path(in_data).resolve()


@attr.s(slots=False, auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class Version:
    major: int = attr.ib(converter=int)
    minor: int = attr.ib(converter=int)
    patch: int = attr.ib(converter=int)
    extra: Union[int, str] = attr.ib(default=None, converter=convert_maybe_int)
    file: Path = attr.ib(default=None, converter=convert_maybe_path)
    line_number: int = attr.ib(default=None, converter=convert_maybe_int)

    def increment_major(self) -> "Version":
        major = self.major + 1
        minor = 0
        patch = 0
        extra = None
        kwargs = vars(self) | {"major": major, "minor": minor, "patch": patch, "extra": extra}
        return self.__class__(**kwargs)

    def increment_minor(self) -> "Version":
        minor = self.minor + 1
        patch = 0
        extra = None

        kwargs = vars(self) | {"minor": minor, "patch": patch, "extra": extra}
        return self.__class__(**kwargs)

    def increment_patch(self) -> "Version":
        patch = self.patch + 1
        extra = None
        kwargs = vars(self) | {"patch": patch, "extra": extra}
        return self.__class__(**kwargs)

    def set_extra(self, extra_value: Any) -> "Version":
        extra = extra_value
        kwargs = vars(self) | {"extra": extra}
        return self.__class__(**kwargs)

    def write_version(self) -> "Version":
        return NotImplemented

    def version_string(self) -> str:
        text = f"{self.major}.{self.minor}.{self.patch}"
        if self.extra is not None:
            text += f".{self.extra}"
        return text

    def __repr__(self) -> str:
        file = self.file.as_posix() if self.file is not None else None
        return f"{self.__class__.__name__}(major={self.major!r}, minor={self.minor!r}, patch={self.patch!r}, extra={self.extra!r}, file={file!r}, line_number={self.line_number!r})"

    def __str__(self) -> str:
        return self.version_string()


class FlitVersion(Version):

    def write_version(self) -> "Version":
        if self.file is None:
            raise FileNotFoundError(self.file)

        old_content = self.file.read_text(encoding='utf-8', errors='ignore')
        old_version_line = [line.strip() for line in old_content.splitlines()][self.line_number - 1]
        new_version_line = f'__version__ = "{self!s}"'
        new_content = old_content.replace(old_version_line, new_version_line)
        self.file.write_text(new_content, encoding='utf-8', errors='ignore')
        return self


version_table: dict["PipManager", type[Version]] = {PipManager.FLIT: FlitVersion}


def get_specific_version(pip_manager: "PipManager", major: int, minor: int, patch: int, extra: Union[str, int] = None, file: Path = None, line_number: int = None) -> "Version":
    klass = version_table.get(pip_manager, Version)
    return klass(major=major, minor=minor, patch=patch, extra=extra, file=file, line_number=line_number)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
