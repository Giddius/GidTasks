from typing import Optional, Union
import pytest
from pytest import param
from gid_tasks.version_handling.finder import VersionGrammar, FlitVersionGrammar, FlitAstVersionFinder, FlitTokenizeVersionFinder
from gid_tasks.errors import VersionNotFoundError
from pathlib import Path
from gid_tasks.project_info.project import Project

base_version_grammar_params = [param("0.0.1", {"major": 0, "minor": 0, "patch": 1, "extra": None}, id="simple no extra"),
                               param("23.14.0", {"major": 23, "minor": 14, "patch": 0, "extra": None}, id="simple no extra 2"),
                               param("0.0.1.12", {"major": 0, "minor": 0, "patch": 1, "extra": 12}, id="simple integer extra"),
                               param("0.0.1.alpha", {"major": 0, "minor": 0, "patch": 1, "extra": "alpha"}, id="simple string extra alpha"),
                               param("12.0.0.build2", {"major": 12, "minor": 0, "patch": 0, "extra": "build2"}, id="simple string extra build")]


@pytest.mark.parametrize(["in_version_string", "result"], base_version_grammar_params)
def test_base_version_grammar(in_version_string: str, result: dict[str, Union[int, str]]):
    grammar = VersionGrammar()
    version_item = grammar.full_grammar.parse_string(in_version_string, parse_all=True)[0]

    for k, v in result.items():
        assert getattr(version_item, k) == v


flit_version_full_grammar_params = [param('__version__ = "0.0.1"', {"major": 0, "minor": 0, "patch": 1, "extra": None}, id="simple no extra"),
                                    param("__version__= '23.14.0'", {"major": 23, "minor": 14, "patch": 0, "extra": None}, id="simple no extra 2"),
                                    param('__version__ = "0.0.1.alpha"', {"major": 0, "minor": 0, "patch": 1, "extra": "alpha"}, id="simple string extra alpha")]


@pytest.mark.parametrize(["in_version_string", "result"], flit_version_full_grammar_params)
def test_flit_version_full_grammar(in_version_string: str, result: dict[str, Union[int, str]]):
    grammar = FlitVersionGrammar()

    version_item = grammar.full_grammar.parse_string(in_version_string, parse_all=True)[0]

    for k, v in result.items():
        assert getattr(version_item, k) == v


full_version_text_1 = '''"""
GidTasks
"""


__version__ = "0.0.1"
from pathlib import Path
import logging


logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
'''


full_version_text_2 = '''"""Antistasi Logbook"""

__version__ = '0.4.5'

import os


from rich.console import Console as RichConsole
from rich.table import Table
from rich.panel import Panel
from rich.containers import Renderables
from rich.align import Align
from rich.box import DOUBLE_EDGE
from rich.traceback import install as rich_traceback_install

from pathlib import Path
from gidapptools import setup_main_logger_with_file_logging, get_meta_paths, get_meta_config
from gidapptools.meta_data import setup_meta_data


import sys

'''


full_version_text_3_no_version = '''"""
GidTasks
"""



from pathlib import Path
import logging


logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
'''


flit_search_version_params = [param(full_version_text_1, 5, {"major": 0, "minor": 0, "patch": 1, "extra": None}, None, id="1"),
                              param(full_version_text_2, 2, {"major": 0, "minor": 4, "patch": 5, "extra": None}, None, id="2"),
                              param(full_version_text_3_no_version, 0, {"major": None, "minor": None, "patch": None, "extra": None}, VersionNotFoundError, id="no version")]


@pytest.mark.parametrize(["in_text", "line_number", "result", "error"], flit_search_version_params)
def test_flit_search_version(in_text: str, line_number: int, result: dict[str, Union[int, str]], error: Exception):
    grammar = FlitVersionGrammar()
    if error is not None:
        with pytest.raises(error):
            version_item = grammar.search_version_string(in_text)
    else:
        version_item = grammar.search_version_string(in_text)
        assert version_item.meta_data["line_number"] == line_number

        for k, v in result.items():
            assert getattr(version_item, k) == v


def test_flit_ast_version_finder(fake_package: Path):
    project = Project(cwd=fake_package)
    finder = FlitAstVersionFinder(project.main_module)
    version = finder.find_version()
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.meta_data["line_number"] == 6


def test_flit_tokenize_version_finder(fake_package: Path):
    project = Project(cwd=fake_package)
    finder = FlitTokenizeVersionFinder(project.main_module)
    version = finder.find_version()
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.meta_data["line_number"] == 6
