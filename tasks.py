from gid_tasks import set_project, add_tasks_to_vscode, task
from pathlib import Path
from invoke import Program, Context
from typing import TYPE_CHECKING
from rich.console import Console as RichConsole
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.containers import Renderables
from rich.tree import Tree
from rich.box import Box
from functools import reduce
from operator import add
from gid_tasks.hackler.imports_cleaner import import_clean_project
from gid_tasks.hackler.dependencies_handling.finder import find_project_dependencies
project = set_project()
CONSOLE = RichConsole(soft_wrap=True)

THIS_FILE_DIR = Path(__file__).parent.absolute()


@task
def clean_imports(c):
    list(import_clean_project(project))


@task
def find_all_dependencies(c):
    find_project_dependencies(project=project, output_file_path=THIS_FILE_DIR.joinpath("temp", "all_dependencies.json"))


add_tasks_to_vscode(project, clean_imports, find_all_dependencies)
