"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Iterable, Optional, Generator

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from pathlib import Path
from functools import cached_property

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gid_tasks.project_info.toml import PyProjectTomlFile

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MainModule:

    def __init__(self, base_folder: Path, pyproject_data: "PyProjectTomlFile") -> None:
        self.base_folder = base_folder
        self.pyproject_data = pyproject_data

    @cached_property
    def base_init_file(self) -> Optional[Path]:
        _init_file = self.base_folder.joinpath('__init__.py')
        if _init_file.is_file():
            return _init_file

    @cached_property
    def main_file(self) -> Optional[Path]:
        _main_file = self.base_folder.joinpath('__main__.py')
        if _main_file.is_file():
            return _main_file

    def get_all_python_files(self, exclude_init: bool = False, extra_excludes: Iterable[str] = None) -> Generator[Path, None, None]:
        extra_excludes = [] if extra_excludes is None else list(extra_excludes)
        for dirname, folderlist, filelist in os.walk(self.base_folder):
            for file_path in filelist:
                file = Path(dirname, file_path)
                if file.suffix != '.py':
                    continue
                if file.name == '__init__.py' and exclude_init is True:
                    continue
                if any(file.match(excludes) for excludes in extra_excludes):
                    continue
                yield file

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_folder={self.base_folder.as_posix()!r}, pyproject_data={self.pyproject_data!r})"

    def __str__(self) -> str:
        return self.base_folder.as_posix()

    def __fspath__(self) -> str:
        return self.base_folder.as_posix()
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
