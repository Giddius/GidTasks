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

from gid_tasks.version_handling.finder import VersionFinder
if TYPE_CHECKING:
    from gid_tasks.utility.enums import PipManager
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
