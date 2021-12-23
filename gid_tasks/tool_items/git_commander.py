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


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractCommand(ABC):
    shell: bool = False
    check: bool = False

    @property
    @abstractmethod
    def args(self):
        ...

    def handle_error(self, result: subprocess.CompletedProcess):
        result.check_returncode()


class AddCommand(AbstractCommand):

    @property
    def args(self):
        return "git add ."


class CommitCommand(AbstractCommand):

    def __init__(self, message: str) -> None:
        self.message = message

    @property
    def args(self):
        return f'git commit -am "{self.message}"'


class PushCommand(AbstractCommand):

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    @property
    def args(self):
        args = "git push"
        if self.dry_run is True:
            args += ' --dry-run'
        return args


class GitCommander:

    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd

    def run_command(self, command: AbstractCommand):
        result = subprocess.run(args=command.args, shell=command.shell, check=command.check, cwd=self.cwd, text=True)
        if result.returncode != 0:
            command.handle_error(result)

# region[Main_Exec]


if __name__ == '__main__':
    x = GitCommander(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidTasks").resolve())
    x.run_command(AddCommand())
    x.run_command(CommitCommand("something2"))
    x.run_command(PushCommand(True))

# endregion[Main_Exec]
