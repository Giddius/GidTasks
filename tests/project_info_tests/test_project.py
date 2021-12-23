import pytest
from pathlib import Path
from gid_tasks.project_info.project import Project, PipManager
from gid_tasks.utility.misc import main_dir_from_git, find_main_dir_by_pyproject_location


def test_project(fake_project: Project):
    assert fake_project.pip_manager is PipManager.FLIT
    assert str(fake_project.version) == "1.2.3"
    assert fake_project._get_pyproject_file() == fake_project.base_folder.joinpath("pyproject.toml")
    assert {i.relative_to(fake_project.base_folder) for i in fake_project.main_module.get_all_python_files()} == {Path("faked_pack_src", "plugin.py"), Path("faked_pack_src", "__init__.py"), Path("faked_pack_src", "__main__.py")}
