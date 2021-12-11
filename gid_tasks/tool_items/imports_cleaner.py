"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from gid_tasks.errors import IsFolderError, WrongFileTypeError
import attr
import isort
import autopep8
import autoflake
from gidapptools import get_logger
if TYPE_CHECKING:
    from gid_tasks.project_info.toml import PyProjectTomlFile
    from gid_tasks.project_info.project import Project
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


@attr.s(auto_detect=True, auto_attribs=True, slots=True)
class ImportSectionParts:
    start_line: str = attr.ib(converter=lambda x: x.strip())
    end_line: str = attr.ib(converter=lambda x: x.strip())
    content: str = attr.ib(converter=lambda x: x.strip())
    start_pos: int = attr.ib()
    end_pos: int = attr.ib()


class _ImportsCleanerTargetFile:

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
            return self.imports_region_regex.sub(rf"\g<start_line>\n{self.import_section_parts.content}\g<end_line>", self.content)
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
        wrapped_file = _ImportsCleanerTargetFile(path=file, imports_region_regex=self.import_region_regex)
        if self.use_autoflake is True:
            wrapped_file = self._apply_autoflake(wrapped_file=wrapped_file)
        if self.use_isort is True:
            wrapped_file = self._apply_isort(wrapped_file=wrapped_file)
        if self.use_autopep8 is True:
            wrapped_file = self._apply_autopep8(wrapped_file=wrapped_file)
        wrapped_file.write()
        return file

    def __call__(self, file: Path) -> Optional[Path]:
        return self.clean_file(file=file)


def import_clean_project(project: "Project"):
    import_cleaner = ImportsCleaner.from_pyproject_toml(project.pyproject)
    for file in project.main_module.get_all_python_files(exclude_init=import_cleaner.exclude_init_files, extra_excludes=import_cleaner.exclude_globs):
        _file = import_cleaner.clean_file(file=file)
        log.info("cleaned imports of file %r", _file.as_posix())
# region[Main_Exec]


if __name__ == '__main__':
    from gid_tasks.project_info.project import Project
    x = Project()
    y = ImportsCleaner.from_pyproject_toml(x.pyproject)
    y(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidTasks\gid_tasks\project_info\toml.py"))
# endregion[Main_Exec]
