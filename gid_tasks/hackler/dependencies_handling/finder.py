"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Any, Optional

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import ast
import sys
import json
from pprint import pprint
from pathlib import Path
from functools import cached_property
from importlib import metadata
from collections import UserList

# * Third Party Imports --------------------------------------------------------------------------------->
import attr
from yarl import URL

# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.project_info.project import Project
from gid_tasks.version_handling.version_item import Version

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
    version: Version = attr.ib()
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

    def to_file(self, file_path: os.PathLike) -> None:
        with Path(file_path).resolve().open("w", encoding='utf-8', errors='ignore') as f:
            json.dump(self.serialize(), f, default=str, sort_keys=False, indent=4)


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
            version = Version.from_string(_distribution.version)
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


def find_project_dependencies(project: Project, output_file_path: os.PathLike):
    finder = DependencyFinder(main_package_name=project.main_module_name)
    for file in project.main_module.get_all_python_files():
        finder.search_file(file)
    finder.found_dependencies.to_file(output_file_path)
    if finder.errored_names:
        pprint(finder.errored_names)


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
