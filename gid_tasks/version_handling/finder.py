"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import TYPE_CHECKING

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import ast
import token
import tokenize
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa
from pyparsing import common as ppc

# * Gid Imports ----------------------------------------------------------------------------------------->
from gid_tasks.errors import VersionNotFoundError
from gid_tasks.utility.enums import PipManager
from gid_tasks.version_handling.version_item import Version, FlitVersion

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gid_tasks.project_info.project import MainModule

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

# Version pyparsing Grammar


class VersionGrammar:
    _extra_regex_patterns: tuple[str] = (r"post\d*",
                                         r"build\d*",
                                         r"rc\d*")

    _extra_literal_values: tuple[str] = ("alpha",
                                         "beta",
                                         "final")

    version_class = Version

    def __init__(self) -> None:
        self.base_grammar = self._create_base_grammar()

    def _create_base_grammar(self) -> ppa.ParseExpression:
        def _action(in_tokens):
            return self.version_class(major=in_tokens["major"],
                                      minor=in_tokens["minor"],
                                      patch=in_tokens["patch"],
                                      extra=in_tokens.get("extra"))
        number_value = ppc.integer
        period = ppa.Suppress(".")
        extra_value = ppa.Or([number_value] + [ppa.Literal(t) for t in self._extra_literal_values] + [ppa.Regex(p, flags=re.IGNORECASE) for p in self._extra_regex_patterns])

        base_version_grammar = number_value("major") + period + number_value("minor") + period + number_value("patch") + ppa.Opt(period + extra_value("extra"))

        return base_version_grammar.set_parse_action(_action)

    @property
    def full_grammar(self) -> ppa.ParseExpression:
        return self.base_grammar

    def parse_version_string(self, version_string: str) -> Version:
        return self.base_grammar.parse_string(version_string, parse_all=True)[0]

    def search_version_string(self, in_text: str) -> Version:
        return NotImplemented


class FlitVersionGrammar(VersionGrammar):
    version_class = FlitVersion

    def __init__(self) -> None:
        super().__init__()
        self._full_grammar = self._get_full_grammar()

    def _get_full_grammar(self) -> ppa.ParseExpression:
        equals_sign = ppa.Suppress("=")
        quotes = ppa.Suppress("'") | ppa.Suppress('"')
        variable_name = ppa.Keyword("__version__")

        full_grammar = variable_name.suppress() + equals_sign + quotes + self.base_grammar + quotes

        return full_grammar

    @property
    def full_grammar(self) -> ppa.ParseExpression:
        return self._full_grammar

    def search_version_string(self, in_text: str) -> Version:
        def _action(s: str, loc: int, toks):
            lines = s[:loc].splitlines()
            line_number = len(lines)
            version_item = toks[0].set_meta_data("line_number", line_number)
            return version_item
        try:
            _out = self.full_grammar.set_parse_action(_action).search_string(in_text, max_matches=1)[0][0]

            return _out
        except IndexError as error:
            raise VersionNotFoundError() from error


# -------------
VERSION_EXTRA_PARTS = r'|'.join([r"(post/d*)", r"(build/d*)", r"(alpha)"])

VERSION_PARTS_REGEX_PATTERN = rf"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\.?(?P<extra>{VERSION_EXTRA_PARTS})?"


VERSION_REGEXES = {PipManager.FLIT: re.compile(r"^\_\_version\_\_\s?\=\s?" + "[\'\"]" + VERSION_PARTS_REGEX_PATTERN + "[\'\"]", re.MULTILINE)}


VERSION_GRAMMARS: dict[PipManager, VersionGrammar] = {PipManager.FLIT: FlitVersionGrammar()}


class VersionFinder:

    def __init__(self, pip_manager: "PipManager", main_module: "MainModule") -> None:
        self.pip_manager = pip_manager
        self.grammar = VERSION_GRAMMARS[self.pip_manager]
        self.main_module = main_module
        self.version: Version = None

    def _search_file(self, in_file: Path) -> bool:
        with in_file.open('r', encoding='utf-8', errors='ignore') as f:
            try:
                self.version = self.grammar.search_version_string(f.read())
                self.version = self.version.set_meta_data("file", in_file)
                return True
            except VersionNotFoundError:
                return False

    def find_version(self, force: bool = False) -> "Version":
        if self.version is not None and force is False:
            return self.version
        for file in self.main_module.get_all_python_files():
            if self._search_file(file) is True:
                return self.version
        raise VersionNotFoundError(f"Unable to find a file with the specific Version indicator for {self.pip_manager.name!r}.")


class FlitAstVersionFinder:

    def __init__(self, main_module: "MainModule") -> None:
        self.main_module = main_module
        self.version: Version = None

    @staticmethod
    def _find_version_in_file(in_file: Path):
        tree = ast.parse(in_file.read_bytes(), in_file.name)
        for node in tree.body:
            try:
                if isinstance(node, ast.Assign) and node.targets[0].id == "__version__":
                    version_text = node.value.value
                    line_number = node.lineno
                    return version_text, line_number
            except (AttributeError, IndexError):
                continue
        raise VersionNotFoundError()

    def find_version(self, force: bool = False) -> "Version":
        if self.version is not None and force is False:
            return self.version
        for file in self.main_module.get_all_python_files():
            try:
                version_text, line_number = self._find_version_in_file(file)
                self.version = VersionGrammar().parse_version_string(version_text).set_meta_data("file", file).set_meta_data("line_number", line_number + 1)

                return self.version
            except VersionNotFoundError:
                continue


class FlitTokenizeVersionFinder(FlitAstVersionFinder):

    @staticmethod
    def _find_version_in_file(in_file: Path):
        with tokenize.open(in_file) as f:
            all_tokens = tuple(tokenize.generate_tokens(f.readline))
            version_text_index = None
            for idx, found_token in enumerate(all_tokens):
                if found_token.exact_type == token.NAME and found_token.string == "__version__":
                    version_text_index = idx + 2

            if version_text_index is None:
                raise VersionNotFoundError()

            version_text = all_tokens[version_text_index].string.strip("'\"").strip()
            line_number = all_tokens[version_text_index].start[0]
            return version_text, line_number
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
