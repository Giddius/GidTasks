import sys
import subprocess
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from gidapptools.general_helper.path_helper import change_cwd
from gid_tasks.project_info.project import Project
from gid_tasks.utility.misc import main_dir_from_git, find_main_dir_by_pyproject_location


@pytest.fixture()
def fake_project(fake_package: Path) -> Project:
    yield Project(cwd=fake_package)


@pytest.fixture()
def fake_toml_file(fake_package: Path):
    yield fake_package.joinpath('pyproject.toml')
