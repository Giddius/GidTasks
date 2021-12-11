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
import pp
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
from gid_tasks.utility.misc import main_dir_from_git, find_main_dir_by_pyproject_location
import attr
from gid_tasks.errors import IsFolderError, AmbigousBaseFolderError
from gid_tasks.project_info.toml import PyProjectTomlFile
from gidapptools.general_helper.path_helper import change_cwd
from importlib.metadata import metadata
from gid_tasks.project_info.main_module_item import MainModule
from gid_tasks.utility.enums import PipManager
from gid_tasks.version_handling.finder import VersionFinder
if TYPE_CHECKING:
    from gidapptools.types import PATH_TYPE
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


def default_basefolder_finder(cwd: "PATH_TYPE") -> Path:
    with change_cwd(target_cwd=cwd):
        git_main_dir = main_dir_from_git().resolve()
        check_main_dir = find_main_dir_by_pyproject_location().resolve()
        if git_main_dir == check_main_dir:
            return git_main_dir
    raise AmbigousBaseFolderError(git_main_dir, check_main_dir)


class Project:

    def __init__(self,
                 pip_manager: PipManager = None,
                 base_folder: Union[Path, str, Callable[["PATH_TYPE"], Path]] = default_basefolder_finder,
                 create_missing_files: bool = False,
                 cwd: "PATH_TYPE" = None,
                 main_module_name: str = None) -> None:

        self.cwd = Path.cwd() if cwd is None else Path(cwd)

        self.base_folder = Path(base_folder) if not callable(base_folder) else Path(base_folder(self.cwd))
        self.create_missing_files = create_missing_files
        self.standard_folder = {"tools": self.base_folder.joinpath("tools"),
                                "test": self.base_folder.joinpath("tests"),
                                "temp": self.base_folder.joinpath("temp"),
                                "misc": self.base_folder.joinpath("misc"),
                                "docs": self.base_folder.joinpath("docs"),
                                "vscode": self.base_folder.joinpath(".vscode"),
                                "venv": self.base_folder.joinpath(".venv")}

        self.standard_files = {"pyproject_toml": self.base_folder.joinpath("pyproject.toml"),
                               "license": self.base_folder.joinpath("license"),
                               "readme": self.base_folder.joinpath("readme.md"),
                               "tasks": self.base_folder.joinpath("tasks.py"),
                               "gitignore": self.base_folder.joinpath(".gitignore"),
                               "gitattributes": self.base_folder.joinpath(".gitattributes"),
                               "editorconfig": self.base_folder.joinpath(".editorconfig")}
        self.pyproject = PyProjectTomlFile(self._get_pyproject_file())
        self.main_module_name = self.pyproject.package_name if main_module_name is None else main_module_name
        self.main_module = self._get_main_module()
        self.pip_manager = self._determine_pip_manager() if pip_manager is None else pip_manager
        if self.pip_manager is None:
            self.version = None
        else:
            self.version = VersionFinder(self.pip_manager, self.main_module).find_version()

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
        pyproject_file_path = self.standard_files["pyproject_toml"].resolve()
        if check_file_exists(pyproject_file_path, create_if_missing=self.create_missing_files) is False:
            return
        return pyproject_file_path

    def _get_main_module(self) -> "MainModule":
        return MainModule(base_folder=self.base_folder.joinpath(self.main_module_name).resolve(), pyproject_data=self.pyproject)

# region[Main_Exec]


if __name__ == '__main__':
    x = Project()

    print(Path(x.main_module))


# endregion[Main_Exec]