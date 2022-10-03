import pytest
from pathlib import Path
from gid_tasks.project_info.project import Project, PipManager
from gid_tasks.project_info.toml import PyProjectTomlFile, GidTomlFile


def test_fake_project_toml(fake_toml_file: Path):
    fake_toml = PyProjectTomlFile(fake_toml_file)
    assert fake_toml.package_name == "faked_pack_src"
    assert fake_toml.authors == frozenset(["fake_author"])
