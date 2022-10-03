from typing import Union, TYPE_CHECKING
from functools import reduce
from operator import add
from gid_tasks.project_info.project import Project, PipManager, ProjectPaths
from invoke.config import Config as InvokeConfig
import os
if TYPE_CHECKING:
    from gid_tasks._custom_invoke_classes.custom_task_objects import GidTask


def set_project(pip_manager: Union[PipManager, str] = None, cwd: Union[str, os.PathLike] = None, project_paths_class: type[ProjectPaths] = None, create_missing_vscode_files: bool = False) -> Project:
    if pip_manager:
        pip_manager = PipManager(pip_manager)
    project = Project(pip_manager=pip_manager, cwd=cwd, project_paths_class=project_paths_class, create_missing_vscode_files=create_missing_vscode_files)
    InvokeConfig.project = project
    return project


def add_tasks_to_vscode(_project: "Project", *task_objs: "GidTask"):

    if _project.vscode_folder is None:
        return

    _project.vscode_folder.tasks_file.add_tasks(*[t.to_vscode_task_object() for t in task_objs])
    all_input_objects = reduce(add, [t.get_args_for_vscode(only_input_args=True) for t in task_objs])
    _project.vscode_folder.tasks_file.add_inputs(*all_input_objects)

    _project.vscode_folder.tasks_file.save()
