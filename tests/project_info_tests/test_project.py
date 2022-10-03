import pytest
from pathlib import Path
from gid_tasks.project_info.project import Project, PipManager
from gid_tasks.utility.misc import main_dir_from_git, find_main_dir_by_pyproject_location
from gid_tasks.project_info.vscode_objects import VSCodeFolder


def test_project(fake_project: Project):
    assert fake_project.pip_manager is PipManager.FLIT
    assert str(fake_project.version) == "1.2.3"
    fake_project.set_version(fake_project.version.increment_minor())
    assert str(fake_project.version) == "1.3.0"
    assert '__version__ = "1.3.0"' in fake_project.version.meta_data.get("file").read_text(encoding='utf-8', errors='ignore')
    assert '__version__ = "1.2.3"' not in fake_project.version.meta_data.get("file").read_text(encoding='utf-8', errors='ignore')
    assert fake_project._get_pyproject_file() == fake_project.base_folder.joinpath("pyproject.toml")
    assert fake_project.general_todo_data_file == fake_project.base_folder.joinpath("docs", "docs_data", "general_todo_data.json")
    assert fake_project.todo_text_file == fake_project.base_folder.joinpath("TODO.md")

    assert isinstance(fake_project.vscode_folder, VSCodeFolder) is True
    for attribute_name in ["settings_file", "tasks_file"]:
        assert getattr(fake_project.vscode_folder, attribute_name).exists() is False
    assert fake_project.vscode_folder.workspace_file.exists() is True
