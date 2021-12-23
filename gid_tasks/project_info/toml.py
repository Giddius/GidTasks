"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import Any, Union, Mapping, Iterable, Optional, Generator
from pathlib import Path
from functools import cached_property
from threading import Lock

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL
from tomlkit.api import loads as toml_loads
from watchdog.events import FileModifiedEvent
from tomlkit.toml_document import TOMLDocument

# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.errors import NotUniqueNestedKey, WrongFileTypeError
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.hashing import file_hash

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
PATH_TYPE = Union[str, os.PathLike, Path]
# endregion[Constants]


def convert_keypath(in_key_path: Union[str, Iterable[str]]) -> list[str]:
    if isinstance(in_key_path, str):
        in_key_path = (sub_path for sub_path in in_key_path.split('.'))

    return list(in_key_path)


# _observer = Observer()


# _all_toml_instances: WeakSet["GidTomlFile"] = WeakSet()


# class TomlChangeHandler(FileSystemEventHandler):

#     def dispatch(self, event):
#         if event.event_type == EVENT_TYPE_MODIFIED:
#             for instance in _all_toml_instances:
#                 try:
#                     instance.on_modified(event=event)
#                 except AttributeError:
#                     continue


# _event_handler = TomlChangeHandler()

# _observer.start()


# def _close_observer():
#     _observer.stop()
#     _observer.join()


# atexit.register(_close_observer)


class GidTomlFile:
    _write_locks: dict[Path, Lock] = {}

    def __init__(self, path: PATH_TYPE) -> None:
        self.path = self._validate_path(path)
        self.document: TOMLDocument = None
        self.current_hash: str = None
        self.read()

    def on_modified(self, event: FileModifiedEvent) -> None:
        if Path(event.src_path) == self.path:
            self.read()

    @staticmethod
    def _validate_path(path: PATH_TYPE) -> Path:
        path = Path(path)
        if path.exists() is False:
            raise FileNotFoundError(f"The file {path.as_posix!r} does not exist.")
        if path.is_file() is False:
            raise FileNotFoundError(f"The path {path.as_posix()!r} is not a file.")
        if path.suffix.casefold() != '.toml':
            raise WrongFileTypeError(f"The file {path.as_posix()!r} is not a toml file.")
        return path

    @property
    def write_lock(self) -> Lock:
        try:
            return self._write_locks[self.path]
        except KeyError:
            lock = Lock()
            self._write_locks[self.path] = lock
            return lock

    @property
    def all_keys(self) -> tuple[str]:
        self._check_changed()

        def _get_keys(in_dict: dict, level: int = 0) -> Generator[str, None, None]:
            for k, v in in_dict.items():
                yield k, level
                if isinstance(v, Mapping):
                    yield from _get_keys(v, level=level + 1)
        return tuple(sorted(_get_keys(self.document), key=lambda x: x[1]))

    def _check_changed(self) -> None:
        if file_hash(self.path) != self.current_hash:
            self.read()

    def read(self) -> "GidTomlFile":
        with self.write_lock:
            with self.path.open('r', encoding='utf-8', errors='ignore') as f:
                self.document = toml_loads(f.read())
        self.current_hash = file_hash(self.path)
        return self

    def write(self) -> "GidTomlFile":
        with self.write_lock:
            with self.path.open('w', encoding='utf-8', errors='ignore') as f:
                f.write(self.document.as_string())
        return self

    def get(self, key, default=None) -> Any:
        self._check_changed()
        return self.document.get(key, default)

    def get_from_key_path(self, key_path: Union[str, Iterable[str]], default=MiscEnum.NOTHING) -> Any:
        self._check_changed()
        key_path = convert_keypath(key_path).copy()
        last_key = key_path.pop(-1)
        data = self.document
        for key in key_path:
            try:
                data = data[key]
            except KeyError as e:
                if default is MiscEnum.NOTHING:
                    raise KeyError(f"The {key_path.index(key)+1}. key {key!r} was not found in the dict.") from e
                return default
        try:
            return data[last_key]
        except KeyError:
            if default is MiscEnum.NOTHING:
                raise
            return default

    def get_from_nested_key(self, nested_key: str, default=None) -> Any:
        self._check_changed()
        if nested_key not in {key for key, level in self.all_keys}:
            return default
        if len([key for key, level in self.all_keys if key == nested_key]) > 1:
            raise NotUniqueNestedKey(nested_key=nested_key)

        def _get_data(in_key: str, in_dict: dict) -> Any:
            for k, v in in_dict.items():
                if k == in_key:
                    return v
                if isinstance(v, Mapping):
                    try:
                        return _get_data(in_key=in_key, in_dict=v)
                    except KeyError:
                        continue
            raise KeyError(nested_key)

        return _get_data(nested_key, self.document)

    def set_by_key_path(self, key_path: Union[str, Iterable[str]], value: Any, create_intermediates: bool = True) -> None:
        key_path = convert_keypath(key_path).copy()
        data = self.document
        for sub_path in key_path[:-1]:
            try:
                data = data[sub_path]
            except KeyError:
                if create_intermediates is True:
                    data.add(sub_path, {})
                    data = data[sub_path]
                else:
                    raise

        data[key_path[-1]] = value
        self.write().read()

    def __set_item__(self, key, value):
        self.document.__setitem__(key, value)
        self.write().read()

    def __getitem__(self, key):
        self._check_changed()
        return self.document.__getitem__(key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path.as_posix()!r})"


class PyProjectTomlFile(GidTomlFile):

    @cached_property
    def package_name(self) -> str:
        return str(self.get_from_key_path(["project", "name"]))

    @cached_property
    def source_url(self) -> Optional[URL]:
        raw_url = self.get_from_key_path(["project", "urls", "Source"], default=None)
        if raw_url is None:
            return raw_url
        return URL(raw_url)

    @cached_property
    def authors(self) -> Optional[frozenset[str]]:
        raw_authors = self.get_from_key_path(["project", "authors"], default=None)
        if raw_authors is not None:
            return frozenset(str(author.get("name")) for author in raw_authors)

    def get_autoflake_settings(self, default=MiscEnum.NOTHING) -> dict[str, Any]:
        default = {} if default is MiscEnum.NOTHING else default
        return self.get_from_key_path(["tool", "autoflake"], default=default)

    def get_autopep8_settings(self, default=MiscEnum.NOTHING) -> dict[str, Any]:
        default = {} if default is MiscEnum.NOTHING else default
        return self.get_from_key_path(["tool", "autopep8"], default=default)

    def _complete_isort_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        settings["known_first_party"] = list(set(settings.get("known_first_party", []) + [self.package_name]))
        settings["known_qt"] = list(set(settings.get("known_qt", []) + ["PyQt5", "PyQt6", "PySide6", "pyqtgraph"]))
        settings["known_gid"] = list(set(settings.get("known_gid", []) + ["gid*"]))
        return settings

    def get_isort_settings(self, default=MiscEnum.NOTHING) -> dict[str, Any]:
        default = {} if default is MiscEnum.NOTHING else default
        settings = self.get_from_key_path(["tool", "isort"], default=default)
        return self._complete_isort_settings(settings=settings)

    def get_gid_task_settings(self, default=MiscEnum.NOTHING) -> dict[str, Any]:
        default = {} if default is MiscEnum.NOTHING else default
        return self.get_from_key_path(["tool", "gid_tasks"], default=default)

    def get_project_data(self) -> dict[str, Any]:
        return self.get("project", default={})

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
