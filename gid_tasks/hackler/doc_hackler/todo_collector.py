"""
WiP.

Soon.
"""

# region [Imports]
from invoke import task
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
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader

from marshmallow import Schema, fields
from jinja2 import Environment, BaseLoader
from gid_tasks.hackler.doc_hackler.todo_templates import TEMPLATE_FILES
import pp

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


class PathField(fields.Field):
    default_error_messages = {
        "invalid": "Not a valid Path."}

    def _validate(self, value):
        if value is None:
            return None

        if isinstance(value, Path):
            return value

        if isinstance(value, str):
            return Path(value)

        self.make_error("invalid")

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):

        if value is None:
            return None

        return self._validate(value).as_posix()

    def _deserialize(self, value: Any, attr: Optional[str], data: Optional[Mapping[str, Any]], **kwargs):

        if value is None:
            return None
        if not isinstance(value, (str, bytes)):
            raise self.make_error("invalid")
        return self._validate(value)


class BaseTextReplacer:

    def __init__(self, project: "Project", regex: re.Pattern) -> None:
        self.project = project
        self.regex = regex

    def _sub_func(self, match: re.Match):
        return match.group()

    def make_link(self, link_text: str, path: Path, line_number: int = None) -> str:
        path = path.relative_to(self.project.base_folder)
        if line_number is not None:
            return f"[{link_text}]({path.as_posix()}#L{line_number})"
        return f"[{link_text}]({path.as_posix()})"

    def __call__(self, text: str) -> str:
        return self.regex.sub(self._sub_func, text)


class ClassLinkReplacer(BaseTextReplacer):

    def __init__(self, project: "Project") -> None:
        super().__init__(project=project, regex=re.compile(r"\$CLASS\-\>(?P<arg_text>[^\s]+)\$"))

    def _find_in_files(self, class_name: str) -> Optional[tuple[Path, int]]:
        for file in self.project.main_module.get_all_python_files():
            syntax_tree = ast.parse(file.read_text(encoding='utf-8', errors='ignore'), filename=str(file))
            for item in ast.walk(syntax_tree):
                if isinstance(item, ast.ClassDef):
                    if item.name == class_name:
                        return file, item.lineno

    def _sub_func(self, match: re.Match):
        class_name = match.group("arg_text")
        link_text = class_name
        if ":-:" in class_name:
            class_name, link_text = class_name.split(":-:")

        result = self._find_in_files(class_name=class_name)

        if result is None:
            return f"'{link_text}'"

        return self.make_link(link_text=link_text, path=result[0], line_number=result[1])


class ClassMethodLinkReplacer(BaseTextReplacer):
    def __init__(self, project: "Project") -> None:
        super().__init__(project, regex=re.compile(r"\$CLASSMETHOD\-\>(?P<arg_text>[^\s]+)\$"))

    def _find_in_files(self, class_name: str, method_name: str) -> Optional[tuple[Path, int]]:
        for file in self.project.main_module.get_all_python_files():
            # with file.open("r", encoding='utf-8', errors='ignore') as f:
            # for idx, line in enumerate(f):
            #     if search_term.search(line):
            #         return file, idx + 1
            syntax_tree = ast.parse(file.read_text(encoding='utf-8', errors='ignore'), filename=str(file))
            for item in ast.walk(syntax_tree):
                if isinstance(item, ast.ClassDef) and item.name == class_name:
                    for sub_item in ast.walk(item):
                        if isinstance(sub_item, ast.FunctionDef) and sub_item.name == method_name:
                            return file, sub_item.lineno

    def _sub_func(self, match: re.Match):
        method_name = match.group("arg_text")
        link_text = method_name
        if ":-:" in method_name:
            method_name, link_text = method_name.split(":-:")

        class_name, method_name = method_name.split('.')
        result = self._find_in_files(class_name=class_name, method_name=method_name)

        if result is None:
            return f"'{link_text}'"

        return self.make_link(link_text=link_text, path=result[0], line_number=result[1])


class BaseTodo(ABC):
    text_replace_vars: list[BaseTextReplacer] = []

    def __init__(self, identifier: str, text: str) -> None:
        self.identifier = identifier.casefold()
        self.raw_text = text

    @property
    @abstractmethod
    def schema(self):
        ...

    def _modify_text(self, raw_text: str) -> str:
        mod_text = raw_text
        for replacer in self.text_replace_vars:
            mod_text = replacer(mod_text)
        return mod_text

    @property
    def text(self):
        return self._modify_text(self.raw_text)

    def dump(self) -> str:

        return self.schema.dump(self)


class GeneralTodoSchema(Schema):
    identifier = fields.String()
    category = fields.String()
    text = fields.String()


class GeneralTodo(BaseTodo):
    __slots__ = ("identifier", "raw_text", "category")

    def __init__(self, identifier: str, text: str, category: str = "general") -> None:
        super().__init__(identifier=identifier, text=text)
        self.category = category.casefold()

    @property
    def schema(self):
        return GeneralTodoSchema()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier}, raw_text={self.raw_text!r}, category={self.category!r})"

    def dump(self) -> str:

        return self.schema.dump(self)


class FoundTodoSchema(Schema):
    identifier = fields.String()
    line_number = fields.Integer()
    text = fields.String()
    file_path = PathField()


class FoundTodo(BaseTodo):

    __slots__ = ("identifier", "file_path", "line_number", "raw_text")

    def __init__(self, identifier: str, file_path: Path, line_number: int, text: str) -> None:
        super().__init__(identifier=identifier, text=text)
        self.file_path = file_path
        self.line_number = line_number

    @property
    def schema(self):
        return FoundTodoSchema()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier},file_path={self.file_path.as_posix()!r}, line_number={self.line_number!r}, raw_text={self.raw_text!r})"

    def dump(self) -> str:

        return self.schema.dump(self)


class BaseTodoFinder:
    todo_pattern: str = r".*\#\s?{identifier}\s?\:\s?(?P<text>.*)"

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.regex = re.compile(str(self.todo_pattern).format(identifier=self.identifier), re.IGNORECASE)

    def find_in_file(self, in_file: Path):
        with in_file.open("r", encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f):
                if match := self.regex.match(line):
                    yield FoundTodo(self.identifier, in_file, idx + 1, match.group("text"))


class TodoCollection:

    def __init__(self, project_base_folder: Path, general_todo_data_file: Path) -> None:
        self.project_base_folder = project_base_folder
        self.general_todo_data_file = general_todo_data_file
        self.collected_todos: list[FoundTodo] = []

    @property
    def general_todo_data(self) -> list[GeneralTodo]:
        with self.general_todo_data_file.open("r", encoding='utf-8', errors='ignore') as f:
            raw_data = json.load(f)
        return [GeneralTodo(**i) for i in raw_data]

    @property
    def general_todo_categories(self) -> set[str]:
        return {item.category for item in self.general_todo_data}

    @property
    def general_todo_identifiers(self) -> set[str]:
        return {item.identifier for item in self.general_todo_data}

    @property
    def general_todo_by_identifier(self) -> dict[str, list[GeneralTodo]]:
        _out = defaultdict(list)
        for general_todo in self.general_todo_data:
            _out[general_todo.identifier].append(general_todo)

        for key in list(_out):
            _out[key] = sorted(_out[key], key=lambda x: x.category)
        return _out

    @property
    def found_todo_by_identifier(self) -> dict[str, list[FoundTodo]]:
        _out = defaultdict(list)
        for todo in self.collected_todos:
            _out[todo.identifier].append(todo)

        for key in list(_out):
            _out[key] = sorted(_out[key], key=lambda x: (x.file_path, x.line_number))
        return _out

    def add_todo(self, todo: FoundTodo):
        self.collected_todos.append(todo)

    def make_todo_paths_relative_to(self, base_path: Path):
        for todo in self.collected_todos:
            todo.file_path = todo.file_path.relative_to(base_path)


class AbstractTodoRenderer(ABC):

    @classmethod
    @property
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def render(self, project: "Project", todo_collection: TodoCollection, **kwargs) -> str:
        ...


class JinjaTodoRenderer(AbstractTodoRenderer):

    def __init__(self, template_file: Path) -> None:
        super().__init__()
        self.template_file = template_file
        self.jinja_env = Environment(loader=BaseLoader)

    def render(self, project: "Project", todo_collection: TodoCollection, **kwargs) -> str:
        template_string = self.template_file.read_text(encoding='utf-8', errors='ignore')
        return self.jinja_env.from_string(template_string).render(project_data=project.general_project_data, todo_data=todo_collection, **kwargs)


class TodoCollector:
    def __init__(self,
                 project: "Project",
                 identifiers: Iterable[str],
                 general_todo_data_file: Path = None,
                 output_file: Path = None,
                 renderer: AbstractTodoRenderer = JinjaTodoRenderer(TEMPLATE_FILES["basic_template"])) -> None:
        self.project = project
        self.identifiers = tuple(identifiers)
        self._general_todo_data_file = general_todo_data_file
        self._output_file = output_file
        self.renderer = renderer
        BaseTodo.text_replace_vars.append(ClassLinkReplacer(self.project))
        BaseTodo.text_replace_vars.append(ClassMethodLinkReplacer(self.project))
        self.finders = [BaseTodoFinder(i) for i in identifiers]
        self.todo_data = TodoCollection(self.project.base_folder, self.general_todo_data_file)

    @property
    def general_todo_data_file(self) -> Path:
        if self._general_todo_data_file is not None:
            return self._general_todo_data_file
        return self.project.general_todo_data_file

    @property
    def output_file(self) -> Path:
        if self._output_file is not None:
            return self._output_file
        return self.project.todo_text_file

    def collect(self):
        for file in self.project.main_module.get_all_python_files(extra_excludes=["*_resources.py"]):
            for finder in self.finders:
                for result in finder.find_in_file(file):
                    self.todo_data.add_todo(result)

    def render(self) -> str:
        return self.renderer.render(project=self.project, todo_collection=self.todo_data)

    def create(self):
        self.todo_data.make_todo_paths_relative_to(self.project.base_folder)
        with self.output_file.open("w", encoding='utf-8', errors='ignore') as f:
            f.write(self.render())


def full_path(in_path):
    return str(Path(in_path).resolve())


@task(name="todo", iterable=["identifier"])
def todo_task(c, identifier):
    in_identifier = []
    for iden in identifier:
        in_identifier += iden.split(',')
    identifier = {"TODO", "IDEA"}.union({i.upper() for i in in_identifier})
    c.console.print(identifier)
    c.console.rule()
    todo_hackler = TodoCollector(c.project, identifier)
    todo_hackler.collect()
    c.console.print("collected todos:")
    c.console.print(todo_hackler.todo_data.collected_todos)
    todo_hackler.create()


    # region[Main_Exec]
if __name__ == '__main__':
    pass


# endregion[Main_Exec]
