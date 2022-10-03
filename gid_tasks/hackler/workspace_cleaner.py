"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Any, Mapping, Callable

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import shutil
import logging
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from send2trash import send2trash

# * Gid Imports ----------------------------------------------------------------------------------------->


# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gid_tasks.project_info.project import Project

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]


THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class WorkspaceCleaner:
    default_settings: dict[str, Any] = {"folder_to_ignore": [".venv/", ".vscode/", ".git/", "tests/"],
                                        "files_to_ignore": ["pyproject.toml", "LICENSE", ".gitignore", ".gitattributes", ".editorconfig"],
                                        "to_clean": [],
                                        "dry_run": True}

    def __init__(self, base_folder: os.PathLike, settings: Mapping[str, Any] = None, log_func: Callable[[Any], None] = None) -> None:
        self.base_folder = Path(base_folder).resolve()
        self.settings = settings or {}
        self.log_func = log_func or print

    def get_folders_to_ignore_setting(self) -> set[str]:
        from_settings = self.settings.get("folder_to_ignore", [])
        return set(from_settings + self.default_settings.get("folder_to_ignore"))

    def get_files_to_ignore_setting(self) -> set[str]:
        from_settings = self.settings.get("files_to_ignore", [])
        return set(from_settings + self.default_settings.get("files_to_ignore"))

    def get_to_clean_setting(self) -> set[str]:
        from_settings = self.settings.get("to_clean", [])
        return set(from_settings + self.default_settings.get("to_clean"))

    def get_dry_run_setting(self) -> bool:
        return self.settings.get("dry_run", self.default_settings.get("dry_run"))

    def _check_if_to_clean(self, in_path: Path) -> bool:
        if any(in_path.match(p) for p in self.get_files_to_ignore_setting()):
            return False

        if any(in_path.match(p) for p in self.get_folders_to_ignore_setting()):
            return False

        if any(in_path.match(p) for p in self.get_to_clean_setting()):
            return True

        return False

    def _clean_file(self, in_file: Path) -> None:
        if self.get_dry_run_setting() is True:
            self.log_func("not deleting file %r because dry_run=True", in_file.as_posix())
        else:
            if in_file.exists() is False:
                return
            try:
                send2trash(in_file)
            except OSError:
                in_file.unlink(missing_ok=True)
            self.log_func("cleaned file %r", in_file.as_posix())

    def _clean_folder(self, in_folder: Path) -> Path:
        if self.get_dry_run_setting() is True:
            self.log_func("not deleting folder %r because dry_run=True", in_folder.as_posix())
        else:
            if in_folder.exists() is False:
                return
            try:
                send2trash(in_folder)
            except OSError:
                shutil.rmtree(in_folder)
                in_folder.unlink(True)
            self.log_func("cleaned folder %r", in_folder.as_posix())

    def clean(self) -> None:
        for dirname, folderlist, filelist in os.walk(self.base_folder, topdown=True):
            folderlist[:] = [p for p in folderlist if not any(Path(dirname, p).match(i) for i in self.get_folders_to_ignore_setting())]
            for file in filelist:
                file_path = Path(dirname, file)
                if self._check_if_to_clean(file_path) is True:
                    self._clean_file(file_path)
            for folder in folderlist:
                folder_path = Path(dirname, folder)
                if self._check_if_to_clean(folder_path) is True:
                    self._clean_folder(folder_path)
        self.log_func("finished cleaning %r (%r)", self.base_folder.name, self.base_folder.as_posix())


def clean_project(project: "Project") -> None:
    base_folder = project.base_folder
    settings = project.pyproject.get_gid_task_settings().get("workspace_cleaner", None)
    workspace_cleaner = WorkspaceCleaner(base_folder=base_folder, settings=settings)
    workspace_cleaner.clean()

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
