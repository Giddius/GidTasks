"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Any, Union, Optional, TypedDict

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from pathlib import Path
from functools import total_ordering

# * Third Party Imports --------------------------------------------------------------------------------->
from frozendict import frozendict

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
        return None

    if isinstance(in_data, int):
        return in_data

    if in_data.isnumeric():
        return int(in_data)

    return in_data


def convert_maybe_path(in_data: Union[str, os.PathLike, Path, None]) -> Union[Path, None]:
    if in_data is None:
        return None

    return Path(in_data).resolve()


class Construction_Params_Dict(TypedDict):
    major: int
    minor: int
    patch: int
    extra: Optional[Union[int, str]]
    meta_data: Optional[dict[str, object]]


@total_ordering
class Version:
    def __init__(self, major: int, minor: int, patch: int, extra: Union[int, str] = None, meta_data: dict[str, object] = None) -> None:
        self._major = major
        self._minor = minor
        self._patch = patch
        self._extra = extra
        self._meta_data = frozendict(meta_data) if meta_data is not None else frozendict()

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    @property
    def extra(self) -> Optional[Union[int, str]]:
        return self._extra

    @property
    def meta_data(self) -> frozendict[str, Any]:
        return self._meta_data

    @property
    def _construction_params(self) -> Construction_Params_Dict:
        return {"major": self.major,
                "minor": self.minor,
                "patch": self.patch,
                "extra": self.extra,
                "meta_data": self._meta_data}

    def set_meta_data(self, key: str, value: Any) -> "Version":
        meta_data = dict(self.meta_data)
        meta_data[key] = value

        kwargs = self._construction_params
        kwargs["meta_data"] = meta_data
        return self.__class__(**kwargs)

    def increment_major(self) -> "Version":
        major = self.major + 1
        minor = 0
        patch = 0
        extra = None

        kwargs = self._construction_params
        kwargs["major"] = major
        kwargs["minor"] = minor
        kwargs["patch"] = patch
        kwargs["extra"] = extra
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def set_major(self, new_major: int) -> "Version":
        kwargs = self._construction_params
        kwargs["major"] = new_major
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def increment_minor(self) -> "Version":
        minor = self.minor + 1
        patch = 0
        extra = None

        kwargs = self._construction_params
        kwargs["minor"] = minor
        kwargs["patch"] = patch
        kwargs["extra"] = extra
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def set_minor(self, new_minor: int) -> "Version":
        kwargs = self._construction_params
        kwargs["minor"] = new_minor
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def increment_patch(self) -> "Version":
        patch = self.patch + 1
        extra = None
        kwargs = self._construction_params
        kwargs["patch"] = patch
        kwargs["extra"] = extra
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def set_patch(self, new_patch: int) -> "Version":
        kwargs = self._construction_params
        kwargs["patch"] = new_patch
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def set_extra(self, extra_value: Optional[Union[str, int]] = None) -> "Version":
        kwargs = self._construction_params
        kwargs["extra"] = extra_value
        return self.__class__(major=kwargs["major"], minor=kwargs["minor"], patch=kwargs["patch"], extra=kwargs["extra"], meta_data=kwargs["meta_data"])

    def as_string(self) -> str:
        text = f"{self.major}.{self.minor}.{self.patch}"
        if self.extra is not None:
            text += f".{self.extra}"
        return text

    def as_tuple(self) -> tuple[int, int, int, Optional[Union[str, int]]]:
        return (self.major, self.minor, self.patch, self.extra)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.as_tuple() == other.as_tuple()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.as_tuple() < other.as_tuple()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(major={self.major!r}, minor={self.minor!r}, patch={self.patch!r}, extra={self.extra!r})"

    def __str__(self) -> str:
        return self.as_string()


class FlitVersion(Version):

    def write_version(self) -> "Version":
        file = self.meta_data.get("file")
        line_number = self.meta_data.get("line_number")

        if file is None:
            raise FileNotFoundError(file)

        old_content = file.read_text(encoding='utf-8', errors='ignore')
        old_version_line = [line.strip() for line in old_content.splitlines()][line_number]
        new_version_line = f'__version__ = "{self!s}"'
        new_content = old_content.replace(old_version_line, new_version_line)
        file.write_text(new_content, encoding='utf-8', errors='ignore')
        return self


version_table: dict["PipManager", type[Version]] = {PipManager.FLIT: FlitVersion}


def get_specific_version(pip_manager: "PipManager", major: int, minor: int, patch: int, extra: Union[str, int] = None, file: Path = None, line_number: int = None) -> "Version":
    klass = version_table.get(pip_manager, Version)
    return klass(major=major, minor=minor, patch=patch, extra=extra, file=file, line_number=line_number)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
