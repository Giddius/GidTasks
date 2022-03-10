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
from collections.abc import Iterable
from gidapptools.general_helper.string_helper import strip_only_wrapping_empty_lines
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def make_snippet_body(in_code_text: str, as_string: bool = True, pre_extra_lines: Iterable[str] = None, post_extra_lines: Iterable[str] = None) -> Union[list[str], str]:
    pre_extra_lines = list(pre_extra_lines) if pre_extra_lines is not None else []
    post_extra_lines = list(post_extra_lines) if post_extra_lines is not None else []
    snippet_body = pre_extra_lines + [l for l in strip_only_wrapping_empty_lines(in_code_text).splitlines()] + post_extra_lines
    if as_string is False:
        return snippet_body

    return json.dumps(snippet_body, sort_keys=False, indent=4, default=str)

# region[Main_Exec]


if __name__ == '__main__':
    a = """

try:
    from .misc import *
except ImportError:
    pass



    """
    print(make_snippet_body(a))
# endregion[Main_Exec]
