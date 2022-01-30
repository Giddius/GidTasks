"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Union, Callable, Optional, Any, Iterable

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from pathlib import Path
from functools import cached_property
import re
# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.errors import IsFolderError, AmbigousBaseFolderError
from gid_tasks.utility.misc import main_dir_from_git, find_main_dir_by_pyproject_location
from gid_tasks.utility.enums import PipManager
from gid_tasks.project_info.toml import PyProjectTomlFile
from gid_tasks.version_handling.finder import VersionFinder
from gidapptools.general_helper.path_helper import change_cwd
from gid_tasks.project_info.main_module_item import MainModule

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.types import PATH_TYPE
    from gid_tasks.version_handling.version_item import Version

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

DEFAULT_EMPTY_JSON_TYPUS: Union[type[dict], type[list]] = list


def _create_empty_json_file(in_file: Path, typus: Union[type[dict], type[list]] = DEFAULT_EMPTY_JSON_TYPUS) -> Path:
    with in_file.open('w', encoding='utf-8', errors='ignore') as f:
        json.dump(typus(), f, indent=4, sort_keys=False)
    return in_file


SPECIAL_CREATE_FILE_CASES: dict[str, Callable] = {'.json': _create_empty_json_file}


def create_empty_file(in_file: Path) -> Path:
    special_case = SPECIAL_CREATE_FILE_CASES.get(in_file.suffix.casefold(), None)
    if special_case is not None:
        return special_case(in_file=in_file)
    in_file.touch()
    return in_file


def check_file_exists(in_file: Path, create_if_missing: bool = False) -> bool:
    if in_file.exists() is False:
        if create_if_missing is True:
            create_empty_file(in_file)
            return True
        return False
    if in_file.is_file() is False:
        raise IsFolderError(in_file)
    return True


# def default_basefolder_finder(cwd: "PATH_TYPE") -> Path:
#     base_folder = None
#     with change_cwd(target_cwd=cwd):
#         git_main_dir = main_dir_from_git().resolve()
#         check_main_dir = find_main_dir_by_pyproject_location().resolve()
#         if git_main_dir == check_main_dir:
#             base_folder = git_main_dir
#     if base_folder:
#         return base_folder
#     raise AmbigousBaseFolderError(git_main_dir, check_main_dir)


def default_basefolder_finder(cwd: "PATH_TYPE") -> Path:
    with change_cwd(target_cwd=cwd):
        base_folder = find_main_dir_by_pyproject_location().resolve()

    if base_folder:
        return base_folder
    raise FileNotFoundError(f"Unable to find a 'pyproject.toml' file in {cwd.as_posix()!r} or any parent folder.")


class ProjectPaths:
    global_scripts: dict[str, Path] = {}

    def __init__(self, base_folder: Path) -> None:
        self.base_folder = base_folder
        self.venv = self.base_folder.joinpath(".venv")
        self.vscode = self.base_folder.joinpath(".vscode")
        self.tools = self.base_folder.joinpath("tools")
        self.docs = self.base_folder.joinpath("docs")
        self.misc = self.base_folder.joinpath("misc")
        self.temp = self.base_folder.joinpath("temp")
        self.dist = self.base_folder.joinpath("dist")

        self._scripts = self._collect_scripts()

    def _collect_scripts(self) -> dict[str, Path]:
        scripts = self.global_scripts.copy()
        scripts_folder = self.venv.joinpath("Scripts")
        if scripts_folder.exists() is False:
            return scripts
        scripts["activate"] = scripts_folder.joinpath("activate.bat")
        for file in sorted(scripts_folder.iterdir(), key=lambda x: len(x.name)):
            if file.is_file() and file.stem.casefold() not in {"activate"}:
                scripts[file.stem.casefold()] = file
        return scripts


class Project:
    extra_folder: dict[str, Path] = {}
    extra_files: dict[str, Path] = {}

    def __init__(self,
                 pip_manager: PipManager = None,
                 cwd: "PATH_TYPE" = None,
                 project_paths_class: type[ProjectPaths] = ProjectPaths) -> None:

        self.cwd = Path.cwd() if cwd is None else Path(cwd)
        self.base_folder = Path(default_basefolder_finder(self.cwd))

        self.pyproject = PyProjectTomlFile(self._get_pyproject_file())
        self.main_module_name = self.pyproject.package_name
        self.main_module = self._get_main_module()
        self.pip_manager = self._determine_pip_manager() if pip_manager is None else pip_manager

        self.version = VersionFinder(self.pip_manager, self.main_module).find_version()

        self.paths = project_paths_class(self.base_folder)

    @cached_property
    def general_project_data(self) -> dict[str, Any]:
        def _determine_license_type(in_license_file: Path):
            with in_license_file.open("r", encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
            if "MIT" in first_line:
                return "MIT"
            raise RuntimeError(f"Unknown License type for license file: {in_license_file.as_posix()!r}.")

        def _format_dependencies(in_dependencies: Iterable[str]) -> list[dict[str, Any]]:
            split_regex = re.compile(r"((\=\=)|(\>\=)|(\<\=)|(\~\=))")
            _out = []
            for raw_dep in in_dependencies:
                if match := split_regex.search(raw_dep):
                    name, version = raw_dep.split(match.group())
                else:
                    name = raw_dep
                    version = None
                _out.append({"name": name, "version": version})
            return _out
        data = {}
        project_data = self.pyproject.get_project_data()

        data["name"] = project_data["name"]
        data["authors"] = list(project_data["authors"])
        data["links"] = dict(project_data["urls"])

        license_file = self.base_folder.joinpath(project_data["license"]["file"])
        data["license"] = {"file": license_file, "type": _determine_license_type(license_file)}

        data["version"] = self.version
        data['requires-python'] = project_data['requires-python']
        data["script_names"] = list(project_data["scripts"])
        data["dependencies"] = _format_dependencies(project_data["dependencies"])
        return data

    @property
    def general_todo_data_file(self) -> Path:
        raw = self.paths.docs.joinpath("docs_data", "general_todo_data.json")
        raw.parent.mkdir(parents=True, exist_ok=True)
        if raw.exists() is False:
            raw.write_text("[]", encoding='utf-8', errors='ignore')
        return raw

    @property
    def todo_text_file(self) -> Path:
        raw = self.paths.base_folder.joinpath("TODO.md")
        raw.parent.mkdir(parents=True, exist_ok=True)
        return raw

    def _determine_pip_manager(self) -> PipManager:
        all_keys = set(self.pyproject.all_keys)
        if "flit" in all_keys:
            return PipManager.FLIT
        if "poetry" in all_keys:
            return PipManager.POETRY

        build_backend = self.pyproject.get_from_key_path(["build-system", "build-backend"])
        if str(build_backend).startswith("flit_core"):
            return PipManager.FLIT
        if str(build_backend).startswith("poetry"):
            return PipManager.POETRY

    def _get_pyproject_file(self) -> Optional[Path]:
        pyproject_file_path = self.base_folder.joinpath("pyproject.toml")
        if check_file_exists(pyproject_file_path) is False:
            return
        return pyproject_file_path

    def _get_main_module(self) -> "MainModule":
        return MainModule(base_folder=self.base_folder.joinpath(self.main_module_name).resolve(), pyproject_data=self.pyproject)

    def set_version(self, new_version: "Version") -> "Project":
        self.version = new_version
        self.version.write_version()
        return self

        # region[Main_Exec]


if __name__ == '__main__':
    x = Project()

    print(x.version)


# endregion[Main_Exec]
