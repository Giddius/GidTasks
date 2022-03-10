"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict, UserDict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader

from rich.abc import RichRenderable
from rich.align import Align, VerticalCenter
from rich.ansi import AnsiDecoder
from rich.bar import Bar
from rich.box import (ASCII, ASCII2, ASCII_DOUBLE_HEAD, DOUBLE, DOUBLE_EDGE, HEAVY, HEAVY_EDGE, HEAVY_HEAD, HORIZONTALS, MINIMAL, MINIMAL_DOUBLE_HEAD, MINIMAL_HEAVY_HEAD, ROUNDED, SIMPLE, SIMPLE_HEAD,
                      SIMPLE_HEAVY, SQUARE, SQUARE_DOUBLE_HEAD, Box)
from rich.cells import cell_len, chop_cells, get_character_cell_size, set_cell_size
from rich.color import Color, ColorParseError, ColorSystem, ColorType, blend_rgb, parse_rgb_hex
from rich.color_triplet import ColorTriplet
from rich.columns import Columns
from rich.console import (NO_CHANGE, Capture, CaptureError, Console as RichConsole, ConsoleDimensions, ConsoleOptions, ConsoleRenderable, ConsoleThreadLocals, Group, NewLine, NoChange, PagerContext, RenderHook,
                          RichCast, ScreenContext, ScreenUpdate, ThemeContext, detect_legacy_windows, get_windows_console_features, group)
from rich.constrain import Constrain
from rich.containers import Lines, Renderables, T
from rich.control import Control, strip_control_codes
from rich.emoji import Emoji, NoEmoji
from rich.errors import ConsoleError, LiveError, MarkupError, MissingStyle, NoAltScreen, NotRenderableError, StyleError, StyleStackError, StyleSyntaxError
from rich.file_proxy import FileProxy
from rich.filesize import decimal, pick_unit_and_suffix
from rich.highlighter import Highlighter, JSONHighlighter, NullHighlighter, RegexHighlighter, ReprHighlighter
from rich.json import JSON
from rich.jupyter import JupyterMixin, JupyterRenderable, display, print
from rich.layout import ColumnSplitter, Layout, LayoutError, LayoutRender, NoSplitter, RowSplitter, Splitter
from rich.live import Live
from rich.live_render import LiveRender
from rich.logging import RichHandler
from rich.markdown import BlockQuote, CodeBlock, Heading, HorizontalRule, ImageItem, ListElement, ListItem, Markdown, MarkdownContext, MarkdownElement, Paragraph, TextElement, UnknownElement
from rich.markup import Tag, escape, render
from rich.measure import Measurement, measure_renderables
from rich.padding import Padding
from rich.pager import Pager, SystemPager
from rich.palette import Palette
from rich.panel import Panel
from rich.pretty import Node, Pretty, install, is_expandable, pprint, pretty_repr, traverse
from rich.progress import (BarColumn, DownloadColumn, FileSizeColumn, Progress, ProgressColumn, ProgressSample, ProgressType, RenderableColumn, SpinnerColumn, Task, TaskID, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn, TotalFileSizeColumn, TransferSpeedColumn, track)
from rich.progress_bar import ProgressBar
from rich.prompt import Confirm, DefaultType, FloatPrompt, IntPrompt, InvalidResponse, Prompt, PromptBase, PromptError, PromptType
from rich.protocol import is_renderable, rich_cast
from rich.region import Region
from rich.repr import ReprError, T, auto, rich_repr
from rich.rule import Rule
from rich.scope import render_scope
from rich.screen import Screen
from rich.segment import ControlType, Segment, SegmentLines, Segments
from rich.spinner import Spinner
from rich.status import Status
from rich.style import NULL_STYLE, Style, StyleStack
from rich.styled import Styled
from rich.syntax import ANSISyntaxTheme, PygmentsSyntaxTheme, Syntax, SyntaxTheme
from rich.table import Column, Row, Table
from rich.tabulate import tabulate_mapping
from rich.terminal_theme import DEFAULT_TERMINAL_THEME, TerminalTheme
from rich.text import Span, Text
from rich.theme import Theme, ThemeStack, ThemeStackError
from rich.traceback import Frame, PathHighlighter, Stack, Trace, Traceback, install
from rich.tree import Tree

if TYPE_CHECKING:
    from rich.text import TextType
    from rich.align import AlignMethod
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class DefaultRuleSettings:

    def __init__(self, characters: str, style: Union[str, Style], align: "AlignMethod") -> None:
        self.characters = characters
        self.style = style
        self.align = align

    @classmethod
    def from_kwargs(cls, kwargs: dict[str, Any]) -> "DefaultRuleSettings":
        characters = kwargs.pop("default_rule_characters", "-")
        style = kwargs.pop("default_rule_style", "rule.line")
        align = kwargs.pop("default_rule_align", "center")
        return cls(characters=characters, style=style, align=align)

    def as_dict(self) -> dict[str, Any]:
        return {"characters": self.characters,
                "style": self.style,
                "align": self.align}


class GidTaskConsole(RichConsole):

    def __init__(self, **kwargs) -> None:
        self.default_rule_settings = DefaultRuleSettings.from_kwargs(kwargs)
        super().__init__(**kwargs)

    def rule(self, title: "TextType" = None, *, characters: str = None, style: Union[str, Style] = None, align: "AlignMethod" = None) -> None:
        title = title or ""
        style = style or "rule.line"
        align = align or "center"
        characters = characters or self.default_rule_char
        return super().rule(title=title, characters=characters, style=style, align=align)

    def big_rule(self, title: "TextType" = None, *, characters: str = None, style: Union[str, Style] = None, align: "AlignMethod" = None) -> None:
        characters = characters or self.default_rule_char
        style = style or "rule.line"
        align = align or "center"
        title = title or ""
        top_bottom = Rule(title="", characters=characters, style=style, align=align)
        middle = Rule(title=title, characters=characters, style=style, align=align)
        self.print(Group(top_bottom, middle, top_bottom))

    def end_message(self):
        ...

    def start_message(self):
        ...


def make_console():
    kwargs = {"soft_wrap": True}
    return GidTaskConsole(**kwargs)


# region[Main_Exec]
if __name__ == '__main__':
    c = GidTaskConsole()
    c.big_rule("[red]tt")

# endregion[Main_Exec]
