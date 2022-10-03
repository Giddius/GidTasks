import sys
import subprocess
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from gid_tasks.utility.misc import change_cwd
from gid_tasks.project_info.project import Project
import zipfile

THIS_FILE_DIR = Path(__file__).parent.resolve()


FAKE_PACKAGE_ZIP = THIS_FILE_DIR.joinpath("faked_pack.zip")


@pytest.fixture()
def fake_package(tmpdir) -> Path:
    temporary_dir = Path(tmpdir)
    with zipfile.ZipFile(FAKE_PACKAGE_ZIP, 'r') as zip_ref:
        zip_ref.extractall(temporary_dir)

    temp_fake_package_dir = temporary_dir.joinpath("faked_pack")

    yield temp_fake_package_dir
