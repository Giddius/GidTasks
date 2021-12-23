"""
GidTasks
"""


__version__ = "0.0.1"
from pathlib import Path

from gidapptools import get_main_logger

log = get_main_logger("__main__", Path(__file__).resolve())
