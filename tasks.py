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

project = set_project()
CONSOLE = RichConsole(soft_wrap=True)


@task
def clean_imports(c):
    import_clean_project(c.config.project)


add_tasks_to_vscode(project, clean_imports)
