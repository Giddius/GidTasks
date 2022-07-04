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
from gid_tasks.project_info.vscode_objects import VSCodeTask, VSCodeTaskOptions, VSCodeTaskRunOptions, VSCodeTaskPresentation, VSCodeVariables, VSCodeTaskInput
import invoke
from invoke.parser.context import ParserContext
from gid_tasks.utility.enums import Sentinel
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


class GidTask(invoke.Task):
    _task_marker: str = "INVTASK"

    def __init__(self,
                 body: Callable[..., Any],
                 name: str = None,
                 aliases: tuple[str] = (),
                 positional: Iterable[str] | None = None,
                 optional: Iterable[str] = (),
                 default: bool = False,
                 auto_shortflags: bool = True,
                 help: dict[str, str] | None = None,
                 pre: Iterable[invoke.Task] | None = None,
                 post: Iterable[invoke.Task] | None = None,
                 autoprint: bool = False,
                 iterable: Iterable[str] | None = None,
                 incrementable: Iterable[str] | None = None,
                 project: "Project" = None,
                 add_to_vscode_tasks: bool = False,
                 pretty_name: str = None) -> None:
        super().__init__(body=body,
                         name=name,
                         aliases=aliases,
                         positional=positional,
                         optional=optional,
                         default=default,
                         auto_shortflags=auto_shortflags,
                         help=help,
                         pre=pre,
                         post=post,
                         autoprint=autoprint,
                         iterable=iterable,
                         incrementable=incrementable)
        self.project = project
        self.add_to_vscode_tasks = add_to_vscode_tasks
        self._pretty_name = pretty_name

    @property
    def converted_name(self) -> str:
        return self.name.replace("_", "-")

    @property
    def pretty_name(self) -> str:
        if self._pretty_name is not None:
            return self._pretty_name
        return self.name.replace("_", " ").replace("-", " ").title()

    @property
    def vscode_task_name(self) -> str:
        return ' '.join([self.task_name_prefix, self.pretty_name])

    @property
    def vscode_task_detail(self) -> str:
        marker = self._task_marker.upper()
        description = self.help or ""
        return f"<{marker}> {description}".strip()

    def to_vscode_task_object(self) -> VSCodeTask:
        options = VSCodeTaskOptions(cwd="${workspaceFolder}")
        presentation = VSCodeTaskPresentation(echo=True, reveal="always", focus=False, panel="shared", showReuseMessage=False, clear=False)
        args = self.get_args_for_vscode()
        if not args:
            converted_args = Sentinel.MISSING
        else:
            converted_args = []
            for arg in args:
                if isinstance(arg, VSCodeTaskInput):
                    arg = arg.as_variable
                converted_args.append(arg)

        return VSCodeTask(label=self.pretty_name,
                          detail=self.vscode_task_detail,
                          type="shell",
                          command=f"{VSCodeVariables.WORKSPACE_FOLDER}\\.venv\\scripts\\invoke.exe {self.converted_name}",
                          options=options,
                          args=converted_args,
                          presentation=presentation)

    def get_args_for_vscode(self, only_input_args: bool = False) -> list[Union[str, VSCodeTaskInput]]:
        cc = ParserContext(self.name)
        _out = []
        for arg in self.get_arguments():
            cc.add_arg(arg)
            try:
                flag_name = f"--{arg.name}"
                h = cc.help_for(flag_name)[0]
            except Exception as e:
                h = arg.help or ""
            name = f"<{self._task_marker.upper()}>_{self.name}_{arg.name}_input".strip()
            typus = "promptString"
            description = h
            default = arg.default or Sentinel.MISSING
            if arg.nicknames and only_input_args is False:
                _out.append(f"-{arg.nicknames[0]}")

            _out.append(VSCodeTaskInput(name=name, typus=typus, description=description, default=default))
        return _out


def task(*args, **kwargs) -> GidTask:
    if kwargs.get("klass", None) is None:
        kwargs["klass"] = GidTask

    return invoke.task(*args, **kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
