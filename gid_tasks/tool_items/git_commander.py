"""
WiP.

Soon.
"""

# region [Imports]

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

    @property
    @abstractmethod
    def args(self):
        ...

    def handle_error(self, result: subprocess.CompletedProcess):
        result.check_returncode()


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

    def run_command(self, command: AbstractCommand):
        result = subprocess.run(args=command.args, shell=command.shell, check=command.check, cwd=self.cwd, text=True)
        if result.returncode != 0:
            command.handle_error(result)

# region[Main_Exec]


if __name__ == '__main__':
    x = GitCommander(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidTasks").resolve())
    x.run_command(AddCommand())
    x.run_command(CommitCommand("something2"))
    x.run_command(PushCommand())

# endregion[Main_Exec]
