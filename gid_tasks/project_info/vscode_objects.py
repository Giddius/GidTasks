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

from pprint import pprint
import attrs
import attrs.converters

from gid_tasks.utility.enums import Sentinel

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class FILE_CLASSES_TYPE(TypedDict):
    workspace: type["BaseVSCodeFile"]
    settings: type["BaseCreateableVSCodeFile"]
    tasks: type["BaseCreateableVSCodeFile"]
    # launch: type["BaseCreateableVSCodeFile"]
    # snippets: type["BaseCreateableVSCodeFile"]


class BaseVSCodeFile(ABC):

    def __init__(self, file_path: Union[str, os.PathLike]) -> None:
        self._path = Path(file_path)
        self._raw_content: dict[str, Any] | None = None

    def _load_content(self) -> None:
        self._raw_content = self.get_content()

    def load_content(self) -> "BaseVSCodeFile":
        self._load_content()
        return self

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self.path.stem

    def exists(self) -> bool:
        return self.path.exists()

    @classmethod
    @abstractmethod
    def check_file(cls, in_file: Path) -> bool:
        ...

    def get_text_content(self) -> str:
        return self.path.read_text(encoding='utf-8', errors='ignore')

    def get_content(self) -> dict[str, Any]:
        with self.path.open("r", encoding='utf-8', errors='ignore') as f:
            return json.load(f)

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        ...

    def save(self):
        with self.path.open("w", encoding='utf-8', errors='ignore') as f:
            json.dump(self.serialize(), f, default=str, indent=4)

    def __fspath__(self) -> str:
        return os.fspath(self.path)

    def __str__(self) -> str:
        return self.__fspath__()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(file_path={self.path.as_posix()!r})'


class BaseCreateableVSCodeFile(BaseVSCodeFile):

    def __init__(self, file_path: Union[str, os.PathLike], create_if_missing: bool = False) -> None:
        super().__init__(file_path)
        self.create_if_missing = create_if_missing

    @classmethod
    def create_from_folder(cls, vscode_folder: "VSCodeFolder") -> "BaseCreateableVSCodeFile":
        file_path = vscode_folder.path.joinpath(cls._file_stem + cls._file_suffix)
        return cls(file_path=file_path, create_if_missing=vscode_folder.create_missing_files)

    @abstractmethod
    def create_default_file(self) -> None:
        ...

    def handle_not_existing(self):
        if self.exists() is True:
            return
        if self.create_if_missing is True:
            self.create_default_file()

    def load_content(self) -> "BaseVSCodeFile":
        self.handle_not_existing()
        if self.exists() is True:
            super().load_content()

        return self


class VSCodeWorkspaceFile(BaseVSCodeFile):
    _file_suffix: str = ".code-workspace"

    def __init__(self, file_path: Union[str, os.PathLike]) -> None:
        super().__init__(file_path)
        self.folders: list[Path] | None = None
        self.others: dict[str, dict[str, Any]] | None = None

    def _load_folders(self, data: list[dict[str, str]]) -> tuple[Path]:
        folders = []
        for item in data:
            try:
                rel_path = item["path"]
                path = self.path.parent.joinpath(rel_path).resolve()
                folders.append(path)
            except KeyError as e:
                continue
        return folders

    def _load_others(self) -> dict[str, dict[str, Any]]:

        return {k: v for k, v in self._raw_content.items() if k.casefold() != "folders"}

    def _load_content(self) -> None:
        super()._load_content()
        self.folders = self._load_folders(self._raw_content["folders"])
        self.others = self._load_others()

    def serialize(self) -> dict[str, Any]:
        _out = {}
        _out["folders"] = [str(p) for p in self.folders]
        for k, v in self.others.items():
            _out[k] = v
        return _out

    @classmethod
    def check_file(cls, in_file: Path) -> bool:
        return in_file.suffix == cls._file_suffix


class VSCodeSettingsFile(BaseCreateableVSCodeFile):

    _file_stem: str = "settings"
    _file_suffix: str = ".json"

    def __init__(self, file_path: Union[str, os.PathLike], create_if_missing: bool = False) -> None:
        super().__init__(file_path, create_if_missing=create_if_missing)
        self.settings: dict[str, Any] | None = None

    def _load_settings(self) -> dict[str, Any]:

        def _set_key_path(in_dict: dict, _keys: list[str], value: Any):
            data = in_dict
            _last_key = _keys.pop(-1)
            for key in _keys:
                data = data.setdefault(key, {})

            data[_last_key] = value

        _out = {}
        for raw_key, value in self._raw_content.items():
            if "." in raw_key:
                _set_key_path(_out, raw_key.split("."), value)

            else:
                _out[raw_key] = value

        return _out

    def create_default_file(self) -> None:
        self.path.write_text("{}", encoding='utf-8', errors='ignore')

    def _load_content(self) -> None:
        super()._load_content()
        self.settings = self._load_settings()

    def serialize(self) -> dict[str, Any]:

        def flatten_dict(dd, separator='.', prefix=''):
            return {prefix + separator + k if prefix else k: v
                    for kk, vv in dd.items()
                    for k, v in flatten_dict(vv, separator, kk).items()
                    } if isinstance(dd, dict) else {prefix: dd}

        return flatten_dict(self.settings)

    @classmethod
    def check_file(cls, in_file: Path) -> bool:
        return in_file.suffix == cls._file_suffix and in_file.stem == cls._file_stem


class _VSCodeVariable:

    def __init__(self, name: str, value: str = None) -> None:
        self._name = name
        self._value = value or name

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value

    @property
    def text(self) -> str:
        return "${" + self.value + "}"

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, value={self.value!r})"


class VSCodeVariables:
    WORKSPACE_FOLDER = _VSCodeVariable("workspaceFolder")


@attrs.define()
class VSCodeTaskOptions:
    cwd: str = attrs.field(default=None)
    env: dict[str, str] = attrs.field(default=Sentinel.MISSING)
    shell: dict[str, Union[str, list[str]]] = attrs.field(default=Sentinel.MISSING)

    @classmethod
    def init_if_not_none(cls, value: Union[Sentinel, dict]) -> Union[Sentinel, "VSCodeTaskOptions"]:
        if value is None or value is Sentinel.MISSING:
            return Sentinel.MISSING

        if isinstance(value, cls):
            return value

        return cls(**value)


@attrs.define()
class VSCodeTaskPresentation:
    reveal: str = attrs.field(default=Sentinel.MISSING)
    echo: bool = attrs.field(default=Sentinel.MISSING)
    focus: bool = attrs.field(default=Sentinel.MISSING)
    panel: str = attrs.field(default=Sentinel.MISSING)
    showReuseMessage: bool = attrs.field(default=Sentinel.MISSING)
    clear: bool = attrs.field(default=Sentinel.MISSING)
    group: str = attrs.field(default=Sentinel.MISSING)

    @classmethod
    def init_if_not_none(cls, value: Union[Sentinel, dict]) -> Union[Sentinel, "VSCodeTaskPresentation"]:
        if value is None or value is Sentinel.MISSING:
            return Sentinel.MISSING
        if isinstance(value, cls):
            return value

        return cls(**value)


@attrs.define()
class VSCodeTaskRunOptions:
    reevaluateOnRerun: bool = attrs.field(default=Sentinel.MISSING)
    runOn: str = attrs.field(default=Sentinel.MISSING)

    @classmethod
    def init_if_not_none(cls, value: Union[Sentinel, dict]) -> Union[Sentinel, "VSCodeTaskRunOptions"]:
        if value is None or value is Sentinel.MISSING:
            return Sentinel.MISSING
        if isinstance(value, cls):
            return value

        return cls(**value)


def _command_value_ensure_string(value: Union[str, dict[str, str]]) -> str:
    if isinstance(value, dict):
        value = value["value"]

    return value


@attrs.define()
class VSCodeTask:
    label: str = attrs.field()
    type: str = attrs.field()
    command: str = attrs.field(converter=_command_value_ensure_string)
    detail: str = attrs.field(default=Sentinel.MISSING)
    isBackground: bool = attrs.field(default=Sentinel.MISSING)
    options: VSCodeTaskOptions = attrs.field(default=Sentinel.MISSING, converter=VSCodeTaskOptions.init_if_not_none)
    args: list[str] = attrs.field(default=Sentinel.MISSING)
    group: Union[str, dict[str, Union[str, bool]]] = attrs.field(default=Sentinel.MISSING)
    presentation: VSCodeTaskPresentation = attrs.field(default=Sentinel.MISSING, converter=VSCodeTaskPresentation.init_if_not_none)
    problemMatcher: dict = attrs.field(default=Sentinel.MISSING)
    runOptions: VSCodeTaskRunOptions = attrs.field(default=Sentinel.MISSING, converter=VSCodeTaskRunOptions.init_if_not_none)
    dependsOn: list[str] = attrs.field(default=Sentinel.MISSING)

    @property
    def marker(self) -> Optional[str]:
        if self.detail is Sentinel.MISSING:
            return None

        marker_regex = re.compile(r"^\<(?P<marker_name>[A-Z_]+)\>")
        match = marker_regex.match(self.detail)
        if not match:
            return None

        return match.group("marker_name")

    @property
    def name(self) -> str:
        return self.label

    @property
    def normalized_name(self) -> str:
        return self.normalize_name(self.name)

    @staticmethod
    def normalize_name(in_name: str) -> str:
        norm_name = in_name.casefold().strip()
        norm_name = norm_name.replace(" ", "_").replace("-", "_")
        return norm_name

    def to_dict(self) -> dict[str, Any]:
        def _missing_filter(attribute: attrs.Attribute, value: Any) -> bool:
            return value is not Sentinel.MISSING

        data = attrs.asdict(self, filter=_missing_filter, recurse=True)
        command_value = data["command"]
        if not isinstance(command_value, dict):

            data["command"] = {"value": command_value, "quoting": "weak"}
        return data


@attrs.define()
class VSCodeTaskInput:
    typus: str = attrs.field()
    name: str = attrs.field()
    default: str = attrs.field(default=Sentinel.MISSING)
    description: str = attrs.field(default="")
    options: list[str] = attrs.field(default=Sentinel.MISSING)

    @property
    def marker(self) -> Optional[str]:
        marker_regex = re.compile(r"^\<(?P<marker_name>[A-Z_]+)\>")
        match = marker_regex.match(self.name)
        if not match:
            return None

        return match.group("marker_name")

    def __getattr__(self, name: str):
        if name == "id":
            return self.name

        if name == "type":
            return self.typus

        raise AttributeError(f"{self!r} has not attribute {name!r}.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VSCodeTaskInput":
        mod_data = {}
        for k, v in data.items():
            if k == "id":
                k = "name"
            elif k == "type":
                k = "typus"
            mod_data[k] = v
        return cls(**mod_data)

    @property
    def as_variable(self) -> str:
        return "${input:" + self.name + "}"

    @property
    def as_arg(self) -> str:
        return f'"{self.as_variable}"'

    def to_dict(self) -> dict[str, Any]:
        def _missing_filter(attribute: attrs.Attribute, value: Any) -> bool:
            return value is not Sentinel.MISSING

        data = attrs.asdict(self, filter=_missing_filter, recurse=True)
        data["id"] = data.pop("name")
        data["type"] = data.pop("typus")
        return data


class VSCodeTasksFile(BaseCreateableVSCodeFile):
    _file_stem: str = "tasks"
    _file_suffix: str = ".json"

    _default_version: str = "2.0.0"

    def __init__(self, file_path: Union[str, os.PathLike], create_if_missing: bool = False) -> None:
        super().__init__(file_path, create_if_missing=create_if_missing)
        self.version: str = None
        self.inputs: list[VSCodeTaskInput] = None
        self.tasks: list[VSCodeTask] = None

    def _load_tasks(self, data: list[dict[str, Any]]) -> list[VSCodeTask]:
        _out = []
        for task_data in data:
            _out.append(VSCodeTask(**task_data))
        return _out

    def _load_inputs(self, data: list[dict[str, Any]]) -> list[VSCodeTaskInput]:
        _out = []
        for item in data:
            _out.append(VSCodeTaskInput.from_dict(item))
        return _out

    def create_default_file(self) -> None:
        data = {"version": self._default_version, "tasks": []}
        with self.path.open("w", encoding='utf-8', errors='ignore') as f:
            json.dump(data, f, indent=4, sort_keys=False, default=str)

    def _load_content(self) -> None:
        super()._load_content()
        self.version = self._raw_content["version"]
        self.inputs = self._load_inputs(self._raw_content.get("inputs", []))
        self.tasks = self._load_tasks(self._raw_content.get("tasks", []))

    def remove_task_by_name(self, name: str):
        normalized_name = VSCodeTask.normalize_name(name)
        task_map = {t.normalized_name: t for t in self.tasks}
        existing_task = task_map.get(normalized_name)
        if existing_task is not None:
            self.tasks.remove(existing_task)

    def remove_input_by_name(self, name: str):
        inputs_map = {i.name: i for i in self.inputs}
        existing_input = inputs_map.get(name, None)
        if existing_input is not None:
            self.inputs.remove(existing_input)

    def update_input(self, in_input: VSCodeTaskInput) -> VSCodeTaskInput:
        inputs_map = {i.name: i for i in self.inputs}
        existing_input = inputs_map.get(in_input.name, None)
        if existing_input is None:
            return in_input
        for attr_name in ["typus", "name", "default", "description"]:
            value = getattr(in_input, attr_name, Sentinel.MISSING)
            if value is Sentinel.MISSING:
                continue
            setattr(existing_input, attr_name, value)

        if in_input.options is not Sentinel.MISSING:
            existing_options = existing_input.options if existing_input.options is not Sentinel.MISSING else []
            for o in in_input.options:
                if o not in existing_options:
                    existing_options.append(o)
            existing_input.options = existing_options
        return existing_input

    def remove_input_by_marker(self, marker: str):
        input_items_to_remove = [i for i in self.inputs if i.marker is not None and i.marker == marker]
        for input_item in input_items_to_remove:
            self.inputs.remove(input_item)

    def add_inputs(self, *in_inputs: VSCodeTaskInput):
        if self.exists() is False:
            return
        all_marker_names = {i.marker for i in in_inputs}
        for input_marker in all_marker_names:
            self.remove_input_by_marker(input_marker)

        for in_input in in_inputs:
            if in_input not in self.inputs:
                self.inputs.append(in_input)

    def remove_tasks_by_marker(self, marker: str):
        tasks_to_remove = [t for t in self.tasks if t.marker is not None and t.marker == marker]
        for task in tasks_to_remove:
            self.tasks.remove(task)

    def add_tasks(self, *tasks: VSCodeTask):
        if self.exists() is False:
            return
        all_marker_names = {t.marker for t in tasks}
        for marker in all_marker_names:
            self.remove_tasks_by_marker(marker)

        self.tasks += list(tasks)

    def serialize(self) -> dict[str, Any]:
        _out = {}
        _out["version"] = self.version
        _out["tasks"] = [t.to_dict() for t in self.tasks]
        _out["inputs"] = [i.to_dict() for i in self.inputs]
        return _out

    @classmethod
    def check_file(cls, in_file: Path) -> bool:
        return in_file.suffix == cls._file_suffix and in_file.stem == cls._file_stem


class VSCodeFolder:
    _find_folder_name: str = ".vscode"
    _file_classes: FILE_CLASSES_TYPE = {"settings": VSCodeSettingsFile,
                                        "workspace": VSCodeWorkspaceFile,
                                        "tasks": VSCodeTasksFile}

    def __init__(self, folder_path: Union[str, os.PathLike], create_missing_files: bool = False) -> None:
        self._path = Path(folder_path).resolve()
        self._create_missing_files = create_missing_files
        self._workspace_file: VSCodeWorkspaceFile = self._find_workspace_file().load_content()
        self._settings_file: VSCodeSettingsFile = self._file_classes["settings"].create_from_folder(self).load_content()
        self._tasks_file: VSCodeTasksFile = self._file_classes["tasks"].create_from_folder(self).load_content()
        # self._launch_file =
        # self._snippets_file =

    def _find_workspace_file(self) -> "VSCodeWorkspaceFile":
        workspace_file_class = self._file_classes["workspace"]
        x = self._file_classes["settings"]

        for file in self.path.iterdir():
            if file.is_file() is False:
                continue

            if workspace_file_class.check_file(file) is True:
                return workspace_file_class(file)
        raise FileNotFoundError(f"Unable to locate a Workspace-file in folder {self.path.as_posix()!r}.")

    @property
    def path(self) -> Path:
        return self._path

    @property
    def create_missing_files(self) -> bool:
        return self._create_missing_files

    @property
    def workspace_file(self) -> Optional[VSCodeWorkspaceFile]:
        return self._workspace_file

    @property
    def settings_file(self) -> Optional[VSCodeSettingsFile]:
        return self._settings_file

    @property
    def tasks_file(self) -> Optional[VSCodeTasksFile]:
        return self._tasks_file

    # @property
    # def launch_file(self) -> Optional[str]:
    #     return self._launch_file

    # @property
    # def snippets_file(self) -> Optional[str]:
    #     return self._snippets_file

    def set_workspace_file(self, workspace_file_path: Union[str, os.PathLike]) -> None:
        self._workspace_file = self._file_classes["workspace"](workspace_file_path)

    def set_settings_file(self, settings_file_path: Union[str, os.PathLike]) -> None:
        self._settings_file = self._file_classes["settings"](settings_file_path)

    def set_tasks_file(self, tasks_file_path: Union[str, os.PathLike]) -> None:
        self._tasks_file = self._file_classes["tasks"](tasks_file_path)

    # def set_launch_file(self, launch_file_path: Union[str, os.PathLike]) -> None:
    #     self._launch_file = self._file_classes["launch"](launch_file_path)

    # def set_snippets_file(self, snippets_file_path: Union[str, os.PathLike]) -> None:
    #     self._snippets_file = self._file_classes["snippets"](snippets_file_path)

    @classmethod
    def from_base_folder(cls, base_folder: Path, create_missing_files: bool = False) -> "VSCodeFolder":
        for item in base_folder.iterdir():
            if item.is_file() is True:
                continue
            if item.name == cls._find_folder_name:
                return cls(item, create_missing_files=create_missing_files)

        raise FileNotFoundError(f"Unable to find any folder named {cls._find_folder_name!r} in {base_folder.as_posix()!r}.")

    def __fspath__(self) -> str:
        return os.fspath(self.path)

    def __str__(self) -> str:
        return self.__fspath__()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(folder_path={self.path.as_posix()!r}, create_missing_files={self.create_missing_files!r})'


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
