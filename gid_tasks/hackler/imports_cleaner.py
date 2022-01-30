"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Any, Mapping, Optional, Iterable
from invoke import task
# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import attr
import isort
import autopep8
import autoflake

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools import get_logger
from gid_tasks.project_info.project import Project
from gidapptools.general_helper.hashing import file_hash

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
log = get_logger(__name__)
# endregion[Constants]

# autoflake settings defaults

# additional_imports = None
# expand_star_imports = true
# remove_all_unused_imports = true
# remove_duplicate_keys = false
# remove_unused_variables = false
# ignore_init_module_imports = true


def _clean_import_content(raw_content: str):
    cleaned_lines = (line for line in raw_content.splitlines() if line.strip() != "" and not line.strip().startswith('#'))
    return '\n'.join(cleaned_lines).strip()


@attr.s(auto_detect=True, auto_attribs=True, slots=True)
class ImportSectionParts:
    start_line: str = attr.ib(converter=lambda x: x.strip())
    end_line: str = attr.ib(converter=lambda x: x.strip())
    content: str = attr.ib(converter=_clean_import_content)
    start_pos: int = attr.ib()
    end_pos: int = attr.ib()


class _ImportsCleanerTargetFile:
    type_checking_import_header_comment: str = "# * Type-Checking Imports --------------------------------------------------------------------------------->"

    def __init__(self, path: Path, imports_region_regex: re.Pattern) -> None:
        self.path = path
        self.imports_region_regex = imports_region_regex
        self.content: str = self.path.read_text(encoding='utf-8', errors='ignore')
        self._has_no_imports_region: bool = None
        self._import_section_parts: ImportSectionParts = None

    @property
    def import_section_parts(self) -> Optional[ImportSectionParts]:
        if self._import_section_parts is None and self._has_no_imports_region is None:
            self._collect_imports_part()
        return self._import_section_parts

    @property
    def has_no_imports_region(self) -> bool:
        if self._has_no_imports_region is None:
            self._collect_imports_part()
        return self._has_no_imports_region

    def _collect_imports_part(self):
        if match := self.imports_region_regex.search(self.content):
            self._import_section_parts = ImportSectionParts(**match.groupdict(), start_pos=match.start("start_line"), end_pos=match.end("end_line"))
            self._has_no_imports_region = False
        else:
            self._has_no_imports_region = True

    def _new_content(self) -> str:
        if self.has_no_imports_region is False:
            new_content = self.imports_region_regex.sub(rf"\g<start_line>\n{self.import_section_parts.content}\g<end_line>", self.content)
            new_content = new_content.replace("if TYPE_CHECKING:", self.type_checking_import_header_comment + '\nif TYPE_CHECKING:', 1)
            return new_content
        return self.content

    def write(self) -> None:
        self.path.write_text(self._new_content(), encoding='utf-8', errors='ignore')


class ImportsCleaner:
    default_settings: dict[str, Any] = {"import_region_name": "Imports",
                                        "use_autoflake": True,
                                        "use_isort": True,
                                        "use_autopep8": True,
                                        "exclude_init_files": True,
                                        "ignore_missing_import_section": True,
                                        "exclude_globs": []}
    import_region_regex_pattern = (r"""
                                    (?P<start_line>\#\s*region\s*\[{import_region_name}\]\n?)
                                    (?P<content>.*?)
                                    (?P<end_line>\n\#\s*endregion\s*\[{import_region_name}\]\n?)
                                    """, re.IGNORECASE | re.DOTALL | re.VERBOSE)

    def __init__(self,
                 settings: Mapping[str, Any],
                 autoflake_settings: Mapping[str, Any],
                 isort_settings: Mapping[str, Any],
                 autopep8_settings: Mapping[str, Any]) -> None:
        self.settings = settings
        self.autoflake_settings = autoflake_settings
        self.isort_settings = isort_settings
        self.autopep8_settings = autopep8_settings

        self.import_region_name = self._get_setting_value("import_region_name")
        self.import_region_regex = re.compile(self.import_region_regex_pattern[0].format(import_region_name=self.import_region_name), self.import_region_regex_pattern[1])

    @classmethod
    def from_pyproject_toml(cls, pyproject_toml: "PyProjectTomlFile") -> "ImportsCleaner":
        return cls(settings=pyproject_toml.get_gid_task_settings(default={}).get("imports_cleaner", {}),
                   autoflake_settings=pyproject_toml.get_autoflake_settings(default={}),
                   isort_settings=pyproject_toml.get_isort_settings(default={}),
                   autopep8_settings=pyproject_toml.get_autopep8_settings(default={}))

    def _get_setting_value(self, key: str) -> Any:
        return self.settings.get(key, self.default_settings[key])

    @property
    def exclude_globs(self) -> list[str]:
        return self._get_setting_value("exclude_globs")

    @property
    def use_autoflake(self) -> bool:
        return self._get_setting_value("use_autoflake")

    @property
    def use_isort(self) -> bool:
        return self._get_setting_value("use_isort")

    @property
    def use_autopep8(self) -> bool:
        return self._get_setting_value("use_autopep8")

    @property
    def exclude_init_files(self) -> bool:
        return self._get_setting_value("exclude_init_files")

    def _validate_file(self, in_file: Path) -> bool:
        if in_file.is_file() is False:
            return False
        if in_file.suffix != ".py":
            return False
        if self.exclude_init_files is True and in_file.stem == "__init__":
            return False
        if any(in_file.match(excludes) for excludes in self.exclude_globs):
            return False
        return True

    def _apply_autoflake(self, wrapped_file: _ImportsCleanerTargetFile) -> _ImportsCleanerTargetFile:
        new_content = autoflake.fix_code(wrapped_file.content, **self.autoflake_settings)
        wrapped_file.content = new_content
        return wrapped_file

    def _apply_isort(self, wrapped_file: _ImportsCleanerTargetFile) -> _ImportsCleanerTargetFile:
        if wrapped_file.has_no_imports_region is False:
            new_import_section_content = isort.code(code=wrapped_file.import_section_parts.content, **self.isort_settings)
            wrapped_file.import_section_parts.content = new_import_section_content
        else:
            if self._get_setting_value("ignore_missing_import_section") is True:
                new_content = isort.code(code=wrapped_file.content, **self.isort_settings)
                wrapped_file.content = new_content
        return wrapped_file

    def _apply_autopep8(self, wrapped_file: _ImportsCleanerTargetFile) -> _ImportsCleanerTargetFile:
        if wrapped_file.has_no_imports_region is False:
            new_import_section_content = autopep8.fix_code(wrapped_file.import_section_parts.content, options=self.autopep8_settings)
            wrapped_file.import_section_parts.content = new_import_section_content
        else:
            if self._get_setting_value("ignore_missing_import_section") is True:
                new_content = autopep8.fix_code(wrapped_file.content, options=self.autopep8_settings)
                wrapped_file.content = new_content
        return wrapped_file

    def clean_file(self, file: Path) -> Optional[Path]:
        if self._validate_file(in_file=file) is False:
            return
        if all(i is False for i in (self.use_autoflake, self.use_autopep8, self.use_isort)):
            return
        old_hash = file_hash(file)
        wrapped_file = _ImportsCleanerTargetFile(path=file, imports_region_regex=self.import_region_regex)
        if self.use_autoflake is True:
            wrapped_file = self._apply_autoflake(wrapped_file=wrapped_file)
        if self.use_isort is True:
            wrapped_file = self._apply_isort(wrapped_file=wrapped_file)
        if self.use_autopep8 is True:
            wrapped_file = self._apply_autopep8(wrapped_file=wrapped_file)
        wrapped_file.write()
        if old_hash == file_hash(file):
            return
        return file

    def __call__(self, file: Path) -> Optional[Path]:
        return self.clean_file(file=file)


def import_clean_project(project: "Project"):
    import_cleaner = ImportsCleaner.from_pyproject_toml(project.pyproject)
    for file in project.main_module.get_all_python_files(exclude_init=import_cleaner.exclude_init_files, extra_excludes=import_cleaner.exclude_globs):
        _file = import_cleaner.clean_file(file=file)
        if _file is not None:
            yield _file


@task(name="clean_imports")
def clean_imports_task(c):
    for cleaned_file in import_clean_project(c.project):
        c.console.print(f"cleaned file -> {cleaned_file.as_posix()!r}")
# region[Main_Exec]


if __name__ == '__main__':
    p = Project(base_folder=Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_Logbook"))
    import_clean_project(p, exclude={"sqf_syntax_data.py", "antistasi_logbook_resources.py"})
# endregion[Main_Exec]
