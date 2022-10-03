"""
GidTasks
"""


__version__ = "0.0.2"
from pathlib import Path
import logging
from gid_tasks.project_info import set_project, add_tasks_to_vscode
from gid_tasks._custom_invoke_classes.custom_task_objects import task

logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
