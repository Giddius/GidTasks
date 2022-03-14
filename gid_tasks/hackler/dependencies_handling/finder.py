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
import pp

import ast
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
from importlib import import_module, invalidate_caches, metadata
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict, UserList
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader

import attr

from gidapptools.utility_classes import VersionItem
from yarl import URL

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@attr.s(slots=True, weakref_slot=True)
class Dependency:
    import_name: str = attr.ib()
    distribution_name: str = attr.ib()
    version: VersionItem = attr.ib()
    url: URL = attr.ib(default=None)
    files: set[Path] = attr.ib(factory=set, converter=set)

    def combine(self, other_dependecy: "Dependency") -> None:
        for file in other_dependecy.files:
            self.files.add(file)

    def serialize(self) -> dict[str, Any]:
        def _value_serializer(inst: type, field: attr.Attribute, value: Any) -> Any:
            try:
                match field.name:
                    case "version":
                        return str(value)
                    case "url":
                        return value.human_repr()
                    case "files":
                        return [f.as_posix() for f in value]
                    case _:
                        return value
            except AttributeError:
                return value
        return attr.asdict(self, recurse=False, value_serializer=_value_serializer)


class FoundDependencies(UserList):

    def __init__(self) -> None:
        self.data: list[Dependency] = []

    @ property
    def by_name_data(self) -> dict[str, Dependency]:
        import_name_data = {d.import_name: d for d in self}
        distribution_name_data = {d.distribution_name: d for d in self}
        return import_name_data | distribution_name_data

    def get_by_name(self, name: str) -> Optional[Dependency]:
        return self.by_name_data.get(name, None)

    def add(self, dependency: Dependency) -> None:
        existing_item = self.get_by_name(dependency.import_name)
        if existing_item is not None:
            existing_item.combine(dependency)

        else:
            super().append(dependency)

    def append(self, item: Dependency) -> None:
        self.add(item)

    def serialize(self) -> list[dict[str, Any]]:
        return [item.serialize() for item in self]


class AstImportVisitor(ast.NodeVisitor):

    def __init__(self, file: Path) -> None:
        self.file = file
        self.found: list[Dependency] = []
        self.errored: list[str] = []

    @ cached_property
    def distribution_map(self) -> dict[str, metadata.Distribution]:
        _out = {}
        for dist in metadata.distributions():
            top_level_content = dist.read_text('top_level.txt')
            if top_level_content is not None:
                for imp_name in top_level_content.split():
                    _out[imp_name] = dist
            else:
                _out[dist.name] = dist
        return _out

    def _is_valid_name(self, name: str) -> bool:
        if name is None:
            return False
        if name in sys.stdlib_module_names:
            return False
        if name.split(".")[0] in sys.stdlib_module_names:
            return False
        return True

    def _create_dependecy_item(self, name: str) -> Dependency:
        try:
            import_name = name if "." not in name else name.split(".")[0]
            _distribution = self.distribution_map[import_name]
            distribution_name = _distribution.name
            version = VersionItem.from_string(_distribution.version)
            url = _distribution.metadata["Project-URL"] or _distribution.metadata["Home-page"]
            if url is not None:
                url = URL(url.split()[-1])
            return Dependency(import_name=import_name, distribution_name=distribution_name, version=version, url=url, files=[self.file])
        except Exception as e:
            self.errored.append((name, e))

    def visit_Import(self, node: ast.Import) -> Any:
        for item in node.names:
            name = item.name
            if not self._is_valid_name(name):
                continue
            dep = self._create_dependecy_item(name)
            if dep is not None:
                self.found.append(dep)

        return self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        name = node.module
        if node.level == 0 and self._is_valid_name(name):
            dep = self._create_dependecy_item(name)
            if dep is not None:
                self.found.append(dep)

        return self.generic_visit(node)


class DependencyFinder:

    def __init__(self, main_package_name: str = None) -> None:
        self.main_package_name = main_package_name
        self.found_dependencies: FoundDependencies[Dependency] = FoundDependencies()
        self.errored_names: set[str] = set()

    def search_file(self, in_file: os.PathLike):
        in_file = Path(in_file).resolve()
        ast_tree = ast.parse(in_file.read_text(encoding='utf-8', errors='ignore'))
        visitor = AstImportVisitor(in_file)
        visitor.visit(ast_tree)
        for dependency in visitor.found:
            if self.main_package_name is not None and dependency.distribution_name != self.main_package_name:
                self.found_dependencies.add(dependency)
        for errored in visitor.errored:
            self.errored_names.add(errored)


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
