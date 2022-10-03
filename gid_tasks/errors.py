"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidTaskBaseError(Exception):
    ...


class GidTomlBaseError(GidTaskBaseError):
    ...


class NotUniqueNestedKey(GidTomlBaseError):
    def __init__(self, nested_key: str) -> None:
        self.nested_key = nested_key
        self.msg = f"The key {self.nested_key!r} is not unique in the Toml-file, it occures more than 1 time."
        super().__init__(self.msg)


class ProjectInfoBaseError(GidTaskBaseError):
    ...


class VersionNotFoundError(ProjectInfoBaseError):
    ...


class FileSystemErrors(OSError):
    ...


class AmbigousBaseFolderError(ProjectInfoBaseError):
    def __init__(self, *found_base_folders) -> None:
        self.found_base_folders = tuple(found_base_folders)
        self.msg = f"Different folder were found as base folders -> {self.found_base_folders!r}."
        super().__init__(self.msg)


class IsFolderError(FileSystemErrors):

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.msg = f"The path {self.file_path.as_posix()!r} is a Folder and not a File."
        super().__init__(self.msg)


class WrongFileTypeError(FileSystemErrors):
    ...


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
