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
