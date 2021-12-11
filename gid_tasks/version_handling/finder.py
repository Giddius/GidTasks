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
from gid_tasks.version_handling.version_item import Version, get_specific_version
from gid_tasks.utility.enums import PipManager
from gid_tasks.errors import VersionNotFoundError
if TYPE_CHECKING:
    from gid_tasks.project_info.project import Project, MainModule
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

VERSION_PARTS_REGEX_PATTERN = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>[\drc]+)\.?(?P<extra>post\d)?"


VERSION_REGEXES = {PipManager.FLIT: re.compile(r"^\_\_version\_\_\s?\=\s?" + '\"?' + VERSION_PARTS_REGEX_PATTERN + '\"?', re.MULTILINE)}


class VersionFinder:

    def __init__(self, pip_manager: "PipManager", main_module: "MainModule") -> None:
        self.pip_manager = pip_manager
        self.regex = VERSION_REGEXES[self.pip_manager]
        self.main_module = main_module
        self.version: Version = None

    def _search_file(self, in_file: Path) -> bool:
        with in_file.open('r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                if version_match := self.regex.match(line.strip()):

                    self.version = get_specific_version(pip_manager=self.pip_manager, **version_match.groupdict(), file=in_file, line_number=line_num)
                    return True
        return False

    def find_version(self, force: bool = False) -> "Version":
        if self.version is not None and force is False:
            return self.version
        for file in self.main_module.get_all_python_files():
            if self._search_file(file) is True:
                return self.version
        raise VersionNotFoundError(f"Unable to find a file with the specific Version indicator for {self.pip_manager.name!r}.")

# region[Main_Exec]


if __name__ == '__main__':
    print(os.getenv("TESTING_SITE_CUSTOMIZE", "0"))


# endregion[Main_Exec]
