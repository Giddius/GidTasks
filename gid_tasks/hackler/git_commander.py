"""
WiP.

Soon.
"""

# region [Imports]

# * Typing Imports --------------------------------------------------------------------------------------->
from typing import Any, Optional

# * Standard Library Imports ---------------------------------------------------------------------------->
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractCommand(ABC):
    shell: bool = False
    check: bool = False
    text: bool = True
    start_new_session: bool = False
    creationflags = None
    capture_output: bool = True

    asynchronous: bool = False
    disown: bool = False
    dry: bool = False
    echo: bool = False
    hide: bool = False
    in_stream = None
    out_stream = None
    inv_shell: Optional[str] = None

    timeout: Optional[int] = None

    @property
    @abstractmethod
    def args(self) -> str:
        ...

    def handle_error(self, result: subprocess.CompletedProcess):
        result.check_returncode()

    @property
    def subprocess_kwargs(self) -> dict[str, Any]:
        _out = {"shell": self.shell,
                "check": self.check,
                "text": self.text,
                "start_new_session": self.start_new_session,
                "timeout": self.timeout,
                "creationflags": self.creationflags,
                "capture_output": self.capture_output}
        return {k: v for k, v in _out.items() if v is not None}

    @property
    def invoke_kwargs(self) -> dict[str, Any]:
        _out = {'asynchronous': self.asynchronous,
                'disown': self.disown,
                'dry': self.dry,
                'echo': self.echo,
                'hide': self.hide,
                'in_stream': self.in_stream,
                'inv_shell': self.shell,
                'out_stream': self.out_stream,
                'timeout': self.timeout}
        return {k: v for k, v in _out.items() if v is not None}


class AddCommand(AbstractCommand):

    @property
    def args(self):
        return "git add ."


class CommitCommand(AbstractCommand):

    def __init__(self, message: str) -> None:
        self.message = message

    @property
    def args(self):
        return f'git commit -am "{self.message}"'


class PushCommand(AbstractCommand):

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    @property
    def args(self):
        args = "git push"
        if self.dry_run is True:
            args += ' --dry-run'
        return args


class GitCommander:

    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd


# region[Main_Exec]

if __name__ == '__main__':
    pass
# endregion[Main_Exec]
